#!/usr/bin/env bash
set -euo pipefail

: "${ANTHROPIC_API_KEY:?Set ANTHROPIC_API_KEY before the confirmatory run.}"
: "${ANTHROPIC_MODEL:?Set ANTHROPIC_MODEL before the confirmatory run.}"

if [[ "${ANTHROPIC_MODEL}" != "claude-sonnet-4-6" ]]; then
  echo "Claude confirmatory audit is locked to claude-sonnet-4-6; received ${ANTHROPIC_MODEL}." >&2
  exit 1
fi

protected_outputs=(
  outputs/claude_confirmatory/screening_results.csv
  outputs/claude_confirmatory/manipulation_checks.csv
  outputs/claude_confirmatory/prompt_robustness/concise/screening_results.csv
  outputs/claude_confirmatory/prompt_robustness/rubric/screening_results.csv
)
for protected_output in "${protected_outputs[@]}"; do
  if [[ -e "${protected_output}" ]]; then
    echo "Refusing to overwrite ${protected_output}." >&2
    echo "Preserve every live attempt and record any restart as a deviation." >&2
    exit 1
  fi
done

# Create the prospective SHA-256 design lock before any Claude API request.
python scripts/lock_claude_confirmatory.py

if [[ ! -s docs/claude_confirmatory_design_lock.json ]]; then
  echo "Claude confirmatory design lock was not created." >&2
  exit 1
fi

hiring-audit-generate --config config/claude_confirmatory.yaml

hiring-audit-run \
  --config config/claude_confirmatory.yaml \
  --provider anthropic

hiring-audit-analyze-core \
  --input outputs/claude_confirmatory/screening_results.csv \
  --output-dir outputs/claude_confirmatory/analysis

python scripts/make_core_result_figure.py \
  --input outputs/claude_confirmatory/analysis/core_effect_sizes.csv \
  --output outputs/claude_confirmatory/analysis/claude_treatment_effects.svg

# Run only after all 640 primary Claude observations have been attempted.
hiring-audit-manipulation-check \
  --config config/claude_confirmatory.yaml \
  --provider anthropic

bash scripts/run_claude_prompt_robustness.sh

echo "Claude confirmatory program complete. Preserve outputs/claude_confirmatory before interpretation."
