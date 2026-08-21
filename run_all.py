#!/usr/bin/env python3
"""Run the validated placebo gate, then the locked Claude confirmatory audit."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREREG_PATH = ROOT / "prereg.md"
CLAUDE_CONFIG_PATH = ROOT / "config" / "claude_confirmatory.yaml"
PLACEBO_MANIFEST_PATH = ROOT / "outputs" / "core_placebo" / "run_manifest.json"
PLACEBO_LOG_PATH = ROOT / "logs" / "placebo.log"

MODEL = "claude-sonnet-4-6"
TEMPERATURE = 0.0
EXPECTED_PLACEBO_ROWS = 640


def stop(message: str, code: int = 1) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return code


def run_with_log(command: list[str], log_path: Path) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log_file:
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="")
            log_file.write(line)
        return process.wait()


def validate_locked_configuration() -> None:
    if not PREREG_PATH.is_file():
        raise RuntimeError("prereg.md is missing; refusing to run.")
    if not CLAUDE_CONFIG_PATH.is_file():
        raise RuntimeError("config/claude_confirmatory.yaml is missing; refusing to run.")

    config_text = CLAUDE_CONFIG_PATH.read_text(encoding="utf-8")
    if f"model: {MODEL}" not in config_text:
        raise RuntimeError(f"Claude config is not locked to {MODEL}.")
    if f"temperatures: [{TEMPERATURE}]" not in config_text:
        raise RuntimeError(f"Claude config is not locked to temperature {TEMPERATURE}.")


def validate_placebo_manifest() -> None:
    if not PLACEBO_MANIFEST_PATH.is_file():
        raise RuntimeError("Placebo run did not create outputs/core_placebo/run_manifest.json.")

    manifest = json.loads(PLACEBO_MANIFEST_PATH.read_text(encoding="utf-8"))
    rows = manifest.get("rows")
    successful_rows = manifest.get("successful_rows")
    failed_rows = manifest.get("failed_rows")

    if rows != EXPECTED_PLACEBO_ROWS or successful_rows != EXPECTED_PLACEBO_ROWS:
        raise RuntimeError(
            "Placebo gate failed: expected 640/640 successful evaluations, "
            f"got {successful_rows}/{rows}."
        )
    if failed_rows != 0:
        raise RuntimeError(f"Placebo gate failed: expected 0 failures, got {failed_rows}.")


def main() -> int:
    try:
        validate_locked_configuration()
    except (OSError, RuntimeError) as exc:
        return stop(str(exc))

    print("Step 1/2: running the validated 640-evaluation placebo gate...")
    placebo_exit = run_with_log(
        ["bash", "scripts/reproduce_core_placebo.sh"],
        PLACEBO_LOG_PATH,
    )
    if placebo_exit != 0:
        return stop(
            f"Placebo command exited with status {placebo_exit}. "
            f"See {PLACEBO_LOG_PATH.relative_to(ROOT)}."
        )

    try:
        validate_placebo_manifest()
    except (OSError, json.JSONDecodeError, RuntimeError) as exc:
        return stop(str(exc))

    print(f"Placebo gate passed: 640/640. Log saved to {PLACEBO_LOG_PATH.relative_to(ROOT)}.")

    if not os.getenv("ANTHROPIC_API_KEY"):
        return stop(
            "ANTHROPIC_API_KEY is not set. Placebo passed, but the live audit was not started."
        )

    print(f"Step 2/2: starting locked live audit ({MODEL}, temperature={TEMPERATURE})...")
    live_env = os.environ.copy()
    live_env["ANTHROPIC_MODEL"] = MODEL
    live_result = subprocess.run(
        ["bash", "scripts/run_claude_confirmatory.sh"],
        cwd=ROOT,
        env=live_env,
        check=False,
    )
    if live_result.returncode != 0:
        return stop(f"Live audit exited with status {live_result.returncode}.")

    print("One-command audit pipeline complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
