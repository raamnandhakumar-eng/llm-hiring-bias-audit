#!/usr/bin/env bash
set -euo pipefail

: "${EXTERNAL_PREREGISTRATION_URL:?Set the permanent preregistration URL before the pilot.}"
: "${GEMINI_API_KEY:?Set GEMINI_API_KEY before the pilot.}"
: "${GEMINI_MODEL:?Set GEMINI_MODEL before the pilot.}"

if [[ "${GEMINI_MODEL}" != "gemini-2.5-flash" ]]; then
  echo "Gemini pilot is locked to gemini-2.5-flash; received ${GEMINI_MODEL}." >&2
  exit 1
fi

if [[ -e outputs/gemini_pilot/screening_results.csv ]] || \
   [[ -e outputs/gemini_pilot/run_manifest.json ]]; then
  echo "Refusing to overwrite an existing Gemini pilot attempt." >&2
  exit 1
fi

python scripts/lock_claude_confirmatory.py \
  --registration-url "${EXTERNAL_PREREGISTRATION_URL}"
hiring-audit-generate --config config/claude_confirmatory.yaml
hiring-audit-run-gemini-pilot --config config/claude_confirmatory.yaml

echo "Gemini feasibility pilot complete. Do not use pilot outcomes to alter the Claude design."
