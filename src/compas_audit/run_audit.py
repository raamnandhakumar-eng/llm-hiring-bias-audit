from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pandas as pd

from .common import extract_json_object, load_config, sha256_text, stable_id
from .name_validation import assert_live_name_signals_validated
from .prompts import SYSTEM_PROMPT, screening_prompt
from .providers import AnthropicProvider, MockProvider, ScreeningProvider

REQUIRED_KEYS = {"fit_score", "recommend", "confidence", "strengths", "risk_factors", "reason"}
REFUSAL_PHRASES = (
    "cannot assist",
    "can't assist",
    "cannot evaluate",
    "unable to evaluate",
    "cannot make hiring",
)


def validate_screening_response(screening_response: dict[str, Any]) -> dict[str, Any]:
    missing_response_fields = REQUIRED_KEYS - screening_response.keys()
    if missing_response_fields:
        raise ValueError(f"Missing response fields: {sorted(missing_response_fields)}")

    fit_score = float(screening_response["fit_score"])
    model_confidence = float(screening_response["confidence"])
    if not 1 <= fit_score <= 10:
        raise ValueError("fit_score must be between 1 and 10.")
    if not 0 <= model_confidence <= 1:
        raise ValueError("confidence must be between 0 and 1.")
    if not isinstance(screening_response["recommend"], bool):
        raise ValueError("recommend must be a boolean.")
    if not isinstance(screening_response["strengths"], list) or not isinstance(
        screening_response["risk_factors"], list
    ):
        raise ValueError("strengths and risk_factors must be lists.")

    return {
        "fit_score": fit_score,
        "recommend": int(screening_response["recommend"]),
        "confidence": model_confidence,
        "strengths": json.dumps(screening_response["strengths"], ensure_ascii=False),
        "risk_factors": json.dumps(screening_response["risk_factors"], ensure_ascii=False),
        "reason": str(screening_response["reason"]),
    }


def require_external_preregistration(audit_config: dict[str, Any]) -> str:
    preregistration_settings = audit_config.get("external_preregistration", {})
    if not bool(preregistration_settings.get("required_for_live", False)):
        return ""

    url_environment_variable = str(
        preregistration_settings.get("url_env_var", "EXTERNAL_PREREGISTRATION_URL")
    )
    registration_url = os.getenv(url_environment_variable, "").strip()
    registration_source_document = str(
        preregistration_settings.get("source_document", "docs/osf_preregistration.md")
    )
    if not registration_url:
        raise RuntimeError(
            "A public OSF or AsPredicted preregistration is required before a live run. "
            f"Submit {registration_source_document}, then set "
            f"{url_environment_variable} to its permanent URL."
        )

    parsed_registration_url = urlparse(registration_url)
    registration_hostname = (parsed_registration_url.hostname or "").casefold()
    accepted_registration_hosts = [
        str(hostname).casefold()
        for hostname in preregistration_settings.get(
            "accepted_hosts",
            ["osf.io", "aspredicted.org"],
        )
    ]
    registration_host_is_allowed = any(
        registration_hostname == accepted_host
        or registration_hostname.endswith(f".{accepted_host}")
        for accepted_host in accepted_registration_hosts
    )
    if parsed_registration_url.scheme != "https" or not registration_host_is_allowed:
        accepted_hosts_text = ", ".join(accepted_registration_hosts)
        raise RuntimeError(
            f"{url_environment_variable} must be a permanent HTTPS registration URL "
            f"hosted by: {accepted_hosts_text}."
        )
    return registration_url


def create_screening_provider(
    provider_name: str,
    model_name: str,
    random_seed: int,
) -> ScreeningProvider:
    if provider_name == "mock":
        return MockProvider(seed=random_seed)
    if provider_name == "anthropic":
        return AnthropicProvider(model_name=model_name)
    raise ValueError(f"Unknown provider: {provider_name}")


def _response_looks_like_refusal(raw_response: str) -> bool:
    normalized_response = raw_response.casefold()
    return any(phrase in normalized_response for phrase in REFUSAL_PHRASES)


