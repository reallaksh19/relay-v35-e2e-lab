import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

p = Path(__file__).resolve().parents[1]/'scripts'/'verify_github_comment.py'
spec = importlib.util.spec_from_file_location('comment_readback',p)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class GitHubReadback(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/'draft.md'
        self.path.write_text('## TASK_EVIDENCE — T00 — PASS\nExact-source proof\n')

    def tearDown(self):
        self.tmp.cleanup()

    def response(self, **kwargs):
        raw = {'html_url':'https://github.com/reallaksh19/Common/issues/875#issuecomment-234',
               'issue_url':'https://api.github.com/repos/reallaksh19/Common/issues/875',
               'body':self.path.read_text(),'user':{'login':'authorized-local-agent'}}
        raw.update(kwargs)
        return subprocess.CompletedProcess(['gh','api'],0,json.dumps(raw),'')

    def test_exact_body_and_issue_provider_get(self):
        with patch.object(module.subprocess,'run',return_value=self.response()) as mock:
            result=module.verify(234,self.path,expected_author='authorized-local-agent')
        self.assertTrue(result['body_match'])
        self.assertFalse(result['principal_authenticated_for_reviewer'])
        self.assertIn('repos/reallaksh19/Common/issues/comments/234',mock.call_args.args[0][2])

    def test_wrong_body_fails(self):
        with patch.object(module.subprocess,'run',return_value=self.response(body='FORGED')):
            with self.assertRaisesRegex(ValueError,'body differs'):
                module.verify(234,self.path)

    def test_wrong_issue_fails(self):
        with patch.object(module.subprocess,'run',return_value=self.response(issue_url='https://api.github.com/repos/reallaksh19/Common/issues/877')):
            with self.assertRaisesRegex(ValueError,'target issue mismatch'):
                module.verify(234,self.path)

    def test_wrong_author_fails(self):
        with patch.object(module.subprocess,'run',return_value=self.response()):
            with self.assertRaisesRegex(ValueError,'author mismatch'):
                module.verify(234,self.path,expected_author='other')

    def test_failed_provider_get_never_claims_readback(self):
        with patch.object(module.subprocess,'run',side_effect=subprocess.CalledProcessError(1,['gh'])):
            with self.assertRaisesRegex(ValueError,'GET failed'):
                module.verify(234,self.path)


if __name__=='__main__':
    unittest.main()
