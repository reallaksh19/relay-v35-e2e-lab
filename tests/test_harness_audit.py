import argparse
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import importlib.util

SOURCE = Path(__file__).resolve().parents[1] / 'scripts' / 'audit_trail.py'
spec = importlib.util.spec_from_file_location('audit_under_test', SOURCE)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class AuditChain(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.prev = Path.cwd()
        from os import chdir
        chdir(self.tmp.name)
        Path('evidence/logs').mkdir(parents=True)
        self.artifact = Path('evidence/logs/output.log')
        self.artifact.write_text('COMMAND=python3 -m unittest\nEXIT_CODE=0\n')
        self.ledger = Path('evidence/audit/events.jsonl')

    def tearDown(self):
        from os import chdir
        chdir(self.prev)
        self.tmp.cleanup()

    def args(self, **overrides):
        data = dict(ledger=self.ledger, task='T00', event='TASK_EVIDENCE_DRAFTED',
                    verdict='PASS', actor='separate-local-agent-01', source_sha='UNKNOWN',
                    github_url=None, artifact=[self.artifact], note='Observed harness source read')
        data.update(overrides)
        return argparse.Namespace(**data)

    def test_append_verify_two_records(self):
        one = audit.append(self.args())
        two = audit.append(self.args(task='T01-PREFLIGHT', event='TASK_STARTED', verdict='UNKNOWN'))
        self.assertEqual(1, one['sequence'])
        self.assertEqual(one['event_hash'], two['previous_hash'])
        self.assertEqual(2, len(audit.read_records(self.ledger)))

    def test_mutated_record_detected(self):
        audit.append(self.args())
        raw = self.ledger.read_text().replace('PASS', 'FAIL', 1)
        self.ledger.write_text(raw)
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            audit.read_records(self.ledger)

    def test_mutated_artifact_detected(self):
        audit.append(self.args())
        self.artifact.write_text('COMMAND=wrong\nEXIT_CODE=9\n')
        with self.assertRaisesRegex(ValueError, 'artifact changed'):
            audit.read_records(self.ledger)

    def test_missing_artifact_detected(self):
        audit.append(self.args())
        self.artifact.unlink()
        with self.assertRaisesRegex(ValueError, 'artifact not found'):
            audit.read_records(self.ledger)

    def test_publication_requires_exact_comment_url(self):
        with self.assertRaisesRegex(ValueError, 'exact GitHub comment'):
            audit.append(self.args(event='GITHUB_READBACK_VERIFIED'))
        with self.assertRaisesRegex(ValueError, 'exact GitHub comment'):
            audit.append(self.args(event='GITHUB_PUBLISHED', github_url='https://github.com/reallaksh19/Common/issues/875'))
        good = audit.append(self.args(event='GITHUB_READBACK_VERIFIED',
                                      github_url='https://github.com/reallaksh19/Common/issues/875#issuecomment-123456'))
        self.assertEqual('GITHUB_READBACK_VERIFIED', good['event'])

    def test_lock_refuses_concurrent_writer(self):
        self.ledger.parent.mkdir(parents=True)
        self.ledger.with_suffix('.jsonl.lock').write_text('locked')
        with self.assertRaisesRegex(ValueError, 'ledger lock exists'):
            audit.append(self.args())
        self.assertFalse(self.ledger.exists())

    def test_traversal_and_invalid_sha_rejected(self):
        with self.assertRaisesRegex(ValueError, 'within evidence'):
            audit.append(self.args(artifact=[Path('../secret.txt')]))
        with self.assertRaisesRegex(ValueError, 'source SHA'):
            audit.append(self.args(source_sha='a'*39))
        with self.assertRaisesRegex(ValueError, 'GitHub source URL'):
            audit.append(self.args(github_url='https://example.org/evil'))

    def test_reordered_records_detected(self):
        audit.append(self.args())
        audit.append(self.args(task='T01', verdict='BLOCKED'))
        records = self.ledger.read_text().splitlines()
        self.ledger.write_text('\n'.join(reversed(records)) + '\n')
        with self.assertRaisesRegex(ValueError, 'sequence or predecessor'):
            audit.read_records(self.ledger)


if __name__ == '__main__':
    unittest.main()
