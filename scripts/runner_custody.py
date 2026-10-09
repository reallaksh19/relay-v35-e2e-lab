#!/usr/bin/env python3
"""RNR-05 LAB custody gateway. Only protects operations brokered through it.

No GitHub credential distribution, provider-side fencing or Owner authorization
is implemented by this module. Operator methods MUST be behind separate ACLs.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Callable

import runner_pilot as S1

SCHEMA = "RUNNER_CUSTODY_GRANT_V1"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$")
GRANT_FIELDS = frozenset({"schema", "transfer_id", "responsibility", "old_epoch",
                          "from_agent", "to_agent", "candidate_head", "reconciliation_digest",
                          "operator_receipt", "successor_token_hash", "signature"})
ALLOWED_PATHS = frozenset({"src/inventorylab/parser.py", "tests/test_inventory_parser.py"})
RESULTS = frozenset({"SUCCEEDED", "FAILED", "UNKNOWN"})


class CustodyDenied(S1.PilotError):
    pass


def validate_id(value: str) -> None:
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise CustodyDenied("invalid identity")


def require_sha(value: str) -> None:
    if not isinstance(value, str) or not HEX40.fullmatch(value):
        raise CustodyDenied("invalid exact candidate head")


def token_hash(token: str) -> str:
    if not isinstance(token, str) or len(token) < 32:
        raise CustodyDenied("executor capability must be a strong opaque token")
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def valid_reconciliation(report: dict, head: str, report_digest: str) -> None:
    if not isinstance(report, dict) or S1.digest(S1.canonical(report)) != report_digest:
        raise CustodyDenied("reconciliation receipt digest mismatch")
    if (report.get("schema") != "RUNNER_RECONCILIATION_V1"
            or report.get("responsibility") != "LAB-R1"
            or report.get("source_reconciliation") != "SOURCE_RECONCILED_READ_ONLY"
            or report.get("blockers") != []
            or report.get("writer_authorization") != "DENIED"
            or report.get("custody_transfer") != "NOT_EXECUTED"
            or report.get("source", {}).get("candidate_head") != head
            or report.get("remote", {}).get("status") != "MATCH"
            or report.get("remote", {}).get("remote_head") != head):
        raise CustodyDenied("Stage 2 is not a clean, sealed, read-only reconciliation")


class LabGateway:
    """SQLite-backed monotonic epoch broker; no direct GitHub/write capability.

    Deploy as a trusted *single* gateway with exclusive credentials and separate
    operator/agent endpoints. The Python object itself is not an auth boundary.
    """

    def __init__(self, path: Path, operator_key: bytes):
        if not isinstance(operator_key, bytes) or len(operator_key) < 32:
            raise CustodyDenied("controller operator signing key must be 32+ bytes")
        self.path, self.key = Path(path), operator_key
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            fd = os.open(self.path, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600)
            os.close(fd)
        with self.tx() as c:
            c.execute("CREATE TABLE IF NOT EXISTS custody ("
                      "responsibility TEXT PRIMARY KEY, epoch INTEGER NOT NULL, holder TEXT NOT NULL, "
                      "token_hash TEXT NOT NULL, active_head TEXT NOT NULL, phase TEXT NOT NULL, pending_id TEXT, "
                      "pending_to TEXT, pending_head TEXT, pending_digest TEXT)")
            c.execute("CREATE TABLE IF NOT EXISTS operations ("
                      "id TEXT PRIMARY KEY, responsibility TEXT NOT NULL, epoch INTEGER NOT NULL, "
                      "holder TEXT NOT NULL, path TEXT NOT NULL, candidate_head TEXT NOT NULL, "
                      "status TEXT NOT NULL, evidence_ref TEXT)")
            c.execute("CREATE TABLE IF NOT EXISTS transfers ("
                      "id TEXT PRIMARY KEY, responsibility TEXT NOT NULL, old_epoch INTEGER NOT NULL, "
                      "new_epoch INTEGER NOT NULL, old_holder TEXT NOT NULL, new_holder TEXT NOT NULL, "
                      "candidate_head TEXT NOT NULL, reconciliation_digest TEXT NOT NULL)")
            c.execute("CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                      "responsibility TEXT, event TEXT NOT NULL, ref TEXT NOT NULL)")

    @contextmanager
    def tx(self):
        conn = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("BEGIN IMMEDIATE")
            yield conn
            conn.execute("COMMIT")
        except BaseException:
            conn.execute("ROLLBACK")
            raise
        finally:
            conn.close()

    @staticmethod
    def row(conn, responsibility: str):
        r = conn.execute("SELECT * FROM custody WHERE responsibility=?", (responsibility,)).fetchone()
        if not r:
            raise CustodyDenied("unknown responsibility")
        return r

    @staticmethod
    def audit(conn, responsibility: str, event: str, ref: str):
        conn.execute("INSERT INTO audit(responsibility,event,ref) VALUES (?,?,?)",
                     (responsibility, event, ref))

    def bootstrap(self, responsibility: str, agent: str, capability: str, operator_receipt: str, initial_head: str) -> dict:
        # Trusted OPERATOR ONLY. A runner/agent MUST NOT access this method.
        validate_id(responsibility)
        validate_id(agent)
        require_sha(initial_head)
        if responsibility != "LAB-R1" or not isinstance(operator_receipt, str) or not operator_receipt.strip():
            raise CustodyDenied("missing scoped lab bootstrap receipt")
        cap = token_hash(capability)
        with self.tx() as c:
            if c.execute("SELECT 1 FROM custody WHERE responsibility=?", (responsibility,)).fetchone():
                raise CustodyDenied("bootstrap cannot reset existing epoch")
            c.execute("INSERT INTO custody VALUES(?,1,? ,?, ?,'ACTIVE',NULL,NULL,NULL,NULL)",
                      (responsibility, agent, cap, initial_head))
            self.audit(c, responsibility, "BOOTSTRAP", operator_receipt)
            return self.read_in_tx(c, responsibility)

    @staticmethod
    def read_in_tx(c, responsibility: str) -> dict:
        row = LabGateway.row(c, responsibility)
        return {"responsibility": responsibility, "epoch": row["epoch"],
                "holder": row["holder"], "phase": row["phase"], "active_head": row["active_head"],
                "pending_transfer_id": row["pending_id"]}

    def read(self, responsibility: str) -> dict:
        with self.tx() as c:
            return self.read_in_tx(c, responsibility)

    def issue_transfer_grant(self, *, transfer_id: str, responsibility: str,
                             old_epoch: int, from_agent: str, to_agent: str,
                             candidate_head: str, reconciliation_digest: str,
                             operator_receipt: str, successor_capability: str) -> dict:
        # Operator-controlled signing API, not available to executor clients.
        for value in (transfer_id, responsibility, from_agent, to_agent):
            validate_id(value)
        require_sha(candidate_head)
        if responsibility != "LAB-R1" or not isinstance(old_epoch, int) or isinstance(old_epoch, bool) or old_epoch < 1:
            raise CustodyDenied("invalid epoch or responsibility")
        if to_agent == from_agent or not re.fullmatch(r"[0-9a-f]{64}", reconciliation_digest):
            raise CustodyDenied("invalid transfer digest or successor")
        if not isinstance(operator_receipt, str) or not operator_receipt.strip():
            raise CustodyDenied("missing operator grant evidence")
        payload = {"schema": SCHEMA, "transfer_id": transfer_id, "responsibility": responsibility,
                   "old_epoch": old_epoch, "from_agent": from_agent, "to_agent": to_agent,
                   "candidate_head": candidate_head, "reconciliation_digest": reconciliation_digest,
                   "operator_receipt": operator_receipt,
                   "successor_token_hash": token_hash(successor_capability)}
        payload["signature"] = hmac.new(self.key, S1.canonical(payload), hashlib.sha256).hexdigest()
        return payload

    def verify_grant(self, grant: dict) -> None:
        if not isinstance(grant, dict) or set(grant) != GRANT_FIELDS:
            raise CustodyDenied("grant fields incorrect")
        unsigned = {k: v for k, v in grant.items() if k != "signature"}
        signature = hmac.new(self.key, S1.canonical(unsigned), hashlib.sha256).hexdigest()
        if not isinstance(grant["signature"], str) or not hmac.compare_digest(signature, grant["signature"]):
            raise CustodyDenied("operator signature invalid")
        if grant["schema"] != SCHEMA or grant["responsibility"] != "LAB-R1":
            raise CustodyDenied("wrong grant schema/scope")
        for k in ("transfer_id", "responsibility", "from_agent", "to_agent"):
            validate_id(grant[k])
        require_sha(grant["candidate_head"])
        if (type(grant["old_epoch"]) is not int or grant["old_epoch"] < 1
                or not re.fullmatch(r"[0-9a-f]{64}", str(grant["reconciliation_digest"]))
                or grant["from_agent"] == grant["to_agent"]
                or not re.fullmatch(r"[0-9a-f]{64}", str(grant["successor_token_hash"]))):
            raise CustodyDenied("grant identity mismatch")

    def begin_fence(self, grant: dict, reconciliation: dict) -> dict:
        self.verify_grant(grant)
        valid_reconciliation(reconciliation, grant["candidate_head"], grant["reconciliation_digest"])
        resp = grant["responsibility"]
        with self.tx() as c:
            row = self.row(c, resp)
            if row["phase"] == "FENCING" and row["pending_id"] == grant["transfer_id"]:
                return self.read_in_tx(c, resp)
            if (row["phase"] != "ACTIVE" or row["epoch"] != grant["old_epoch"]
                    or row["holder"] != grant["from_agent"]
                    or row["active_head"] != grant["candidate_head"]):
                raise CustodyDenied("stale, duplicate or competing transfer")
            if c.execute("SELECT 1 FROM transfers WHERE id=?", (grant["transfer_id"],)).fetchone():
                raise CustodyDenied("reused transfer id")
            c.execute("UPDATE custody SET phase='FENCING', pending_id=?, pending_to=?, "
                      "pending_head=?, pending_digest=? WHERE responsibility=?",
                      (grant["transfer_id"], grant["to_agent"], grant["candidate_head"],
                       grant["reconciliation_digest"], resp))
            self.audit(c, resp, "FENCE_START", grant["transfer_id"])
            return self.read_in_tx(c, resp)

    def admit(self, responsibility: str, agent: str, epoch: int, capability: str,
              operation_id: str, path: str, candidate_head: str,
              source_oracle: Callable[[], str]) -> dict:
        validate_id(agent)
        validate_id(operation_id)
        require_sha(candidate_head)
        if path not in ALLOWED_PATHS or type(epoch) is not int:
            raise CustodyDenied("write outside allowed LAB-R1 surface")
        supplied = token_hash(capability)
        with self.tx() as c:
            row = self.row(c, responsibility)
            if (row["phase"] != "ACTIVE" or row["holder"] != agent
                    or row["epoch"] != epoch or row["active_head"] != candidate_head
                    or not hmac.compare_digest(row["token_hash"], supplied)):
                raise CustodyDenied("old or unauthorized executor was fenced")
            if source_oracle() != candidate_head:
                raise CustodyDenied("provider source drift before write admission")
            if c.execute("SELECT 1 FROM operations WHERE responsibility=? AND status IN ('STARTED','UNKNOWN')",
                         (responsibility,)).fetchone():
                raise CustodyDenied("unresolved operation blocks further writes")
            if c.execute("SELECT 1 FROM operations WHERE id=?", (operation_id,)).fetchone():
                raise CustodyDenied("operation ID already used; never replay")
            c.execute("INSERT INTO operations VALUES (?,?,?,?,? ,?,'STARTED',NULL)",
                      (operation_id, responsibility, epoch, agent, path, candidate_head))
            self.audit(c, responsibility, "WRITE_ADMITTED", operation_id)
            # Trusted controller MUST now apply a provider-side candidate SHA CAS.
            return {"operation_id": operation_id, "decision": "BROKER_ADMITTED_NOT_PROVIDER_COMMITTED",
                    "epoch": epoch, "candidate_head": candidate_head}

    def finish(self, operation_id: str, result: str, evidence_ref: str,
               source_oracle: Callable[[], str], new_head: str | None = None) -> None:
        # Controller-only method. An UNKNOWN operation is unresolved and blocks promotion.
        if result not in RESULTS or not isinstance(evidence_ref, str) or not evidence_ref.strip():
            raise CustodyDenied("result/evidence required")
        validate_id(operation_id)
        with self.tx() as c:
            op = c.execute("SELECT * FROM operations WHERE id=?", (operation_id,)).fetchone()
            if not op or op["status"] != "STARTED":
                raise CustodyDenied("unknown or already settled operation")
            row = self.row(c, op["responsibility"])
            if result == "SUCCEEDED":
                require_sha(new_head)
                if source_oracle() != new_head:
                    raise CustodyDenied("provider did not verify resulting candidate head")
                c.execute("UPDATE custody SET active_head=? WHERE responsibility=?",
                          (new_head, op["responsibility"]))
            elif result == "FAILED" and source_oracle() != row["active_head"]:
                raise CustodyDenied("failure may have committed remotely: classify UNKNOWN")
            c.execute("UPDATE operations SET status=?, evidence_ref=? WHERE id=?",
                      (result, evidence_ref, operation_id))
            self.audit(c, op["responsibility"], "WRITE_" + result, operation_id)

    def finish_transfer(self, grant: dict, new_capability: str,
                        source_oracle: Callable[[], str]) -> dict:
        self.verify_grant(grant)
        new_hash = token_hash(new_capability)
        if not hmac.compare_digest(new_hash, grant["successor_token_hash"]):
            raise CustodyDenied("successor capability does not match signed transfer grant")
        resp = grant["responsibility"]
        with self.tx() as c:
            row = self.row(c, resp)
            committed = c.execute("SELECT * FROM transfers WHERE id=?", (grant["transfer_id"],)).fetchone()
            if committed:
                if (committed["responsibility"] != resp or committed["old_epoch"] != grant["old_epoch"]
                        or committed["new_holder"] != grant["to_agent"] or
                        committed["candidate_head"] != grant["candidate_head"] or
                        committed["reconciliation_digest"] != grant["reconciliation_digest"] or
                        row["epoch"] != committed["new_epoch"] or row["holder"] != grant["to_agent"] or
                        not hmac.compare_digest(row["token_hash"], new_hash)):
                    raise CustodyDenied("competing transfer or conflicting retry")
                return self.read_in_tx(c, resp)
            if (row["phase"] != "FENCING" or row["pending_id"] != grant["transfer_id"]
                    or row["epoch"] != grant["old_epoch"] or row["holder"] != grant["from_agent"]
                    or row["pending_to"] != grant["to_agent"]
                    or row["active_head"] != grant["candidate_head"]
                    or row["pending_head"] != grant["candidate_head"]
                    or row["pending_digest"] != grant["reconciliation_digest"]):
                raise CustodyDenied("not this transfer's fenced predecessor")
            outstanding = c.execute("SELECT count(*) FROM operations WHERE responsibility=? AND status IN ('STARTED','UNKNOWN')",
                                    (resp,)).fetchone()[0]
            if outstanding:
                raise CustodyDenied("in-flight or uncertain writes require exact provider reconciliation")
            # Must be a trusted controller-side source read. Caller strings are not authority.
            try:
                live_head = source_oracle()
            except Exception as exc:
                raise CustodyDenied("current-source oracle unavailable") from exc
            if live_head != grant["candidate_head"]:
                raise CustodyDenied("source moved since Stage 2; fresh reconciliation required")
            new_epoch = row["epoch"] + 1
            c.execute("UPDATE custody SET epoch=?, holder=?, token_hash=?, phase='ACTIVE', "
                      "pending_id=NULL, pending_to=NULL, pending_head=NULL, pending_digest=NULL WHERE responsibility=?",
                      (new_epoch, grant["to_agent"], new_hash, resp))
            c.execute("INSERT INTO transfers VALUES (?,?,?,?,?,?,?,?)",
                      (grant["transfer_id"], resp, grant["old_epoch"], new_epoch,
                       grant["from_agent"], grant["to_agent"], grant["candidate_head"], grant["reconciliation_digest"]))
            self.audit(c, resp, "PROMOTED", grant["transfer_id"])
            return self.read_in_tx(c, resp)

    def audit_events(self, responsibility: str) -> list[dict]:
        with self.tx() as c:
            return [dict(r) for r in c.execute("SELECT id, responsibility, event, ref FROM audit "
                                                "WHERE responsibility=? ORDER BY id", (responsibility,))]
