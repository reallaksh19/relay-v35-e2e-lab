"""RNR-05 SQLite broker/fencing tests. No real GitHub authorization granted."""
import copy
import json
import secrets
import sys
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import runner_pilot as S1
import runner_custody as C

HEAD0 = 'a' * 40
HEAD1 = 'b' * 40
HEAD2 = 'c' * 40


class BrokerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / 'broker.db'
        self.key = b'controller-key-not-available-to-agents' + b' ' * 10
        self.b = C.LabGateway(self.db, self.key)
        self.a_token = secrets.token_hex(32)
        self.b_token = secrets.token_hex(32)
        self.head = HEAD0
        self.oracle = lambda: self.head
        self.b.bootstrap('LAB-R1', 'Agent-A', self.a_token, 'operator-bootstrap-1', HEAD0)
        self.report = self.reconciliation(HEAD0)
        self.grant = self.make_grant('Agent-B')

    def tearDown(self):
        self.tmp.cleanup()

    def reconciliation(self, head):
        return {'schema': 'RUNNER_RECONCILIATION_V1', 'responsibility': 'LAB-R1',
                'mode': 'EMERGENCY', 'frozen_plan_digest': 'd'*64,
                'frozen_bundle_digest': 'e'*64,
                'source_reconciliation': 'SOURCE_RECONCILED_READ_ONLY',
                'blockers': [], 'writer_authorization': 'DENIED',
                'custody_transfer': 'NOT_EXECUTED',
                'source': {'candidate_head': head, 'base_is_ancestor': True,
                           'dirty_paths': [], 'out_of_scope_changes': [], 'branch': 'main'},
                'remote': {'status': 'MATCH', 'remote_head': head}}

    def make_grant(self, next_holder, transfer_id='handoff-1', head=HEAD0):
        return self.b.issue_transfer_grant(
            transfer_id=transfer_id, responsibility='LAB-R1', old_epoch=1,
            from_agent='Agent-A', to_agent=next_holder,
            candidate_head=head,
            reconciliation_digest=S1.digest(S1.canonical(self.report)),
            operator_receipt='LAB-OPERATOR-APPROVAL-REF-001',
            successor_capability=self.b_token)

    def admit_a(self, op_id='write-1', path='src/inventorylab/parser.py', head=HEAD0):
        return self.b.admit('LAB-R1', 'Agent-A', 1, self.a_token,
                            op_id, path, head, self.oracle)

    def test_bootstrap_epoch_is_one(self):
        self.assertEqual(self.b.read('LAB-R1')['epoch'], 1)
        self.assertEqual(self.b.read('LAB-R1')['active_head'], HEAD0)

    def test_rebootstrap_cannot_reset_epoch(self):
        with self.assertRaises(C.CustodyDenied):
            self.b.bootstrap('LAB-R1', 'Agent-C', secrets.token_hex(32), 'receipt', HEAD0)

    def test_invalid_grant_signature_rejected(self):
        altered = dict(self.grant, to_agent='Agent-C')
        with self.assertRaises(C.CustodyDenied):
            self.b.begin_fence(altered, self.report)

    def test_forged_stage2_admission_rejected(self):
        report = dict(self.report, writer_authorization='GRANTED')
        # Digest mismatch already proves forged record cannot be substituted.
        with self.assertRaises(C.CustodyDenied):
            self.b.begin_fence(self.grant, report)

    def test_stage2_blockers_rejected_even_if_operator_signs_digest(self):
        self.report['blockers'] = ['UNCOMMITTED_MATERIAL']
        self.grant = self.make_grant('Agent-B')
        with self.assertRaises(C.CustodyDenied):
            self.b.begin_fence(self.grant, self.report)

    def test_real_stage2_freeze_and_repository_observation_admitted_read_only(self):
        import test_runner_stage2 as ST
        t = ST.Stage2Tests('test_emergency_no_handover_remains_read_only')
        t.setUp()
        try:
            actual = t.reconcile()
            self.assertEqual(actual['source_reconciliation'], 'SOURCE_RECONCILED_READ_ONLY')
            C.valid_reconciliation(actual, t.base, S1.digest(S1.canonical(actual)))
            # Actual Stage 2 has no writer authority despite source success.
            self.assertEqual(actual['writer_authorization'], 'DENIED')
        finally:
            t.tearDown()

    def test_read_only_report_missing_frozen_plan_is_rejected(self):
        changed = dict(self.report)
        changed.pop('frozen_plan_digest')
        with self.assertRaises(C.CustodyDenied):
            C.valid_reconciliation(changed, HEAD0, S1.digest(S1.canonical(changed)))

    def test_agent_a_can_write_before_fence(self):
        receipt = self.admit_a()
        self.assertEqual(receipt['decision'], 'BROKER_ADMITTED_NOT_PROVIDER_COMMITTED')
        self.assertEqual(self.b.read('LAB-R1')['holder'], 'Agent-A')

    def test_write_surface_is_explicit(self):
        with self.assertRaises(C.CustodyDenied):
            self.admit_a(path='src/inventorylab/report.py')

    def test_invalid_executor_token_denied(self):
        with self.assertRaises(C.CustodyDenied):
            self.b.admit('LAB-R1', 'Agent-A', 1, self.b_token, 'fake-1',
                         'src/inventorylab/parser.py', HEAD0, self.oracle)

    def test_provider_drift_denied_at_admission(self):
        self.head = HEAD1
        with self.assertRaises(C.CustodyDenied):
            self.admit_a()

    def test_reused_operation_id_never_redispatches(self):
        self.admit_a()
        self.b.finish('write-1', 'FAILED', 'provider-explicit-rejection', self.oracle)
        with self.assertRaises(C.CustodyDenied):
            self.admit_a()

    def test_write_result_advances_bound_head_only_with_provider_evidence(self):
        self.admit_a()
        self.head = HEAD1
        with self.assertRaises(C.CustodyDenied):
            self.b.finish('write-1', 'SUCCEEDED', 'provider-commit', self.oracle, HEAD2)
        self.b.finish('write-1', 'SUCCEEDED', 'provider-commit', self.oracle, HEAD1)
        self.assertEqual(self.b.read('LAB-R1')['active_head'], HEAD1)
        with self.assertRaises(C.CustodyDenied):
            self.admit_a('write-2', head=HEAD0)
        self.b.admit('LAB-R1', 'Agent-A', 1, self.a_token, 'write-2',
                     'tests/test_inventory_parser.py', HEAD1, self.oracle)

    def test_fencing_immediately_blocks_new_agent_a_admissions(self):
        self.b.begin_fence(self.grant, self.report)
        self.assertEqual(self.b.read('LAB-R1')['phase'], 'FENCING')
        with self.assertRaises(C.CustodyDenied):
            self.admit_a()

    def test_begin_fence_idempotent_for_same_grant(self):
        p = self.b.begin_fence(self.grant, self.report)
        self.assertEqual(p, self.b.begin_fence(self.grant, self.report))
        self.assertEqual(len([e for e in self.b.audit_events('LAB-R1') if e['event']=='FENCE_START']), 1)

    def test_unfinished_write_blocks_promotion(self):
        self.admit_a()
        self.b.begin_fence(self.grant, self.report)
        with self.assertRaises(C.CustodyDenied):
            self.b.finish_transfer(self.grant, self.b_token, self.oracle)
        self.b.finish('write-1', 'FAILED', 'provider-rejection', self.oracle)
        self.assertEqual(self.b.finish_transfer(self.grant, self.b_token, self.oracle)['epoch'], 2)

    def test_uncertain_write_blocks_promotion_after_crash(self):
        self.admit_a()
        self.b.finish('write-1', 'UNKNOWN', 'provider-outcome-unknown', self.oracle)
        self.b.begin_fence(self.grant, self.report)
        with self.assertRaises(C.CustodyDenied):
            self.b.finish_transfer(self.grant, self.b_token, self.oracle)
        self.assertEqual(self.b.read('LAB-R1')['phase'], 'FENCING')

    def test_source_advance_after_stage2_blocks_promotion(self):
        self.b.begin_fence(self.grant, self.report)
        self.head = HEAD1
        with self.assertRaises(C.CustodyDenied):
            self.b.finish_transfer(self.grant, self.b_token, self.oracle)

    def test_successful_promotion_fences_old_token_and_accepts_new(self):
        self.b.begin_fence(self.grant, self.report)
        s = self.b.finish_transfer(self.grant, self.b_token, self.oracle)
        self.assertEqual((s['epoch'], s['holder'], s['phase']), (2, 'Agent-B', 'ACTIVE'))
        with self.assertRaises(C.CustodyDenied):
            self.admit_a()
        admitted = self.b.admit('LAB-R1', 'Agent-B', 2, self.b_token, 'B-1',
                                  'src/inventorylab/parser.py', HEAD0, self.oracle)
        self.assertEqual(admitted['epoch'], 2)
        with self.assertRaises(C.CustodyDenied):
            self.b.admit('LAB-R1', 'Agent-B', 1, self.b_token, 'wrong-epoch',
                         'src/inventorylab/parser.py', HEAD0, self.oracle)

    def test_promotion_replay_same_token_is_idempotent_not_new_epoch(self):
        self.b.begin_fence(self.grant, self.report)
        s1 = self.b.finish_transfer(self.grant, self.b_token, self.oracle)
        s2 = self.b.finish_transfer(self.grant, self.b_token, self.oracle)
        self.assertEqual(s1, s2)
        self.assertEqual(s2['epoch'], 2)
        with self.assertRaises(C.CustodyDenied):
            self.b.finish_transfer(self.grant, secrets.token_hex(32), self.oracle)

    def test_competing_transfer_grant_denied(self):
        other = self.make_grant('Agent-C', transfer_id='handoff-2')
        self.b.begin_fence(self.grant, self.report)
        with self.assertRaises(C.CustodyDenied):
            self.b.begin_fence(other, self.report)

    def test_changed_stage2_digest_cannot_reuse_grant(self):
        changed = copy.deepcopy(self.report)
        changed['source']['dirty_paths'] = ['uncommitted.txt']
        with self.assertRaises(C.CustodyDenied):
            self.b.begin_fence(self.grant, changed)

    def test_parallel_promotion_cannot_generate_two_primaries(self):
        self.b.begin_fence(self.grant, self.report)
        new_b = C.LabGateway(self.db, self.key)
        token2 = secrets.token_hex(32)
        with ThreadPoolExecutor(max_workers=2) as pool:
            fa = pool.submit(self.b.finish_transfer, self.grant, self.b_token, self.oracle)
            fb = pool.submit(new_b.finish_transfer, self.grant, token2, self.oracle)
            outcomes = []
            for f in (fa, fb):
                try: outcomes.append(f.result()['holder'])
                except C.CustodyDenied: outcomes.append('DENIED')
        self.assertEqual(sorted(outcomes), ['Agent-B', 'DENIED'])
        self.assertEqual(self.b.read('LAB-R1')['epoch'], 2)

    def test_source_oracle_unavailable_does_not_promote(self):
        self.b.begin_fence(self.grant, self.report)
        def boom(): raise TimeoutError('offline')
        with self.assertRaises(C.CustodyDenied):
            self.b.finish_transfer(self.grant, self.b_token, boom)
        self.assertEqual(self.b.read('LAB-R1')['phase'], 'FENCING')

    def test_no_runner_self_approval_from_a_clean_stage2_report(self):
        # A clean source report alone NEVER calls begin_fence nor creates an epoch.
        C.valid_reconciliation(self.report, HEAD0, S1.digest(S1.canonical(self.report)))
        self.assertEqual(self.b.read('LAB-R1')['epoch'], 1)

    def test_audit_retains_fence_and_promotion_events(self):
        self.b.begin_fence(self.grant, self.report)
        self.b.finish_transfer(self.grant, self.b_token, self.oracle)
        self.assertEqual([e['event'] for e in self.b.audit_events('LAB-R1')],
                         ['BOOTSTRAP', 'FENCE_START', 'PROMOTED'])


if __name__ == '__main__':
    unittest.main()
