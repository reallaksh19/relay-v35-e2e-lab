#!/usr/bin/env python3
"""RNR-06B: private Unix-socket façade for the LAB-R1 broker.

No operator lifecycle actions are reachable through this façade. This does not
provision a separate Unix identity or revoke GitHub credentials: those are
external admission requirements, never inferred from socket tests.
"""
from __future__ import annotations

import base64
import binascii
import json
import os
import socket
import socketserver
import stat
import struct
from pathlib import Path
from typing import Any

from runner_custody import CustodyDenied
from runner_provider import BrokeredGitWriter, ProviderUncertain

MAX_LINE = 360_000  # 256k binary payload plus JSON/base64 envelope
REQUEST_FIELDS = frozenset(("schema", "action", "agent", "epoch", "capability",
                            "operation_id", "path", "expected_head", "content_b64"))
RESPONSE_SCHEMA = "RUNNER_LAB_GATEWAY_RESPONSE_V1"


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CustodyDenied("ambiguous duplicate JSON field")
        result[key] = value
    return result


def _parse_request(raw: bytes) -> dict[str, Any]:
    if len(raw) > MAX_LINE or not raw.endswith(b"\n"):
        raise CustodyDenied("invalid bounded request frame")
    try:
        parsed = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_pairs)
    except (ValueError, UnicodeDecodeError) as exc:
        raise CustodyDenied("invalid request JSON") from exc
    if (not isinstance(parsed, dict) or set(parsed) != REQUEST_FIELDS or
            parsed.get("schema") != "RUNNER_LAB_GATEWAY_WRITE_V1" or
            parsed.get("action") != "WRITE" or type(parsed.get("epoch")) is not int):
        raise CustodyDenied("unknown command or authority escalation")
    encoded = parsed["content_b64"]
    if not isinstance(encoded, str) or len(encoded) > 350_000:
        raise CustodyDenied("invalid payload size")
    try:
        decoded = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise CustodyDenied("invalid base64 content") from exc
    if len(decoded) > 256_000:
        raise CustodyDenied("binary content exceeds LAB-R1 limit")
    for key in ("agent", "capability", "operation_id", "path", "expected_head"):
        if not isinstance(parsed[key], str):
            raise CustodyDenied("invalid typed request")
    parsed["content"] = decoded
    del parsed["content_b64"]
    return parsed


def validate_socket_location(socket_path: Path) -> None:
    """No bind outside a private operator-controlled directory; no unlink races."""
    if not isinstance(socket_path, Path) or not socket_path.is_absolute():
        raise CustodyDenied("absolute trusted socket path required")
    directory = socket_path.parent
    st = directory.lstat()
    if (not stat.S_ISDIR(st.st_mode) or st.st_uid != os.getuid() or
            st.st_mode & 0o077 or directory.is_symlink()):
        raise CustodyDenied("gateway requires owner-only non-symlink directory")
    if os.path.lexists(socket_path):
        raise CustodyDenied("gateway socket path already occupied")


def validate_peer_uid(actual: int, expected: int, operator: int,
                      *, allow_same_uid_in_tests: bool = False) -> None:
    if (type(actual) is not int or type(expected) is not int or
            expected < 0 or actual != expected or
            (actual == operator and not allow_same_uid_in_tests)):
        raise CustodyDenied("client process is not the designated agent Unix identity")


class _Handler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        self.request.settimeout(5)
        try:
            server = self.server
            if not hasattr(socket, 'SO_PEERCRED'):
                raise CustodyDenied("OS cannot attest client identity")
            peer = self.request.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED,
                                           struct.calcsize('3i'))
            _, uid, _ = struct.unpack('3i', peer)
            parsed = _parse_request(self.rfile.readline(MAX_LINE + 1))
            # Kernel-attested UID must match the *operator-bound* agent name.
            # A successor never inherits the predecessor's Unix principal.
            expected_uid = server.agent_uids.get(parsed["agent"])
            validate_peer_uid(uid, expected_uid, os.getuid(),
                              allow_same_uid_in_tests=server.allow_same_uid_in_tests)
            response = self.server.writer.write(  # type: ignore[attr-defined]
                agent=parsed["agent"], epoch=parsed["epoch"],
                token=parsed["capability"], operation_id=parsed["operation_id"],
                path=parsed["path"], expected_head=parsed["expected_head"],
                content=parsed["content"],
            )
            answer = {"schema": RESPONSE_SCHEMA, "status": "COMMITTED",
                      "new_head": response["new_head"]}
        except ProviderUncertain:
            answer = {"schema": RESPONSE_SCHEMA, "status": "HOLD"}
        except (CustodyDenied, OSError, ValueError, TypeError, KeyError, TimeoutError):
            # Do not echo secrets, raw provider errors, signed grants or SQL.
            answer = {"schema": RESPONSE_SCHEMA, "status": "DENIED"}
        self.wfile.write((json.dumps(answer, sort_keys=True) + "\n").encode())


