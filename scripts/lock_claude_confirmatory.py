#!/usr/bin/env python3
"""Create a prospective SHA-256 lock for the Claude confirmatory audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

LOCKED_FILES = (
    "docs/claude_confirmatory_protocol.md",
    "docs/core_audit_preregistration.md",
    "docs/power_analysis.md",
    "docs/treatment_construction.md",
    "config/claude_confirmatory.yaml",
    ".github/workflows/claude-confirmatory.yml",
    "pyproject.toml",
    "requirements-lock.txt",
    "src/compas_audit/prompts.py",
    "src/compas_audit/providers.py",
    "src/compas_audit/run_audit.py",
    "src/compas_audit/core_analysis.py",
    "src/compas_audit/manipulation.py",
    "src/compas_audit/generate.py",
    "scripts/lock_claude_confirmatory.py",
    "scripts/run_claude_confirmatory.sh",
    "scripts/run_claude_prompt_robustness.sh",
    "scripts/make_core_result_figure.py",
    "scripts/summarize_prompt_robustness.py",
    "data/templates/resume_templates.csv",
    "outputs/claude_confirmatory/resume_permutations.csv",
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create the prospective Claude confirmatory code/design lock."
    )
    parser.add_argument(
        "--output",
        default="docs/claude_confirmatory_design_lock.json",
    )
    args = parser.parse_args()

    missing = [item for item in LOCKED_FILES if not Path(item).exists()]
    if missing:
        raise FileNotFoundError(f"Missing files required for the design lock: {missing}")

    payload = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "prospectively_code_locked",
        "external_registration_url": None,
        "externally_preregistered": False,
        "study_phase": "claude_confirmatory_execution_extension",
        "exact_model_id": "claude-sonnet-4-6",
        "historical_versions_modified": False,
        "pilot_outcomes_permitted_to_change_design": False,
        "files": {item: sha256_file(Path(item)) for item in LOCKED_FILES},
    }
    output = Path(args.output)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({payload['status']})")


if __name__ == "__main__":
    main()
