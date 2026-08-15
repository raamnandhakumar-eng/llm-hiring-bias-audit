#!/usr/bin/env python3
"""Hash the prospective design files before external preregistration."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

LOCKED_FILES = (
    "docs/osf_preregistration.md",
    "docs/core_audit_preregistration.md",
    "docs/power_analysis.md",
    "docs/treatment_construction.md",
    "config/core_audit.yaml",
    "src/compas_audit/prompts.py",
    "data/templates/resume_templates.csv",
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def valid_registration_url(url: str) -> bool:
    parsed = urlparse(url)
    host = (parsed.hostname or "").casefold()
    return parsed.scheme == "https" and any(
        host == accepted or host.endswith(f".{accepted}")
        for accepted in ("osf.io", "aspredicted.org")
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a preregistration file lock.")
    parser.add_argument("--output", default="docs/preregistration_lock.json")
    parser.add_argument("--registration-url", default="")
    args = parser.parse_args()
    if args.registration_url and not valid_registration_url(args.registration_url):
        raise ValueError("Registration URL must be a permanent OSF or AsPredicted HTTPS URL.")
    missing = [item for item in LOCKED_FILES if not Path(item).exists()]
    if missing:
        raise FileNotFoundError(f"Missing files required for the design lock: {missing}")
    payload = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "externally_registered" if args.registration_url else "prepared_not_submitted",
        "external_registration_url": args.registration_url or None,
        "files": {item: sha256_file(Path(item)) for item in LOCKED_FILES},
    }
    output = Path(args.output)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({payload['status']})")


if __name__ == "__main__":
    main()