class PrivateLabGateway(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    """Controller-only process. Does not expose bootstrap/fence/recovery methods."""
    daemon_threads = True
    allow_reuse_address = False

    def __init__(self, socket_path: Path, writer: BrokeredGitWriter, *,
                 expected_client_uid: int | None = None,
                 agent_uids: dict[str, int] | None = None,
                 allow_same_uid_in_tests: bool = False):
        validate_socket_location(socket_path)
        if agent_uids is None:
            if type(expected_client_uid) is not int or expected_client_uid < 0:
                raise CustodyDenied("explicit agent Unix identity required")
            # Single-identity mode exists only for local legacy test harnesses.
            if not allow_same_uid_in_tests:
                raise CustodyDenied("distinct per-agent Unix identities required")
            bindings = {"Agent-A": expected_client_uid, "Agent-B": expected_client_uid}
        else:
            if (set(agent_uids) != {"Agent-A", "Agent-B"} or
                    any(type(uid) is not int or uid < 0 for uid in agent_uids.values()) or
                    (agent_uids["Agent-A"] == agent_uids["Agent-B"] and
                     not allow_same_uid_in_tests)):
                raise CustodyDenied("two distinct operator-bound agent UIDs required")
            bindings = dict(agent_uids)
        if not allow_same_uid_in_tests and os.getuid() in bindings.values():
            raise CustodyDenied("privileged broker UID cannot also be an agent UID")
        self.writer = writer
        self.socket_path = socket_path
        self.agent_uids = bindings
        self.allow_same_uid_in_tests = allow_same_uid_in_tests
        super().__init__(str(socket_path), _Handler)
        os.chmod(socket_path, 0o600)
        self._socket_inode = socket_path.lstat().st_ino

    def server_close(self) -> None:
        super().server_close()
        try:
            st = self.socket_path.lstat()
            if stat.S_ISSOCK(st.st_mode) and st.st_ino == self._socket_inode:
                self.socket_path.unlink()
        except FileNotFoundError:
            pass


def send_write_request(socket_path: Path, *, agent: str, epoch: int,
                       capability: str, operation_id: str, path: str,
                       expected_head: str, content: bytes) -> dict[str, Any]:
    """Unprivileged test/client stub: sends one scoped write, no admin endpoint."""
    if not isinstance(content, bytes) or len(content) > 256_000:
        raise CustodyDenied("content out of scope")
    req = {"schema": "RUNNER_LAB_GATEWAY_WRITE_V1", "action": "WRITE",
           "agent": agent, "epoch": epoch, "capability": capability,
           "operation_id": operation_id, "path": path,
           "expected_head": expected_head,
           "content_b64": base64.b64encode(content).decode("ascii")}
    return send_raw_request(socket_path, (json.dumps(req) + "\n").encode())


def send_raw_request(socket_path: Path, payload: bytes) -> dict[str, Any]:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.settimeout(5)
        sock.connect(str(socket_path))
        sock.sendall(payload)
        sock.shutdown(socket.SHUT_WR)
        response = bytearray()
        while not response.endswith(b"\n") and len(response) < 1024:
            piece = sock.recv(1024)
            if not piece:
                break
            response.extend(piece)
    if not response.endswith(b"\n") or len(response) > 1024:
        raise CustodyDenied("gateway reply is invalid")
    answer = json.loads(response)
    if not isinstance(answer, dict) or answer.get("schema") != RESPONSE_SCHEMA:
        raise CustodyDenied("gateway reply schema invalid")
    return answer
