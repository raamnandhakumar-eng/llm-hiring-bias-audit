from __future__ import annotations

import argparse
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from .common import extract_json_object, load_config, sha256_text, stable_id
from .name_validation import assert_live_name_signals_validated
from .prompts import PRIMARY_PROMPT_VERSION, SYSTEM_PROMPT, screening_prompt
from .providers import GeminiProvider
from .run_audit import (
    _response_looks_like_refusal,
    require_external_preregistration,
    validate_screening_response,
    write_run_manifest,
)


def run_gemini_audit(
    config_path: str,
    resume_limit: int | None = None,
    prompt_version_override: str | None = None,
    trials_override: int | None = None,
) -> pd.DataFrame:
    audit_config = load_config(config_path)
    external_preregistration_url = require_external_preregistration(audit_config)
    assert_live_name_signals_validated(audit_config)

    resume_path = Path(
        audit_config.get("output_resumes", "outputs/resume_permutations.csv")
    )
    if not resume_path.exists():
        raise FileNotFoundError(
            f"Resume permutations not found: {resume_path}. Run hiring-audit-generate first."
        )

    seed = int(audit_config.get("seed", 42))
    resumes = (
        pd.read_csv(resume_path)
        .sample(frac=1, random_state=seed)
        .reset_index(drop=True)
    )
    if resume_limit is not None:
        resumes = resumes.head(resume_limit)

    provider_settings = audit_config.get("provider", {})
    provider = GeminiProvider(model_name="set-via-GEMINI_MODEL-before-live-run")
    trials_per_resume = int(
        trials_override
        if trials_override is not None
        else audit_config.get("trials_per_resume", 1)
    )
    if trials_per_resume < 1:
        raise ValueError("trials_per_resume must be at least 1.")

    temperatures = [
        float(value) for value in audit_config.get("temperatures", [0.0])
    ]
    max_tokens = int(provider_settings.get("max_tokens", 500))
    delay = float(provider_settings.get("request_delay_seconds", 0.0))
    prompt_version = str(
        prompt_version_override
        or provider_settings.get("prompt_version", PRIMARY_PROMPT_VERSION)
    )

    jobs: list[tuple[pd.Series, float, int]] = []
    for _, resume in resumes.iterrows():
        for temperature in temperatures:
            for trial_number in range(1, trials_per_resume + 1):
                jobs.append((resume, temperature, trial_number))

    randomized_order = (
        pd.Series(range(len(jobs)))
        .sample(frac=1, random_state=seed + 1)
        .tolist()
    )

    records: list[dict[str, Any]] = []
    for execution_order, job_index in enumerate(randomized_order, start=1):
        resume, temperature, trial_number = jobs[job_index]
        user_prompt = screening_prompt(
            str(resume["target_role"]),
            str(resume["resume_text"]),
            prompt_version=prompt_version,
        )
        observation_id = stable_id(
            resume["resume_id"],
            provider.model_name,
            prompt_version,
            temperature,
            trial_number,
        )
        started = time.perf_counter()
        timestamp = datetime.now(timezone.utc)
        raw_response = ""
        error = ""
        error_type = ""
        parser_status = "not_attempted"
        parsed: dict[str, Any] = {}
        try:
            raw_response = provider.screen(
                SYSTEM_PROMPT,
                user_prompt,
                temperature,
                max_tokens,
                run_key=f"{observation_id}|trial={trial_number}",
            )
            parsed = validate_screening_response(extract_json_object(raw_response))
            parser_status = "parsed"
        except Exception as exc:
            error_type = type(exc).__name__
            error = f"{error_type}: {exc}"
            parser_status = "error"

        records.append(
            {
                **resume.to_dict(),
                "observation_id": observation_id,
                "run_id": observation_id,
                "execution_order": execution_order,
                "provider": "gemini",
                "exact_model_id": provider.model_name,
                "model": provider.model_name,
                "api_version": "google-genai",
                "run_date": timestamp.date().isoformat(),
                "timestamp_utc": timestamp.isoformat(),
                "temperature": temperature,
                "prompt_version": prompt_version,
                "external_preregistration_url": external_preregistration_url,
                "system_prompt": SYSTEM_PROMPT,
                "user_prompt": user_prompt,
                "trial_number": trial_number,
                "trial": trial_number,
                "latency_seconds": round(time.perf_counter() - started, 4),
                "prompt_sha256": sha256_text(SYSTEM_PROMPT + "\n" + user_prompt),
                **parsed,
                "response_length_chars": len(raw_response),
                "refusal": int(_response_looks_like_refusal(raw_response)),
                "raw_response": raw_response,
                "parser_status": parser_status,
                "error_type": error_type,
                "error": error,
            }
        )
        if delay > 0:
            time.sleep(delay)

    results = (
        pd.DataFrame.from_records(records)
        .sort_values("execution_order")
        .reset_index(drop=True)
    )
    if results["observation_id"].duplicated().any():
        raise RuntimeError("Duplicate observation IDs were generated.")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the preregistered Gemini hiring audit.")
    parser.add_argument("--config", default="config/core_audit.yaml")
    parser.add_argument("--prompt-version", default=None)
    parser.add_argument("--trials", type=int, default=None)
    parser.add_argument("--results-path", default=None)
    parser.add_argument("--manifest-path", default=None)
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional number of resumes for a smoke test. Do not use for the confirmatory run.",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    results_path = Path(
        args.results_path
        or config.get("output_results", "outputs/core/screening_results.csv")
    )
    manifest_path = Path(
        args.manifest_path
        or config.get("output_manifest", "outputs/core/run_manifest.json")
    )
    results_path.parent.mkdir(parents=True, exist_ok=True)
    results = run_gemini_audit(
        args.config,
        resume_limit=args.limit,
        prompt_version_override=args.prompt_version,
        trials_override=args.trials,
    )
    results.to_csv(results_path, index=False)
    write_run_manifest(args.config, results, manifest_path)
    successful = int(results["error"].fillna("").eq("").sum())
    print(f"wrote {len(results)} Gemini trials to {results_path}; {successful} ok")


if __name__ == "__main__":
    main()
