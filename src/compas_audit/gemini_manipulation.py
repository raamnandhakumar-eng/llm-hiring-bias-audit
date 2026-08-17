from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from .common import extract_json_object, load_config, sha256_text, stable_id
from .manipulation import summarize_manipulation_checks, validate_manipulation_response
from .prompts import MANIPULATION_PROMPT_VERSION, SYSTEM_PROMPT, manipulation_prompt
from .providers import GeminiProvider
from .run_audit import require_external_preregistration


def run_gemini_manipulation_checks(
    config_path: str,
    resume_limit: int | None = None,
) -> pd.DataFrame:
    config = load_config(config_path)
    settings = config.get("manipulation_checks", {})
    if not bool(settings.get("enabled", True)):
        raise RuntimeError("Manipulation checks are disabled in the configuration.")

    registration_url = require_external_preregistration(config)
    resume_path = Path(config["output_resumes"])
    if not resume_path.exists():
        raise FileNotFoundError(
            f"Resume permutations not found: {resume_path}. Run generation first."
        )

    seed = int(config.get("seed", 42))
    resumes = (
        pd.read_csv(resume_path)
        .sample(frac=1, random_state=seed + 13)
        .reset_index(drop=True)
    )
    if resume_limit is not None:
        resumes = resumes.head(resume_limit)

    provider = GeminiProvider(model_name="set-via-GEMINI_MODEL-before-live-run")
    max_tokens = int(settings.get("max_tokens", 250))
    delay = float(config.get("provider", {}).get("request_delay_seconds", 0.0))
    records: list[dict[str, Any]] = []

    for execution_order, resume in resumes.iterrows():
        prompt = manipulation_prompt(
            str(resume["target_role"]),
            str(resume["resume_text"]),
        )
        observation_id = stable_id(
            resume["resume_id"],
            provider.model_name,
            MANIPULATION_PROMPT_VERSION,
        )
        started = time.perf_counter()
        timestamp = datetime.now(timezone.utc)
        raw_response = ""
        error = ""
        parsed: dict[str, Any] = {}
        try:
            raw_response = provider.screen(
                SYSTEM_PROMPT,
                prompt,
                0.0,
                max_tokens,
                run_key=observation_id,
            )
            parsed = validate_manipulation_response(extract_json_object(raw_response))
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"

        records.append(
            {
                **resume.to_dict(),
                "observation_id": observation_id,
                "execution_order": int(execution_order) + 1,
                "provider": "gemini",
                "exact_model_id": provider.model_name,
                "prompt_version": MANIPULATION_PROMPT_VERSION,
                "external_preregistration_url": registration_url,
                "timestamp_utc": timestamp.isoformat(),
                "prompt_sha256": sha256_text(SYSTEM_PROMPT + "\n" + prompt),
                "latency_seconds": round(time.perf_counter() - started, 4),
                **parsed,
                "raw_response": raw_response,
                "error": error,
            }
        )
        if delay > 0:
            time.sleep(delay)

    results = pd.DataFrame.from_records(records)
    if results["observation_id"].duplicated().any():
        raise RuntimeError("Duplicate manipulation-check observation IDs")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run post-audit Gemini treatment manipulation checks."
    )
    parser.add_argument("--config", default="config/core_audit.yaml")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--results-path", default=None)
    parser.add_argument("--summary-path", default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    settings = config.get("manipulation_checks", {})
    results_path = Path(
        args.results_path
        or settings.get("output_results", "outputs/core/manipulation_checks.csv")
    )
    summary_path = Path(
        args.summary_path
        or settings.get("output_summary", "outputs/core/manipulation_check_summary.csv")
    )
    results = run_gemini_manipulation_checks(args.config, args.limit)
    summary = summarize_manipulation_checks(results)
    results_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(results_path, index=False)
    summary.to_csv(summary_path, index=False)

    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "provider": "gemini",
        "exact_model_id": str(results["exact_model_id"].iloc[0]) if not results.empty else None,
        "prompt_version": MANIPULATION_PROMPT_VERSION,
        "rows": len(results),
        "successful_rows": int(results["error"].fillna("").eq("").sum()),
        "run_after_primary_required": True,
    }
    (results_path.parent / "manipulation_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
