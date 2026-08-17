#!/usr/bin/env bash
set -euo pipefail

: "${EXTERNAL_PREREGISTRATION_URL:?Submit the external registration and set its permanent URL.}"
: "${GEMINI_API_KEY:?Set GEMINI_API_KEY before the live run.}"
: "${GEMINI_MODEL:?Set GEMINI_MODEL to the exact model ID.}"

protected_outputs=(
  outputs/core/screening_results.csv
  outputs/core/manipulation_checks.csv
  outputs/core/prompt_robustness/concise/screening_results.csv
  outputs/core/prompt_robustness/rubric/screening_results.csv
)
for protected_output in "${protected_outputs[@]}"; do
  if [[ -e "${protected_output}" ]]; then
    echo "Refusing to overwrite ${protected_output}." >&2
    echo "Preserve every live attempt and record any restart as a deviation." >&2
    exit 1
  fi
done

python scripts/power_analysis.py
python scripts/audit_resume_balance.py
python scripts/lock_preregistration.py \
  --registration-url "${EXTERNAL_PREREGISTRATION_URL}"
hiring-audit-generate --config config/core_audit.yaml
hiring-audit-run-gemini --config config/core_audit.yaml
hiring-audit-analyze-core \
  --input outputs/core/screening_results.csv \
  --output-dir outputs/core/analysis
python scripts/make_core_result_figure.py

# Manipulation checks run only after every primary observation has been attempted.
hiring-audit-manipulation-check-gemini --config config/core_audit.yaml

bash scripts/run_gemini_prompt_robustness.sh

echo "Gemini primary live program complete. Preserve outputs/core before interpretation."
