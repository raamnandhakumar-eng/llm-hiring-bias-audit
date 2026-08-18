#!/usr/bin/env bash
set -euo pipefail

: "${ANTHROPIC_API_KEY:?Set ANTHROPIC_API_KEY before the live run.}"
: "${ANTHROPIC_MODEL:?Set ANTHROPIC_MODEL before the live run.}"

if [[ "${ANTHROPIC_MODEL}" != "claude-sonnet-4-6" ]]; then
  echo "Claude confirmatory program is locked to claude-sonnet-4-6; received ${ANTHROPIC_MODEL}." >&2
  exit 1
fi

if [[ ! -s docs/claude_confirmatory_design_lock.json ]]; then
  echo "Claude design lock is missing; robustness runs require the same prospective lock as the primary run." >&2
  exit 1
fi

for prompt_version in v2.0-concise v2.0-rubric; do
  label="${prompt_version#v2.0-}"
  results_path="outputs/claude_confirmatory/prompt_robustness/${label}/screening_results.csv"
  manifest_path="outputs/claude_confirmatory/prompt_robustness/${label}/run_manifest.json"
  analysis_path="outputs/claude_confirmatory/prompt_robustness/${label}/analysis"
  if [[ -e "${results_path}" ]]; then
    echo "Refusing to overwrite ${results_path}. Record a deviation before any rerun." >&2
    exit 1
  fi
  hiring-audit-run \
    --config config/claude_confirmatory.yaml \
    --provider anthropic \
    --prompt-version "${prompt_version}" \
    --trials 5 \
    --results-path "${results_path}" \
    --manifest-path "${manifest_path}"
  hiring-audit-analyze-core \
    --input "${results_path}" \
    --output-dir "${analysis_path}"
done

python scripts/summarize_prompt_robustness.py \
  --core-dir outputs/claude_confirmatory \
  --output-dir outputs/claude_confirmatory/prompt_robustness
