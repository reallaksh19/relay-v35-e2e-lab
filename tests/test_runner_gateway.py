"""RNR-06B executable private Unix-socket service and adversarial requests."""
from __future__ import annotations

import base64
import json
import os
import secrets
import socket
import stat
import subprocess
import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import runner_custody as C
import runner_gateway as G
import runner_pilot as S1
import runner_provider as P


class PrivateGatewayTests(unittest.TestCase):
    def setUp(self):
        # Genuine Git remote backed by a bare repository, not a fabricated CAS.
        import test_runner_provider
        self.fixture = test_runner_provider.GitBrokerCases('test_real_git_ref_lease_updates_exact_path_and_parent')
        self.fixture.setUp()
        self.dir = self.fixture.root / 'operator-socket-only'
        self.dir.mkdir(mode=0o700)
        self.dir.chmod(0o700)
        self.path = self.dir / 'runner.sock'
        self.gateway = G.PrivateLabGateway(
            self.path, self.fixture.writer,
            expected_client_uid=os.getuid(), allow_same_uid_in_tests=True)
        self.worker = threading.Thread(target=self.gateway.serve_forever, kwargs={'poll_interval': .01})
        self.worker.start()

    def tearDown(self):
        self.gateway.shutdown()
        self.worker.join(timeout=5)
        self.gateway.server_close()
        self.fixture.tearDown()

    def request(self, *, agent='Agent-A', epoch=1, token=None, op='gateway-op-1',
                path='src/inventorylab/parser.py', head=None, data=b'gateway commit\n'):
        f = self.fixture
        return G.send_write_request(self.path, agent=agent, epoch=epoch,
                                    capability=token or f.agent_token,
                                    operation_id=op, path=path,
                                    expected_head=head or f.head0, content=data)

    def raw(self, data):
        return G.send_raw_request(self.path, data)

    def test_real_write_through_socket_updates_remote(self):
        result = self.request()
        self.assertEqual(result['status'], 'COMMITTED')
        self.assertEqual(self.fixture.provider.head(), result['new_head'])
        self.assertEqual(self.fixture.db.read('LAB-R1')['active_head'], result['new_head'])
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)

    def test_no_direct_provider_or_branch_override(self):
        fields = self.request_dict()
        fields['remote'] = '/some/attacker/repo'
        self.assertEqual(self.raw((json.dumps(fields)+'\n').encode())['status'], 'DENIED')
        self.assertEqual(self.fixture.provider.head(), self.fixture.head0)

    def test_no_operator_promotion_endpoint(self):
        fields = self.request_dict()
        fields['action'] = 'PROMOTE'
        self.assertEqual(self.raw((json.dumps(fields)+'\n').encode())['status'], 'DENIED')
        self.assertEqual(self.fixture.db.read('LAB-R1')['epoch'], 1)

    def test_no_status_or_secrets_endpoint(self):
        self.assertEqual(self.raw(b'{"action":"STATUS"}\n')['status'], 'DENIED')

    def test_invalid_capability_denied(self):
        result = self.request(token=secrets.token_hex(32))
        self.assertEqual(result['status'], 'DENIED')
        self.assertEqual(self.fixture.provider.head(), self.fixture.head0)
        self.assertNotIn(self.fixture.agent_token, json.dumps(result))

    def test_bool_epoch_is_rejected(self):
        fields = self.request_dict()
        fields['epoch'] = True
        self.assertEqual(self.raw((json.dumps(fields)+'\n').encode())['status'], 'DENIED')

    def test_replayed_write_does_not_duplicate_commit(self):
        first = self.request()
        second = self.request()
        self.assertEqual(first['status'], 'COMMITTED')
        self.assertEqual(second['status'], 'DENIED')
        self.assertEqual(self.fixture.provider.head(), first['new_head'])

    def test_old_agent_rejected_after_fence_before_promotion(self):
        report, grant = self.prepare_fence()
        self.fixture.db.begin_fence(grant, report)
        self.assertEqual(self.request()['status'], 'DENIED')
        self.assertEqual(self.fixture.provider.head(), self.fixture.head0)

    def test_promoted_successor_can_write_and_predecessor_cannot(self):
        report, grant = self.prepare_fence()
        self.fixture.db.begin_fence(grant, report)
        self.fixture.db.finish_transfer(grant, self.new_token, self.fixture.provider.head)
        self.assertEqual(self.request()['status'], 'DENIED')
        self.assertEqual(self.request(agent='Agent-B', epoch=2, token=self.new_token,
                                      op='B-unique')['status'], 'COMMITTED')
        self.assertEqual(self.fixture.db.read('LAB-R1')['epoch'], 2)

    def test_wrong_scope_is_denied(self):
        self.assertEqual(self.request(path='src/inventorylab/report.py')['status'], 'DENIED')

    def test_extra_untrusted_fields_rejected(self):
        fields = self.request_dict()
        fields['owner_approval'] = True
        self.assertEqual(self.raw((json.dumps(fields)+'\n').encode())['status'], 'DENIED')

    def test_duplicate_json_key_rejected(self):
        # JSON parser must not quietly take attacker's last-supplied identity.
        fields = self.request_dict()
        raw = (json.dumps(fields)[:-1] + ',"agent":"Agent-B"}\n').encode()
        self.assertEqual(self.raw(raw)['status'], 'DENIED')

    def test_invalid_base64_rejected(self):
        fields = self.request_dict()
        fields['content_b64'] = 'not base64???'
        self.assertEqual(self.raw((json.dumps(fields)+'\n').encode())['status'], 'DENIED')

    def test_oversized_frame_denied(self):
        self.assertEqual(self.raw(b'X' * (G.MAX_LINE + 1) + b'\n')['status'], 'DENIED')

    def test_unterminated_frame_denied(self):
        self.assertEqual(self.raw(b'{}')['status'], 'DENIED')

    def test_private_directory_required(self):
        pub = self.fixture.root / 'untrusted'
        pub.mkdir(mode=0o755)
        pub.chmod(0o755)
        with self.assertRaises(C.CustodyDenied):
            G.PrivateLabGateway(pub / 'other.sock', self.fixture.writer,
                                expected_client_uid=os.getuid(), allow_same_uid_in_tests=True)

    def test_symlink_directory_rejected(self):
        alias = self.fixture.root / 'alias'
        alias.symlink_to(self.dir, target_is_directory=True)
        with self.assertRaises(C.CustodyDenied):
            G.PrivateLabGateway(alias / 'other.sock', self.fixture.writer,
                                expected_client_uid=os.getuid(), allow_same_uid_in_tests=True)

    def test_existing_socket_cannot_be_rebound(self):
        with self.assertRaises(C.CustodyDenied):
            G.PrivateLabGateway(self.path, self.fixture.writer,
                                expected_client_uid=os.getuid(), allow_same_uid_in_tests=True)

    def test_production_cannot_share_privileged_unix_identity(self):
        with self.assertRaises(C.CustodyDenied):
            G.PrivateLabGateway(self.dir / 'other.sock', self.fixture.writer,
                                expected_client_uid=os.getuid())

    def test_missing_identity_fails_closed(self):
        with self.assertRaises(C.CustodyDenied):
            G.PrivateLabGateway(self.dir / 'other.sock', self.fixture.writer)

    def test_peer_identity_oracle_denies_other_user(self):
        with self.assertRaises(C.CustodyDenied):
            G.validate_peer_uid(os.getuid() + 1, os.getuid(), os.getuid(),
                                allow_same_uid_in_tests=True)

    def test_lost_provider_ack_remains_hold_through_socket(self):
        fixture = self.fixture
        class AckLost(P.GitRefProvider):
            def commit_and_push(self, *args):
                super().commit_and_push(*args)
                raise P.ProviderUncertain('ack lost')
        self.gateway.writer = P.BrokeredGitWriter(
            fixture.db, AckLost(str(fixture.origin), allow_local_test_remote=True))
        self.assertEqual(self.request()['status'], 'HOLD')
        self.assertEqual(self.fixture.db.read('LAB-R1')['active_head'], self.fixture.head0)
        self.assertEqual(self.request(op='late-other-write')['status'], 'DENIED')

    def test_client_agent_environment_has_no_credential_in_response(self):
        # This tests response redaction, NOT actual Unix identity separation.
        f = self.request_dict()
        f['capability'] = 'SENSITIVE_TEST_TOKEN_SHOULD_NOT_LEAK'
        result = self.raw((json.dumps(f) + '\n').encode())
        self.assertEqual(result, {'schema': G.RESPONSE_SCHEMA, 'status': 'DENIED'})

    def test_separate_client_process_reaches_only_brokered_socket(self):
        # Untrusted client runs in its own process with no inherited GitHub/SSH
        # environment. It is still the same Unix UID in this test: production
        # process-user separation and repository token revocation are UNKNOWN.
        snippet = (
            'import base64, json, sys, pathlib, runner_gateway as G\n'
            'data=json.loads(sys.stdin.readline())\n'
            'reply=G.send_write_request(pathlib.Path(data["socket"]), '
            'agent=data["agent"],epoch=data["epoch"],capability=data["capability"],'
            'operation_id=data["operation_id"],path=data["path"],'
            'expected_head=data["expected_head"],content=base64.b64decode(data["payload"]))\n'
            'print(json.dumps(reply))\n'
        )
        payload = {'socket':str(self.path), 'agent':'Agent-A','epoch':1,
                   'capability':self.fixture.agent_token,'operation_id':'client-process-1',
                   'path':'src/inventorylab/parser.py',
                   'expected_head':self.fixture.head0,
                   'payload':base64.b64encode(b'from separate agent process\n').decode()}
        child_env = {'PATH':os.environ.get('PATH', '/usr/bin:/bin'),
                     'PYTHONPATH':str(Path(__file__).resolve().parents[1] / 'scripts')}
        p = subprocess.run([sys.executable, '-c', snippet],
                           input=json.dumps(payload)+'\n', text=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           env=child_env, timeout=10)
        self.assertEqual(p.returncode, 0, p.stderr)
        reply = json.loads(p.stdout)
        self.assertEqual(reply['status'], 'COMMITTED')
        self.assertEqual(self.fixture.provider.head(), reply['new_head'])

    def request_dict(self):
        return {'schema':'RUNNER_LAB_GATEWAY_WRITE_V1', 'action':'WRITE',
                'agent':'Agent-A','epoch':1,'capability':self.fixture.agent_token,
                'operation_id':'gateway-op-1', 'path':'src/inventorylab/parser.py',
                'expected_head':self.fixture.head0,
                'content_b64':base64.b64encode(b'x\n').decode()}

    def prepare_fence(self):
        f = self.fixture
        report = {'schema':'RUNNER_RECONCILIATION_V1','responsibility':'LAB-R1',
                  'mode':'EMERGENCY','frozen_plan_digest':'d'*64,'frozen_bundle_digest':'e'*64,
                  'source_reconciliation':'SOURCE_RECONCILED_READ_ONLY',
                  'blockers':[], 'writer_authorization':'DENIED',
                  'custody_transfer':'NOT_EXECUTED',
                  'source':{'candidate_head':f.head0,'base_is_ancestor':True,
                            'dirty_paths':[],'out_of_scope_changes':[],
                            'branch':'lab/runner-provider-sandbox'},
                  'remote':{'status':'MATCH','remote_head':f.head0}}
        self.new_token = secrets.token_hex(32)
        grant = f.db.issue_transfer_grant(transfer_id='transfer-b',responsibility='LAB-R1',
            old_epoch=1,from_agent='Agent-A',to_agent='Agent-B',candidate_head=f.head0,
            reconciliation_digest=S1.digest(S1.canonical(report)),
            operator_receipt='operator-explicit-lab-only',successor_capability=self.new_token)
        return report, grant


if __name__ == '__main__':
    unittest.main()