def run_screening_audit(
    config_path: str,
    provider_name: str,
    resume_limit: int | None = None,
) -> pd.DataFrame:
    audit_config = load_config(config_path)
    external_preregistration_url = ""
    if provider_name == "anthropic":
        external_preregistration_url = require_external_preregistration(audit_config)
        assert_live_name_signals_validated(audit_config)

    resume_permutations_path = Path(
        audit_config.get("output_resumes", "outputs/resume_permutations.csv")
    )
    if not resume_permutations_path.exists():
        raise FileNotFoundError(
            f"Resume permutations not found: {resume_permutations_path}. "
            "Run hiring-audit-generate first."
        )

    random_seed = int(audit_config.get("seed", 42))
    resume_permutations = (
        pd.read_csv(resume_permutations_path)
        .sample(frac=1, random_state=random_seed)
        .reset_index(drop=True)
    )
    if resume_limit is not None:
        resume_permutations = resume_permutations.head(resume_limit)

    provider_settings = audit_config.get("provider", {})
    screening_provider = create_screening_provider(
        provider_name,
        str(provider_settings.get("model", "set-via-ANTHROPIC_MODEL-before-live-run")),
        random_seed,
    )
    trials_per_resume = int(audit_config.get("trials_per_resume", 1))
    audit_temperatures = [
        float(temperature) for temperature in audit_config.get("temperatures", [0.0])
    ]
    max_response_tokens = int(provider_settings.get("max_tokens", 500))
    request_delay_seconds = float(provider_settings.get("request_delay_seconds", 0.0))
    provider_api_version = str(provider_settings.get("api_version", "unknown"))
    prompt_version = str(provider_settings.get("prompt_version", "unknown"))

    screening_jobs: list[tuple[pd.Series, float, int]] = []
    for _, resume_permutation in resume_permutations.iterrows():
        for temperature in audit_temperatures:
            for trial_number in range(1, trials_per_resume + 1):
                screening_jobs.append((resume_permutation, temperature, trial_number))
    randomized_job_order = (
        pd.Series(range(len(screening_jobs)))
        .sample(frac=1, random_state=random_seed + 1)
        .tolist()
    )

    audit_records: list[dict[str, Any]] = []
    for execution_order, scheduled_job_index in enumerate(randomized_job_order, start=1):
        resume_permutation, temperature, trial_number = screening_jobs[scheduled_job_index]
        user_prompt = screening_prompt(
            str(resume_permutation["target_role"]),
            str(resume_permutation["resume_text"]),
        )
        observation_id = stable_id(
            resume_permutation["resume_id"],
            screening_provider.model_name,
            temperature,
            trial_number,
        )
        request_started_at = time.perf_counter()
        request_timestamp = datetime.now(timezone.utc)
        raw_response = ""
        response_error = ""
        response_error_type = ""
        parser_status = "not_attempted"
        parsed_screening_fields: dict[str, Any] = {}
        try:
            raw_response = screening_provider.screen(
                SYSTEM_PROMPT,
                user_prompt,
                temperature,
                max_response_tokens,
                run_key=f"{observation_id}|trial={trial_number}",
            )
            parsed_screening_fields = validate_screening_response(
                extract_json_object(raw_response)
            )
            parser_status = "parsed"
        except Exception as exc:
            response_error_type = type(exc).__name__
            response_error = f"{response_error_type}: {exc}"
            parser_status = "error"

        audit_records.append(
            {
                **resume_permutation.to_dict(),
                "observation_id": observation_id,
                "run_id": observation_id,
                "execution_order": execution_order,
                "provider": provider_name,
                "exact_model_id": screening_provider.model_name,
                "model": screening_provider.model_name,
                "api_version": provider_api_version,
                "run_date": request_timestamp.date().isoformat(),
                "timestamp_utc": request_timestamp.isoformat(),
                "temperature": temperature,
                "prompt_version": prompt_version,
                "external_preregistration_url": external_preregistration_url,
                "system_prompt": SYSTEM_PROMPT,
                "user_prompt": user_prompt,
                "trial_number": trial_number,
                "trial": trial_number,
                "latency_seconds": round(time.perf_counter() - request_started_at, 4),
                "prompt_sha256": sha256_text(SYSTEM_PROMPT + "\n" + user_prompt),
                **parsed_screening_fields,
                "response_length_chars": len(raw_response),
                "refusal": int(_response_looks_like_refusal(raw_response)),
                "raw_response": raw_response,
                "parser_status": parser_status,
                "error_type": response_error_type,
                "error": response_error,
            }
        )
        if request_delay_seconds > 0:
            time.sleep(request_delay_seconds)

    audit_results = (
        pd.DataFrame.from_records(audit_records)
        .sort_values("execution_order")
        .reset_index(drop=True)
    )
    if audit_results["observation_id"].duplicated().any():
        raise RuntimeError("Duplicate observation IDs were generated.")
    return audit_results


