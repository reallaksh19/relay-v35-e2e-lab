#!/usr/bin/env bash
set -euo pipefail
COMMON="${1:-../Common}"
EXPECTED='13989969f6b7e432c4f7c1ddfe975449dba53593'
[[ -f .relay/graph.yaml ]] || { echo 'First run bash scripts/bootstrap_lab.sh' >&2; exit 2; }
[[ -f "$COMMON/skills/engineering-pr-delivery-v3.2/scripts/delp_projection_v32.py" ]] || {
  echo "Common checkout missing: $COMMON" >&2; exit 2;
}
ACTUAL="$(git -C "$COMMON" rev-parse HEAD)"
[[ "$ACTUAL" == "$EXPECTED" ]] || { echo "Common basis drift: $ACTUAL != $EXPECTED" >&2; exit 2; }
DELP="$COMMON/skills/engineering-pr-delivery-v3.2/scripts/delp_projection_v32.py"
python3 "$DELP" validate-graph --graph .relay/graph.yaml
python3 "$DELP" decompose-check --graph .relay/graph.yaml --mode ENFORCED
python3 "$DELP" project --graph .relay/graph.yaml --output .relay/projection.json
printf '\nBaseline DELP projection generated at .relay/projection.json (not Owner or review acceptance).\n'
