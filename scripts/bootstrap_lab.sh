#!/usr/bin/env bash
# One-shot, fail-closed GitHub PRIVATE lab bootstrap. Human/local-agent invoked only.
set -euo pipefail
REPO="${1:-reallaksh19/relay-v35-e2e-lab}"
if [[ "$REPO" != "reallaksh19/relay-v35-e2e-lab" ]]; then
  echo "refusing non-lab/production OWNER/REPO: expected reallaksh19/relay-v35-e2e-lab" >&2; exit 2
fi
for tool in gh git python3; do command -v "$tool" >/dev/null || { echo "$tool is required" >&2; exit 2; }; done
python3 -c 'import yaml' || { echo 'PyYAML is required' >&2; exit 2; }
[[ ! -e .relay/issue-map.json ]] || { echo 'issue-map already exists; refusing duplicate bootstrap' >&2; exit 2; }
[[ -f docs/owner-intent.md ]] && grep -q 'SYNTHETIC' docs/owner-intent.md || {
  echo 'synthetic lab Owner prompt missing; refusing' >&2; exit 2;
}
gh auth status >/dev/null || { echo 'gh login is required' >&2; exit 2; }
# Refuse ambiguous existing repositories and partially completed issue creation.
if gh repo view "$REPO" --json name >/dev/null 2>&1; then
  [[ "$(gh repo view "$REPO" --json isPrivate -q '.isPrivate')" == true ]] || {
    echo 'existing repo is NOT PRIVATE; refusing' >&2; exit 2;
  }
  # Existing repo might have been created by an interrupted previous run.
  # Never mint a second set of R0/R1/R2 or overwrite untracked refs.
  if [[ -n "$(gh issue list --repo "$REPO" --state all --limit 100 --json title --jq '.[] | select(.title | startswith("[LAB/R")) | .title')" ]]; then
    echo 'lab already contains managed R0/R1/R2 issues; reconcile manually, do not recreate' >&2; exit 2;
  fi
  echo 'Private lab repo exists; initial content must be inspected before using this bootstrap.' >&2
  exit 2
fi
[[ ! -d .git ]] || { echo 'repository has local Git history; inspect before one-shot bootstrap' >&2; exit 2; }
[[ ! -e .relay/graph.yaml ]] || { echo 'generated graph present; reconcile previous setup first' >&2; exit 2; }
git init -b main
git add .
git commit -m 'chore(lab): declare intentionally RED inventory lifecycle baseline'
gh repo create "$REPO" --private --source=. --remote=origin --push
# Persistent marker identifies an interrupted operation; it must be reconciled,
# never removed and replayed blindly if GitHub issue creation partially succeeds.
mkdir -p .relay
printf '%s\n' 'CREATED_PRIVATE_REPO_ISSUES_PENDING' > .relay/bootstrap-state.txt
PARENT_URL=$(gh issue create --repo "$REPO" \
  --title '[LAB/R0] Synthetic Owner programme — inventory lifecycle' \
  --body-file docs/owner-intent.md)
printf '%s\n' "PARENT_URL=$PARENT_URL" >> .relay/bootstrap-state.txt
PARSER_URL=$(gh issue create --repo "$REPO" \
  --title '[LAB/R1] Strict CSV parser and validation · U01–U03' \
  --body "Parent: $PARENT_URL
Responsibility: strict CSV parsing and validation; 3 units 35/35/30; only parser and parser-tests paths. Publish TASK_EVIDENCE with real PR HEAD and CI, never hand-computed P/E. Simulate agent interruption after U02; new agent retains this issue. No automatic merge.")
printf '%s\n' "PARSER_URL=$PARSER_URL" >> .relay/bootstrap-state.txt
REPORT_URL=$(gh issue create --repo "$REPO" \
  --title '[LAB/R2] Decimal inventory JSON report · U01–U03' \
  --body "Parent: $PARENT_URL
Depends on: $PARSER_URL
Responsibility: deterministic Decimal report and CLI; 3 units 35/35/30; only reporter, CLI, report-tests paths. Evidence must bind current head and accepted result. No automatic merge.")
printf '%s\n' "REPORT_URL=$REPORT_URL" >> .relay/bootstrap-state.txt
PARENT="${PARENT_URL##*/}"; PARSER="${PARSER_URL##*/}"; REPORT="${REPORT_URL##*/}"
python3 scripts/generate_graph.py --repository "$REPO" \
  --parent "$PARENT" --parser "$PARSER" --report "$REPORT" --output .relay/graph.yaml
python3 - "$REPO" "$PARENT" "$PARSER" "$REPORT" <<'PY'
import json, pathlib, sys
repo, parent, parser, report = sys.argv[1:]
pathlib.Path('.relay/issue-map.json').write_text(json.dumps({
  'repository': repo, 'parent_issue': int(parent),
  'parser_issue': int(parser), 'report_issue': int(report),
  'parser_pr': None, 'report_pr': None, 'programme_acceptance': 'NOT_PROVEN',
  'owner_source_authentication': 'SYNTHETIC_LAB_ONLY', 'live_writer': 'OFF',
}, sort_keys=True, indent=2)+'\n')
PY
printf '%s\n' 'ISSUES_CREATED_GRAPH_READY' >> .relay/bootstrap-state.txt
git add .relay/graph.yaml .relay/issue-map.json .relay/bootstrap-state.txt
git commit -m 'test(lab): bind real GitHub issue identities to DELP graph'
git push origin HEAD:main
printf 'DONE_GITHUB_INITIALIZED\nParent: %s\nParser: %s\nReport: %s\n' "$PARENT_URL" "$PARSER_URL" "$REPORT_URL"
printf 'NEXT: run bash scripts/run_baseline.sh ../Common; preserve expected RED app tests.\n'
