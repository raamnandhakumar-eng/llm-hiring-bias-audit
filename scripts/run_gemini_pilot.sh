#!/usr/bin/env bash
set -euo pipefail

: "${GEMINI_API_KEY:?Set GEMINI_API_KEY before the pilot.}"
: "${GEMINI_MODEL:?Set GEMINI_MODEL before the pilot.}"

if [[ "${GEMINI_MODEL}" != "gemini-3.6-flash" ]]; then
  echo "Gemini pilot is locked to gemini-3.6-flash; received ${GEMINI_MODEL}." >&2
  exit 1
fi

if [[ -e outputs/gemini_pilot/screening_results.csv ]] || \
   [[ -e outputs/gemini_pilot/run_manifest.json ]]; then
  echo "Refusing to overwrite an existing Gemini pilot attempt." >&2
  exit 1
fi

# Freeze a local hash of the Claude confirmatory design before observing pilot output.
# External preregistration remains required only for the later Claude confirmatory run.
python scripts/lock_claude_confirmatory.py
hiring-audit-generate --config config/claude_confirmatory.yaml
hiring-audit-run-gemini-pilot --config config/claude_confirmatory.yaml

echo "Gemini feasibility pilot complete. Do not use pilot outcomes to alter the Claude design."
