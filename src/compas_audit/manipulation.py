from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from .common import extract_json_object, load_config, sha256_text, stable_id
from .prompts import MANIPULATION_PROMPT_VERSION, SYSTEM_PROMPT, manipulation_prompt
from .run_audit import create_screening_provider, require_external_preregistration

REQUIRED_MANIPULATION_KEYS = {
    "detected_career_gap_months",
    "detected_education_pathway",
    "career_gap_evidence",
    "education_evidence",
}


def validate_manipulation_response(payload: dict[str, Any]) -> dict[str, Any]:
    missing = REQUIRED_MANIPULATION_KEYS - payload.keys()
    if missing:
        raise ValueError(f"Missing manipulation-check fields: {sorted(missing)}")
    detected_gap = int(payload["detected_career_gap_months"])
    detected_pathway = str(payload["detected_education_pathway"]).casefold()
    if detected_gap not in {0, 12}:
        raise ValueError("detected_career_gap_months must be 0 or 12")
    if detected_pathway not in {"traditional", "nontraditional", "unclear"}:
        raise ValueError("detected_education_pathway has an invalid value")
    return {
        "detected_career_gap_months": detected_gap,
        "detected_education_pathway": detected_pathway,
        "career_gap_evidence": str(payload["career_gap_evidence"]),
        "education_evidence": str(payload["education_evidence"]),
    }


def run_manipulation_checks(
    config_path: str,
    provider_name: str,
    resume_limit: int | None = None,
) -> pd.DataFrame:
    config = load_config(config_path)
    settings = config.get("manipulation_checks", {})
    if not bool(settings.get("enabled", True)):
        raise RuntimeError("Manipulation checks are disabled in the configuration.")
    registration_url = (
        require_external_preregistration(config)
        if provider_name == "anthropic"
        else ""
    )
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
    provider_settings = config.get("provider", {})
    provider = create_screening_provider(
        provider_name,
        str(provider_settings.get("model", "set-via-ANTHROPIC_MODEL-before-live-run")),
        seed + 13,
    )
    max_tokens = int(settings.get("max_tokens", 250))
    delay = float(provider_settings.get("request_delay_seconds", 0.0))
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
                "provider": provider_name,
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
    frame = pd.DataFrame.from_records(records)
    if frame["observation_id"].duplicated().any():
        raise RuntimeError("Duplicate manipulation-check observation IDs")
    return frame


def summarize_manipulation_checks(results: pd.DataFrame) -> pd.DataFrame:
    valid = results[results["error"].fillna("").eq("")].copy()
    if valid.empty:
        return pd.DataFrame(
            [{"check": "overall", "valid_rows": 0, "correct_rows": 0, "accuracy": float("nan")}]
        )
    valid["career_gap_correct"] = (
        pd.to_numeric(valid["detected_career_gap_months"])
        .eq(pd.to_numeric(valid["career_gap_months"]))
    )
    valid["education_pathway_correct"] = (
        valid["detected_education_pathway"].eq(valid["education_pathway"])
    )
    rows = []
    for check, column in (
        ("career_gap", "career_gap_correct"),
        ("education_pathway", "education_pathway_correct"),
        ("both", "both_correct"),
    ):
        if check == "both":
            valid[column] = valid["career_gap_correct"] & valid["education_pathway_correct"]
        rows.append(
            {
                "check": check,
                "valid_rows": len(valid),
                "correct_rows": int(valid[column].sum()),
                "accuracy": float(valid[column].mean()),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run post-audit treatment manipulation checks.")
    parser.add_argument("--config", default="config/core_audit.yaml")
    parser.add_argument("--provider", choices=["mock", "anthropic"], default="mock")
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
    results = run_manipulation_checks(args.config, args.provider, args.limit)
    summary = summarize_manipulation_checks(results)
    results_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(results_path, index=False)
    summary.to_csv(summary_path, index=False)
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "provider": args.provider,
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
