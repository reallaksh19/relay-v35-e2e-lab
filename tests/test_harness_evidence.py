import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

PATH = Path(__file__).resolve().parents[1] / 'scripts/task_evidence.py'
SPEC = importlib.util.spec_from_file_location('lab_task_evidence', PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)

class EvidenceReportContract(unittest.TestCase):
    def make(self, tmp: Path, verdict: str = 'PASS', content: str = 'COMMAND=echo ok\nEXIT_CODE=0\n', **kwargs):
        log = tmp / 'commands.log'
        log.write_text(content)
        opts = dict(task='T00', verdict=verdict, operator='agent-session-test', expected='expected',
                    observed='observed', next='next', sha=None, issue=None, pr=None,
                    log=[str(log)], artifact=[], output=tmp/'evidence.md')
        opts.update(kwargs)
        return SimpleNamespace(**opts)

    def test_pass_with_zero_exit_and_local_hash(self):
        with TemporaryDirectory() as d:
            record = MOD.make_record(self.make(Path(d)))
            self.assertIn('TASK_EVIDENCE — T00 — PASS', record)
            self.assertIn('sha256:', record)
            self.assertIn('NOT_PUBLISHED_BY_THIS_LOCAL_GENERATOR', record)
            self.assertNotIn('P100/E100', record)

    def test_cannot_claim_pass_on_failing_log(self):
        with TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, 'nonzero EXIT_CODE'):
                MOD.make_record(self.make(Path(d), content='COMMAND=bad\nEXIT_CODE=1\n'))

    def test_expected_red_must_have_failing_exit(self):
        with TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, 'no nonzero EXIT_CODE'):
                MOD.make_record(self.make(Path(d), verdict='EXPECTED_RED'))
            record = MOD.make_record(self.make(Path(d), verdict='EXPECTED_RED', content='COMMAND=bad\nEXIT_CODE=1\n'))
            self.assertIn('EXPECTED_RED', record)
            self.assertIn('no broader V3.5 acceptance', record)

    def test_no_verified_claim_without_log(self):
        with TemporaryDirectory() as d:
            a = self.make(Path(d), log=[])
            with self.assertRaisesRegex(ValueError, 'log is required'):
                MOD.make_record(a)

    def test_wrong_or_missing_artifact_rejected(self):
        with TemporaryDirectory() as d:
            a = self.make(Path(d), artifact=[str(Path(d)/'missing.json')])
            with self.assertRaisesRegex(ValueError, 'missing evidence artifact'):
                MOD.make_record(a)

    def test_invalid_material_sha_refused(self):
        with TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, 'SHA must be full'):
                MOD.make_record(self.make(Path(d), sha='123'))

if __name__ == '__main__':
    unittest.main()
