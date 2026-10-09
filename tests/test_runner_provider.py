"""RNR-06 native local Git push --force-with-lease, uncertain outcome recovery."""
import secrets
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import runner_custody as C
import runner_provider as P


def git(cwd, *args):
    return subprocess.check_output(['git', '-C', str(cwd), *args], text=True, stderr=subprocess.STDOUT).strip()


class GitBrokerCases(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.root = Path(self.t.name)
        self.origin = self.root / 'origin.git'
        subprocess.check_call(['git', 'init', '--bare', '-q', str(self.origin)])
        self.checkout = self.root / 'seed'
        git(self.root, 'init', '-q', '-b', 'lab/runner-provider-sandbox', str(self.checkout))
        git(self.checkout, 'config', 'user.name', 'test')
        git(self.checkout, 'config', 'user.email', 'test@example.invalid')
        for name, data in [('src/inventorylab/parser.py', 'baseline\n'),
                           ('src/inventorylab/report.py', 'report unchanged\n')]:
            file = self.checkout / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(data)
        git(self.checkout, 'add', '.')
        git(self.checkout, 'commit', '-qm', 'baseline')
        self.head0 = git(self.checkout, 'rev-parse', 'HEAD')
        git(self.checkout, 'remote', 'add', 'origin', str(self.origin))
        git(self.checkout, 'push', '-q', 'origin', 'HEAD:refs/heads/lab/runner-provider-sandbox')
        self.provider = P.GitRefProvider(str(self.origin), allow_local_test_remote=True)
        self.db = C.LabGateway(self.root / 'custody.sqlite', b'test-signing-key' * 3)
        self.agent_token = secrets.token_hex(32)
        self.db.bootstrap('LAB-R1', 'Agent-A', self.agent_token, 'operator-lab-bootstrap', self.head0)
        self.writer = P.BrokeredGitWriter(self.db, self.provider)

    def tearDown(self):
        self.t.cleanup()

    def call(self, op='op-1', path='src/inventorylab/parser.py', data=b'changed\n'):
        return self.writer.write(agent='Agent-A', epoch=1, token=self.agent_token,
                                 operation_id=op, path=path,
                                 expected_head=self.head0, content=data)

    def rival_push(self, data='rival changed'):
        (self.checkout / 'src/inventorylab/parser.py').write_text(data)
        git(self.checkout, 'add', '.')
        git(self.checkout, 'commit', '-qm', 'rival')
        git(self.checkout, 'push', '-q', 'origin', 'HEAD:refs/heads/lab/runner-provider-sandbox')
        return git(self.checkout, 'rev-parse', 'HEAD')

    def test_real_git_ref_lease_updates_exact_path_and_parent(self):
        r = self.call()
        self.assertEqual(r['status'], 'PROVIDER_CONFIRMED')
        self.assertEqual(self.provider.head(), r['new_head'])
        self.assertEqual(self.db.read('LAB-R1')['active_head'], r['new_head'])
        self.assertEqual(git(self.origin, 'rev-parse', r['new_head']+'^'), self.head0)
        self.assertEqual(git(self.origin, 'show', r['new_head']+':src/inventorylab/parser.py'), 'changed')
        self.assertEqual(git(self.origin, 'show', r['new_head']+':src/inventorylab/report.py'), 'report unchanged')
        self.assertEqual(self.db.intent('op-1')['intended_head'], r['new_head'])

    def test_replay_rejected_after_provider_confirmed_write(self):
        self.call()
        with self.assertRaises(C.CustodyDenied):
            self.call()

    def test_reporter_scope_rejected_without_operation_reservation(self):
        with self.assertRaises(C.CustodyDenied):
            self.call(path='src/inventorylab/report.py')
        self.assertIsNone(self.db.intent('op-1'))
        self.assertEqual(self.db.read('LAB-R1')['active_head'], self.head0)

    def test_stale_expected_head_fails_closed(self):
        self.rival_push()
        with self.assertRaises(C.CustodyDenied):
            self.call()
        self.assertNotEqual(self.provider.head(), self.head0)

    def test_competing_git_push_after_intent_cannot_overwrite(self):
        case = self
        class RivalDuringLease(P.GitRefProvider):
            def commit_and_push(self, old_head, path, content, operation_id, on_intent):
                def racing_callback(new_head):
                    on_intent(new_head)
                    case.rival_push('rival wins CAS')
                return super().commit_and_push(old_head, path, content, operation_id, racing_callback)
        p = RivalDuringLease(str(self.origin), allow_local_test_remote=True)
        w = P.BrokeredGitWriter(self.db, p)
        with self.assertRaises(P.ProviderUncertain):
            w.write(agent='Agent-A', epoch=1, token=self.agent_token,
                    operation_id='race-1', path='src/inventorylab/parser.py',
                    expected_head=self.head0, content=b'ours denied\n')
        self.assertEqual(git(self.origin, 'show', 'refs/heads/lab/runner-provider-sandbox:src/inventorylab/parser.py'),
                         'rival wins CAS')
        self.assertIsNotNone(self.db.intent('race-1'))
        with self.assertRaises(C.CustodyDenied):
            self.call(op='next-1')

    def test_lost_push_response_recover_success_by_intended_head(self):
        class ResponseLost(P.GitRefProvider):
            def commit_and_push(self, *args):
                candidate, _ = super().commit_and_push(*args)
                raise P.ProviderUncertain('response lost after Git ref update')
        p = ResponseLost(str(self.origin), allow_local_test_remote=True)
        with self.assertRaises(P.ProviderUncertain):
            P.BrokeredGitWriter(self.db, p).write(
                agent='Agent-A', epoch=1, token=self.agent_token,
                operation_id='lost-1', path='src/inventorylab/parser.py',
                expected_head=self.head0, content=b'committed despite lost ack\n')
        expected = self.db.intent('lost-1')['intended_head']
        self.assertEqual(self.provider.head(), expected)
        self.assertEqual(self.db.resolve_unknown('lost-1', provider_head=expected,
                         quiescence_receipt='controller-verified-all-workers-stopped',
                         source_oracle=self.provider.head), 'SUCCEEDED')
        self.assertEqual(self.db.read('LAB-R1')['active_head'], expected)

    def test_pre_dispatch_failure_records_failed_and_unblocks(self):
        class BadBuilder(P.GitRefProvider):
            def commit_and_push(self, *args):
                raise C.CustodyDenied('local candidate construction invalid before intent')
        p = BadBuilder(str(self.origin), allow_local_test_remote=True)
        with self.assertRaises(C.CustodyDenied):
            P.BrokeredGitWriter(self.db, p).write(
                agent='Agent-A', epoch=1, token=self.agent_token,
                operation_id='bad-builder', path='src/inventorylab/parser.py',
                expected_head=self.head0, content=b'x')
        self.assertIsNone(self.db.intent('bad-builder'))
        self.assertEqual(self.provider.head(), self.head0)
        self.assertEqual(self.call(op='after-preflight')['status'], 'PROVIDER_CONFIRMED')

    def test_unknown_without_intent_cannot_resolve(self):
        self.db.admit('LAB-R1', 'Agent-A', 1, self.agent_token, 'old-1',
                      'src/inventorylab/parser.py', self.head0, self.provider.head)
        self.db.finish('old-1', 'UNKNOWN', 'lost connection', self.provider.head)
        with self.assertRaises(C.CustodyDenied):
            self.db.resolve_unknown('old-1', provider_head=self.head0,
                                   quiescence_receipt='operator', source_oracle=self.provider.head)

    def test_unknown_intent_no_dispatch_requires_quiescence_receipt(self):
        class NoDispatch(P.GitRefProvider):
            def commit_and_push(self, old_head, path, content, operation_id, on_intent):
                on_intent('e' * 40)
                raise P.ProviderUncertain('worker never sent push')
        p = NoDispatch(str(self.origin), allow_local_test_remote=True)
        with self.assertRaises(P.ProviderUncertain):
            P.BrokeredGitWriter(self.db, p).write(
                agent='Agent-A', epoch=1, token=self.agent_token,
                operation_id='noop-1', path='src/inventorylab/parser.py',
                expected_head=self.head0, content=b'not pushed')
        with self.assertRaises(C.CustodyDenied):
            self.db.resolve_unknown('noop-1', provider_head=self.head0,
                                   quiescence_receipt='', source_oracle=self.provider.head)
        self.assertEqual(self.db.resolve_unknown('noop-1', provider_head=self.head0,
                         quiescence_receipt='externally-verified-no-running-worker',
                         source_oracle=self.provider.head), 'FAILED')

    def test_unknown_third_party_move_requires_human_reconciliation(self):
        class NoDispatch(P.GitRefProvider):
            def commit_and_push(self, old_head, path, content, operation_id, on_intent):
                on_intent('e' * 40)
                raise P.ProviderUncertain('uncertain')
        with self.assertRaises(P.ProviderUncertain):
            P.BrokeredGitWriter(self.db, NoDispatch(str(self.origin), allow_local_test_remote=True)).write(
                agent='Agent-A', epoch=1, token=self.agent_token,
                operation_id='unknown-1', path='src/inventorylab/parser.py',
                expected_head=self.head0, content=b'something')
        moved = self.rival_push()
        with self.assertRaises(C.CustodyDenied):
            self.db.resolve_unknown('unknown-1', provider_head=moved,
                        quiescence_receipt='processes-stopped', source_oracle=self.provider.head)

    def test_production_remote_uri_pinned_and_test_local_explicit(self):
        with self.assertRaises(C.CustodyDenied):
            P.GitRefProvider(str(self.origin))
        with self.assertRaises(C.CustodyDenied):
            P.GitRefProvider('git@github.com:untrusted/other.git')
        with self.assertRaises(C.CustodyDenied):
            P.GitRefProvider('git@github.com:reallaksh19/relay-v35-e2e-lab.git', branch='../evil')

    def test_old_agent_direct_push_is_possible_if_credentials_not_removed(self):
        # Negative oracle: proves broker state alone CANNOT prevent an agent with
        # independent Git credentials from mutating remote after being fenced.
        report = {'schema': 'RUNNER_RECONCILIATION_V1', 'responsibility': 'LAB-R1',
                  'source_reconciliation': 'SOURCE_RECONCILED_READ_ONLY', 'blockers': [],
                  'writer_authorization': 'DENIED', 'custody_transfer': 'NOT_EXECUTED',
                  'mode': 'EMERGENCY', 'frozen_plan_digest': 'd'*64, 'frozen_bundle_digest': 'e'*64,
                  'source': {'candidate_head': self.head0, 'base_is_ancestor': True,
                             'dirty_paths': [], 'out_of_scope_changes': [], 'branch': 'lab/runner-provider-sandbox'},
                  'remote': {'status': 'MATCH', 'remote_head': self.head0}}
        import runner_pilot as S1
        grant = self.db.issue_transfer_grant(transfer_id='fence-1', responsibility='LAB-R1',
            old_epoch=1, from_agent='Agent-A', to_agent='Agent-B', candidate_head=self.head0,
            reconciliation_digest=S1.digest(S1.canonical(report)),
            operator_receipt='test-only', successor_capability=secrets.token_hex(32))
        self.db.begin_fence(grant, report)
        with self.assertRaises(C.CustodyDenied):
            self.call()
        # This direct push succeeds because local test checkout holds an independent write route.
        # Production safety MUST revoke it. This is proof of an explicit blocker.
        self.rival_push('bypass exists')
        self.assertNotEqual(self.provider.head(), self.head0)


if __name__ == '__main__':
    unittest.main()
