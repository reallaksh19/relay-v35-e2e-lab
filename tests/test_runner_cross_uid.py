"""RNR-06B2 cross-Unix-principal acceptance oracle (privileged LAB only).

Requires Linux root + POSIX ACL: github-hosted non-root runs SKIP, never a
credential-isolated GitHub acceptance result. Uses no external credentials.
"""
from __future__ import annotations

import base64
import ctypes
import json
import os
import pwd
import subprocess
import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import runner_custody as C
import runner_gateway as G
import runner_pilot as S1


def _acl(path: Path, entries: dict[int, str], owner: str) -> None:
    """Apply a narrowly-scoped filesystem ACL; privileged fixture only."""
    lib = ctypes.CDLL("libacl.so.1", use_errno=True)
    lib.acl_from_text.argtypes = [ctypes.c_char_p]
    lib.acl_from_text.restype = ctypes.c_void_p
    lib.acl_set_file.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p]
    lib.acl_set_file.restype = ctypes.c_int
    lib.acl_free.argtypes = [ctypes.c_void_p]
    lib.acl_free.restype = ctypes.c_int
    mask = "--x" if owner == "rwx" else "rw-"
    acl_text = ("user::" + owner + "\n" + "".join(
        f"user:{uid}:{perm}\n" for uid, perm in sorted(entries.items())) +
        "group::---\nmask::" + mask + "\nother::---\n")
    raw = lib.acl_from_text(acl_text.encode())
    if not raw:
        raise OSError(ctypes.get_errno(), "invalid test ACL")
    try:
        if lib.acl_set_file(os.fsencode(path), 0x8000, raw) != 0:
            raise OSError(ctypes.get_errno(), "cannot set filesystem ACL")
    finally:
        lib.acl_free(raw)


class CrossUnixPrincipalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if sys.platform != "linux" or os.geteuid() != 0 or not hasattr(os, "setgroups"):
            raise unittest.SkipTest("real Unix cross-UID requires privileged Linux lab")
        try:
            cls.a_uid = pwd.getpwnam("oai").pw_uid
            cls.b_uid = pwd.getpwnam("nobody").pw_uid
            ctypes.CDLL("libacl.so.1")
        except (KeyError, OSError):
            raise unittest.SkipTest("two nonprivileged identities and libacl required")
        if cls.a_uid == cls.b_uid or 0 in (cls.a_uid, cls.b_uid):
            raise unittest.SkipTest("distinct, non-root identities required")

    def setUp(self):
        import test_runner_provider
        self.fixture = test_runner_provider.GitBrokerCases(
            "test_real_git_ref_lease_updates_exact_path_and_parent")
        self.fixture.setUp()
        self.root = self.fixture.root
        self.folder = self.root / "protected-socket"
        self.folder.mkdir(mode=0o700)
        self.folder.chmod(0o700)
        self.path = self.folder / "write.sock"
        self.server = G.PrivateLabGateway(
            self.path, self.fixture.writer,
            agent_uids={"Agent-A": self.a_uid, "Agent-B": self.b_uid})
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       kwargs={"poll_interval": .01})
        self.thread.start()
        # ACL entries are applied only AFTER the broker has safely bound its
        # owner-only socket; never permit clients to see DB/SSH/signing key.
        for parent in (self.root, self.folder):
            _acl(parent, {self.a_uid: "--x", self.b_uid: "--x"}, "rwx")
        _acl(self.path, {self.a_uid: "rw-", self.b_uid: "rw-"}, "rw-")

    def tearDown(self):
        self.server.shutdown()
        self.thread.join(timeout=5)
        self.server.server_close()
        self.fixture.tearDown()

    def call_uid(self, uid: int, *, agent: str, epoch: int, token: str,
                 head: str, operation: str) -> dict:
        payload = {
            "socket": str(self.path), "agent": agent, "epoch": epoch,
            "capability": token, "operation_id": operation,
            "head": head,
            "content": base64.b64encode(("from " + agent + "\n").encode()).decode(),
        }
        child = '''
import base64,json,os,sys
os.setgroups([])
os.setgid(int(sys.argv[1]))
os.setuid(int(sys.argv[1]))
from pathlib import Path
import runner_gateway as G
p=json.loads(sys.stdin.readline())
try:
 r=G.send_write_request(Path(p["socket"]),agent=p["agent"],epoch=p["epoch"],
     capability=p["capability"],operation_id=p["operation_id"],
     path="src/inventorylab/parser.py",expected_head=p["head"],
     content=base64.b64decode(p["content"]))
except OSError:
 r={"status":"OS_DENIED"}
print(json.dumps(r,sort_keys=True))
'''
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"),
               "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "scripts")}
        p = subprocess.run([sys.executable, "-c", child, str(uid)],
                           input=json.dumps(payload) + "\n", text=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           timeout=15, env=env)
        self.assertEqual(p.returncode, 0, p.stderr)
        return json.loads(p.stdout)

    def test_real_two_user_fence_then_successor_and_acl_revocation(self):
        f = self.fixture
        self.assertNotEqual(self.a_uid, self.b_uid)
        # Only original holder A can write. B cannot impersonate A with B UID.
        wrong = self.call_uid(self.b_uid, agent="Agent-A", epoch=1,
                              token=f.agent_token, head=f.head0, operation="impersonate")
        self.assertEqual(wrong["status"], "DENIED")
        early = self.call_uid(self.b_uid, agent="Agent-B", epoch=2,
                              token="x" * 64, head=f.head0, operation="early")
        self.assertEqual(early["status"], "DENIED")
        first = self.call_uid(self.a_uid, agent="Agent-A", epoch=1,
                              token=f.agent_token, head=f.head0, operation="write-a")
        self.assertEqual(first["status"], "COMMITTED")
        current = first["new_head"]
        self.assertEqual(f.provider.head(), current)

        # Controller, not client, creates and executes a signed transfer.
        report = {
            "schema": "RUNNER_RECONCILIATION_V1", "responsibility": "LAB-R1",
            "mode": "EMERGENCY", "source_reconciliation": "SOURCE_RECONCILED_READ_ONLY",
            "frozen_plan_digest": "d" * 64, "frozen_bundle_digest": "e" * 64,
            "blockers": [], "writer_authorization": "DENIED",
            "custody_transfer": "NOT_EXECUTED",
            "source": {"candidate_head": current, "base_is_ancestor": True,
                       "branch": "lab/runner-provider-sandbox", "dirty_paths": [],
                       "out_of_scope_changes": []},
            "remote": {"status": "MATCH", "remote_head": current},
        }
        b_token = "b" * 64
        grant = f.db.issue_transfer_grant(
            transfer_id="cross-uid-transfer", responsibility="LAB-R1",
            old_epoch=1, from_agent="Agent-A", to_agent="Agent-B",
            candidate_head=current,
            reconciliation_digest=S1.digest(S1.canonical(report)),
            operator_receipt="LAB_TEST_CONTROLLER_ONLY",
            successor_capability=b_token)
        f.db.begin_fence(grant, report)
        blocked = self.call_uid(self.a_uid, agent="Agent-A", epoch=1,
                                token=f.agent_token, head=current,
                                operation="fenced-old-write")
        self.assertEqual(blocked["status"], "DENIED")
        new = f.db.finish_transfer(grant, b_token, f.provider.head)
        self.assertEqual((new["holder"], new["epoch"]), ("Agent-B", 2))
        # Revoke old executor at OS ACL layer, preserving Agent B reachability.
        _acl(self.path, {self.a_uid: "---", self.b_uid: "rw-"}, "rw-")
        _acl(self.folder, {self.a_uid: "---", self.b_uid: "--x"}, "rwx")
        old = self.call_uid(self.a_uid, agent="Agent-A", epoch=1,
                            token=f.agent_token, head=current,
                            operation="old-after-revoke")
        self.assertEqual(old["status"], "OS_DENIED")
        second = self.call_uid(self.b_uid, agent="Agent-B", epoch=2,
                               token=b_token, head=current, operation="write-b")
        self.assertEqual(second["status"], "COMMITTED")
        self.assertEqual(f.provider.head(), second["new_head"])
        self.assertEqual(f.db.read("LAB-R1")["epoch"], 2)
        # Even if A somehow reacquired a Unix connection, broker epoch fences it.
        self.assertEqual(f.db.read("LAB-R1")["holder"], "Agent-B")