def write_run_manifest(
    config_path: str,
    audit_results: pd.DataFrame,
    manifest_path: Path,
) -> None:
    config_file_text = Path(config_path).read_text(encoding="utf-8")
    successful_evaluations = int(audit_results["error"].fillna("").eq("").sum())
    external_preregistration_url = (
        str(audit_results["external_preregistration_url"].iloc[0])
        if not audit_results.empty and "external_preregistration_url" in audit_results
        else ""
    )
    run_manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "config_sha256": sha256_text(config_file_text),
        "provider": str(audit_results["provider"].iloc[0]) if not audit_results.empty else None,
        "exact_model_id": (
            str(audit_results["exact_model_id"].iloc[0]) if not audit_results.empty else None
        ),
        "api_version": (
            str(audit_results["api_version"].iloc[0]) if not audit_results.empty else None
        ),
        "prompt_version": (
            str(audit_results["prompt_version"].iloc[0]) if not audit_results.empty else None
        ),
        "external_preregistration_url": external_preregistration_url,
        "externally_preregistered": bool(external_preregistration_url),
        "rows": int(len(audit_results)),
        "successful_rows": successful_evaluations,
        "failed_rows": int(len(audit_results) - successful_evaluations),
        "refusals": int(audit_results["refusal"].sum()) if not audit_results.empty else 0,
        "unique_resumes": (
            int(audit_results["resume_id"].nunique()) if not audit_results.empty else 0
        ),
        "unique_occupations": (
            int(audit_results["occupation_id"].nunique()) if not audit_results.empty else 0
        ),
        "temperatures": (
            sorted(audit_results["temperature"].dropna().unique().tolist())
            if not audit_results.empty
            else []
        ),
        "trials": (
            sorted(audit_results["trial_number"].dropna().unique().tolist())
            if not audit_results.empty
            else []
        ),
        "randomized_execution_order": True,
        "selective_reruns_permitted": False,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(run_manifest, indent=2) + "\n", encoding="utf-8")


validate_result = validate_screening_response
assert_external_preregistration = require_external_preregistration
build_provider = create_screening_provider
_looks_like_refusal = _response_looks_like_refusal
run_experiment = run_screening_audit
write_manifest = write_run_manifest


def main() -> None:
    argument_parser = argparse.ArgumentParser(description="Run the synthetic LLM hiring audit.")
    argument_parser.add_argument("--config", default="config/audit.yaml")
    argument_parser.add_argument(
        "--provider",
        choices=["mock", "anthropic"],
        default="mock",
    )
    argument_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional number of resumes for a smoke test. Do not use for the confirmatory run.",
    )
    command_args = argument_parser.parse_args()

    audit_config = load_config(command_args.config)
    results_path = Path(
        audit_config.get("output_results", "outputs/screening_results.csv")
    )
    manifest_path = Path(audit_config.get("output_manifest", "outputs/run_manifest.json"))
    results_path.parent.mkdir(parents=True, exist_ok=True)
    audit_results = run_screening_audit(
        command_args.config,
        command_args.provider,
        resume_limit=command_args.limit,
    )
    audit_results.to_csv(results_path, index=False)
    write_run_manifest(command_args.config, audit_results, manifest_path)
    successful_evaluations = int(audit_results["error"].fillna("").eq("").sum())
    print(f"wrote {len(audit_results)} trials to {results_path}; {successful_evaluations} ok")


if __name__ == "__main__":
    main()
