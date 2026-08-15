#!/usr/bin/env bash
set -euo pipefail

hiring-audit-generate --config config/core_audit.yaml
hiring-audit-run \
  --config config/core_audit.yaml \
  --provider mock \
  --results-path outputs/core_placebo/screening_results.csv \
  --manifest-path outputs/core_placebo/run_manifest.json
hiring-audit-analyze-core \
  --input outputs/core_placebo/screening_results.csv \
  --output-dir outputs/core_placebo/analysis

echo "Core placebo reproduced under outputs/core_placebo/."
