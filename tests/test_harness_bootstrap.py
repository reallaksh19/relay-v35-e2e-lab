"""Exercise the REAL bootstrap shell against hermetic gh/git commands.

Simulation proves local fail-closed control flow only: it does not certify
GitHub privacy, provider readback, CI, a code PR, or DELP integration.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
REPO = "reallaksh19/relay-v35-e2e-lab"

MOCK_GH = r'''#!/usr/bin/env python3
import json, os, pathlib, sys
p = pathlib.Path(os.environ['LAB_GH_MOCK_STATE'])
s = json.loads(p.read_text())
a = sys.argv[1:]

def flush(): p.write_text(json.dumps(s, sort_keys=True))

if a[:2] == ['auth', 'status']:
    sys.exit(0 if s.get('authenticated', True) else 1)
if a[:2] == ['repo', 'view']:
    if not s.get('repo_exists'): sys.exit(1)
    if 'isPrivate' in a: print('true' if s.get('private') else 'false')
    else: print('{"name":"relay-v35-e2e-lab"}')
    sys.exit(0)
if a[:2] == ['repo', 'create']:
    if '--private' not in a or not '--source=.' in a or not '--push' in a:
        print('missing private/source/push', file=sys.stderr); sys.exit(2)
    if s.get('repo_exists'): sys.exit(1)
    s['repo_exists'],s['private']=True,True
    s['create_invocations']=s.get('create_invocations',0)+1
    flush(); print('PRIVATE_REPOSITORY_CREATED_MOCK'); sys.exit(0)
if a[:2] == ['issue', 'create']:
    if not s.get('repo_exists'): sys.exit(1)
    if s.get('fail_issue_ordinal') == s.get('issue_invocations',0)+1:
        print('INJECTED_ISSUE_CREATE_FAILURE',file=sys.stderr);sys.exit(42)
    s['issue_invocations']=s.get('issue_invocations',0)+1
    n=s['issue_invocations']+10
    s.setdefault('issue_ids',[]).append(n)
    flush(); print('https://github.com/'+os.environ['LAB_MOCK_REPO']+'/issues/'+str(n));sys.exit(0)
if a[:2] == ['issue', 'list']:
    if s.get('issue_ids'): print('[LAB/R0] Synthetic Owner')
    sys.exit(0)
print('unsupported gh mock invocation '+repr(a),file=sys.stderr);sys.exit(99)
'''

MOCK_GIT = r'''#!/usr/bin/env python3
import os, pathlib, sys
args=sys.argv[1:]
if args[:2] == ['init','-b']:
    pathlib.Path('.git').mkdir(exist_ok=True);sys.exit(0)
if args and args[0] in ('add','commit','push'):
    sys.exit(0)
print('unsupported git mock invocation '+repr(args),file=sys.stderr);sys.exit(99)
'''


class BootstrapMockBoundary(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='relay-v35-lab-t01-')
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)
        self.work = self.dir / 'work'
        shutil.copytree(ROOT, self.work, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        for stale in (self.work/'.relay/graph.yaml', self.work/'.relay/issue-map.json', self.work/'.relay/bootstrap-state.txt'):
            if stale.exists(): stale.unlink()
        self.bin = self.dir / 'bin'
        self.bin.mkdir()
        for name,code in [('gh',MOCK_GH),('git',MOCK_GIT)]:
            p=self.bin/name
            p.write_text(code)
            p.chmod(0o700)
        self.statefile=self.dir/'state.json'
        self.statefile.write_text('{}')
        self.env=os.environ.copy()
        self.env.update(PATH=str(self.bin)+os.pathsep+os.environ['PATH'],LAB_GH_MOCK_STATE=str(self.statefile),LAB_MOCK_REPO=REPO)

    def set_state(self,**fields):
        s=json.loads(self.statefile.read_text()); s.update(fields)
        self.statefile.write_text(json.dumps(s))

    def state(self): return json.loads(self.statefile.read_text())

    def run_bootstrap(self,repo=REPO):
        return subprocess.run(['bash','scripts/bootstrap_lab.sh',repo], cwd=self.work,
                              env=self.env,capture_output=True,text=True,timeout=15)

    def test_one_shot_private_happy_path_assigns_actual_issue_numbers(self):
        p=self.run_bootstrap()
        self.assertEqual(0,p.returncode,(p.stdout,p.stderr))
        state=self.state()
        self.assertTrue(state['private'])
        self.assertEqual([11,12,13],state['issue_ids'])
        self.assertEqual(1,state['create_invocations'])
        self.assertIn('DONE_GITHUB_INITIALIZED',p.stdout)
        issue_map=json.loads((self.work/'.relay/issue-map.json').read_text())
        self.assertEqual((11,12,13),(issue_map['parent_issue'],issue_map['parser_issue'],issue_map['report_issue']))
        self.assertEqual('OFF',issue_map['live_writer'])
        import yaml
        graph=yaml.safe_load((self.work/'.relay/graph.yaml').read_text())
        self.assertEqual(REPO,graph['programme']['repository'])
        self.assertEqual(['relay-v35-e2e-lab#11','relay-v35-e2e-lab#12','relay-v35-e2e-lab#13'],[n['ref'] for n in graph['nodes']])
        self.assertEqual(['relay-v35-e2e-lab#12'],graph['nodes'][2]['depends_on'])
        self.assertEqual([35,35,30],[u['weight'] for u in graph['nodes'][1]['units']])
        self.assertIn('ISSUES_CREATED_GRAPH_READY',(self.work/'.relay/bootstrap-state.txt').read_text())

    def test_rerun_cannot_duplicate_issues_after_success(self):
        first=self.run_bootstrap()
        self.assertEqual(0,first.returncode,(first.stdout,first.stderr))
        again=self.run_bootstrap()
        self.assertNotEqual(0,again.returncode)
        self.assertEqual([11,12,13],self.state()['issue_ids'])
        self.assertEqual(1,self.state()['create_invocations'])

    def test_interrupted_child_issue_creation_blocks_retry(self):
        self.set_state(fail_issue_ordinal=2)
        first=self.run_bootstrap()
        self.assertNotEqual(0,first.returncode)
        self.assertIn('INJECTED_ISSUE_CREATE_FAILURE',first.stderr)
        self.assertEqual([11],self.state()['issue_ids'])
        self.assertIn('PARENT_URL=',(self.work/'.relay/bootstrap-state.txt').read_text())
        again=self.run_bootstrap()
        self.assertNotEqual(0,again.returncode)
        self.assertEqual([11],self.state()['issue_ids'])
        self.assertEqual(1,self.state()['create_invocations'])

    def test_existing_private_or_public_repo_never_reused_without_reconcile(self):
        for is_private in (False,True):
            with self.subTest(private=is_private):
                self.set_state(repo_exists=True,private=is_private)
                result=self.run_bootstrap()
                self.assertNotEqual(0,result.returncode)
                self.assertEqual(0,self.state().get('issue_invocations',0))
                self.assertEqual(0,self.state().get('create_invocations',0))

    def test_refuse_prod_repository_before_any_repo_action(self):
        result=self.run_bootstrap('reallaksh19/Common')
        self.assertNotEqual(0,result.returncode)
        self.assertIn('refusing non-lab/production',result.stderr)
        self.assertEqual({},self.state())

    def test_refuse_alternative_repository_before_any_repo_action(self):
        result=self.run_bootstrap('reallaksh19/3D_Converters')
        self.assertNotEqual(0,result.returncode)
        self.assertIn('refusing non-lab/production',result.stderr)
        self.assertEqual({},self.state())

    def test_missing_gh_auth_denies_without_side_effect(self):
        self.set_state(authenticated=False)
        result=self.run_bootstrap()
        self.assertNotEqual(0,result.returncode)
        self.assertEqual(0,self.state().get('create_invocations',0))
        self.assertEqual(0,self.state().get('issue_invocations',0))


if __name__ == '__main__': unittest.main()
