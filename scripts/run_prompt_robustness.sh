#!/usr/bin/env bash
set -euo pipefail

: "${EXTERNAL_PREREGISTRATION_URL:?Set the permanent preregistration URL.}"
: "${ANTHROPIC_API_KEY:?Set ANTHROPIC_API_KEY before the live run.}"
: "${ANTHROPIC_MODEL:?Set ANTHROPIC_MODEL to the exact model ID.}"

for prompt_version in v2.0-concise v2.0-rubric; do
  label="${prompt_version#v2.0-}"
  results_path="outputs/core/prompt_robustness/${label}/screening_results.csv"
  manifest_path="outputs/core/prompt_robustness/${label}/run_manifest.json"
  analysis_path="outputs/core/prompt_robustness/${label}/analysis"
  if [[ -e "${results_path}" ]]; then
    echo "Refusing to overwrite ${results_path}. Record a deviation before any rerun." >&2
    exit 1
  fi
  hiring-audit-run \
    --config config/core_audit.yaml \
    --provider anthropic \
    --prompt-version "${prompt_version}" \
    --trials 5 \
    --results-path "${results_path}" \
    --manifest-path "${manifest_path}"
  hiring-audit-analyze-core \
    --input "${results_path}" \
    --output-dir "${analysis_path}"
done

python scripts/summarize_prompt_robustness.py
