from __future__ import annotations

import argparse
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from .common import extract_json_object, load_config, sha256_text, stable_id
from .prompts import PRIMARY_PROMPT_VERSION, SYSTEM_PROMPT, screening_prompt
from .providers import GeminiProvider
from .run_audit import (
    _response_looks_like_refusal,
    require_external_preregistration,
    validate_screening_response,
    write_run_manifest,
)


def select_balanced_pilot_resumes(
    resumes: pd.DataFrame,
    matched_sets_per_occupation: int,
) -> pd.DataFrame:
    selected_sets = (
        resumes[["occupation_id", "matched_set_id"]]
        .drop_duplicates()
        .sort_values(["occupation_id", "matched_set_id"])
        .groupby("occupation_id", group_keys=False)
        .head(matched_sets_per_occupation)
    )
    pilot = resumes.merge(
        selected_sets,
        on=["occupation_id", "matched_set_id"],
        how="inner",
    )
    pilot = pilot.sort_values(
        ["occupation_id", "matched_set_id", "education_pathway", "career_gap_months"]
    ).reset_index(drop=True)
    expected_rows = int(resumes["occupation_id"].nunique()) * matched_sets_per_occupation * 4
    if len(pilot) != expected_rows:
        raise RuntimeError(
            f"Gemini pilot expected {expected_rows} balanced resumes but selected {len(pilot)}."
        )
    if not pilot.groupby("matched_set_id").size().eq(4).all():
        raise RuntimeError("Every Gemini pilot matched set must contain all four treatments.")
    return pilot


def run_gemini_pilot(config_path: str) -> pd.DataFrame:
    config = load_config(config_path)
    registration_url = require_external_preregistration(config)
    pilot_settings = config.get("provider_sequence", {}).get("pilot", {})
    if pilot_settings.get("provider") != "gemini":
        raise RuntimeError("The configured feasibility pilot provider must be Gemini.")
    if bool(pilot_settings.get("inferential_use", True)):
        raise RuntimeError("Gemini pilot must remain non-inferential.")

    expected_model = str(pilot_settings.get("model", "gemini-2.5-flash"))
    provider = GeminiProvider(model_name=expected_model)
    if provider.model_name != expected_model:
        raise RuntimeError(
            f"GEMINI_MODEL must equal the locked pilot model {expected_model!r}; "
            f"received {provider.model_name!r}."
        )

    resume_path = Path(config["output_resumes"])
    if not resume_path.exists():
        raise FileNotFoundError(
            f"Resume permutations not found: {resume_path}. Run hiring-audit-generate first."
        )
    all_resumes = pd.read_csv(resume_path)
    matched_sets_per_occupation = int(
        pilot_settings.get("matched_sets_per_occupation", 1)
    )
    pilot_resumes = select_balanced_pilot_resumes(
        all_resumes,
        matched_sets_per_occupation,
    )

    trials_per_resume = int(pilot_settings.get("trials_per_resume", 1))
    if trials_per_resume != 1:
        raise RuntimeError("Gemini feasibility pilot is locked to one call per resume.")
    temperatures = [float(value) for value in config.get("temperatures", [0.0])]
    if temperatures != [0.0]:
        raise RuntimeError("Gemini feasibility pilot is locked to temperature 0.0.")

    provider_settings = config.get("provider", {})
    max_tokens = int(provider_settings.get("max_tokens", 500))
    prompt_version = str(provider_settings.get("prompt_version", PRIMARY_PROMPT_VERSION))
    seed = int(config.get("seed", 42))

    jobs = [row for _, row in pilot_resumes.iterrows()]
    randomized_order = (
        pd.Series(range(len(jobs)))
        .sample(frac=1, random_state=seed + 101)
        .tolist()
    )

    records: list[dict[str, Any]] = []
    for execution_order, job_index in enumerate(randomized_order, start=1):
        resume = jobs[job_index]
        user_prompt = screening_prompt(
            str(resume["target_role"]),
            str(resume["resume_text"]),
            prompt_version=prompt_version,
        )
        observation_id = stable_id(
            "gemini-pilot",
            resume["resume_id"],
            provider.model_name,
            prompt_version,
            0.0,
            1,
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
                0.0,
                max_tokens,
                run_key=f"{observation_id}|trial=1",
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
                "study_phase": "feasibility_pilot",
                "inferential_use": False,
                "observation_id": observation_id,
                "run_id": observation_id,
                "execution_order": execution_order,
                "provider": "gemini",
                "exact_model_id": provider.model_name,
                "model": provider.model_name,
                "api_version": "google-genai",
                "run_date": timestamp.date().isoformat(),
                "timestamp_utc": timestamp.isoformat(),
                "temperature": 0.0,
                "prompt_version": prompt_version,
                "external_preregistration_url": registration_url,
                "system_prompt": SYSTEM_PROMPT,
                "user_prompt": user_prompt,
                "trial_number": 1,
                "trial": 1,
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

    results = pd.DataFrame.from_records(records).sort_values("execution_order")
    if results["observation_id"].duplicated().any():
        raise RuntimeError("Duplicate Gemini pilot observation IDs were generated.")
    return results.reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the non-inferential Gemini feasibility pilot."
    )
    parser.add_argument("--config", default="config/core_audit.yaml")
    parser.add_argument(
        "--results-path",
        default="outputs/gemini_pilot/screening_results.csv",
    )
    parser.add_argument(
        "--manifest-path",
        default="outputs/gemini_pilot/run_manifest.json",
    )
    args = parser.parse_args()

    results_path = Path(args.results_path)
    manifest_path = Path(args.manifest_path)
    if results_path.exists() or manifest_path.exists():
        raise RuntimeError("Refusing to overwrite an existing Gemini pilot attempt.")
    results_path.parent.mkdir(parents=True, exist_ok=True)

    results = run_gemini_pilot(args.config)
    results.to_csv(results_path, index=False)
    write_run_manifest(args.config, results, manifest_path)
    successful = int(results["error"].fillna("").eq("").sum())
    print(
        f"Gemini feasibility pilot: {successful}/{len(results)} calls parsed; "
        "results are non-confirmatory and must not change the Claude design."
    )


if __name__ == "__main__":
    main()
