from pathlib import Path

import pandas as pd
import pytest

from compas_audit.balance import (
    build_balance_check_table,
    build_resume_metric_table,
)
from compas_audit.generate import generate_resume_permutations
from compas_audit.manipulation import (
    run_manipulation_checks,
    summarize_manipulation_checks,
    validate_manipulation_response,
)
from compas_audit.prompts import (
    ALL_SCREENING_PROMPT_VERSIONS,
    PRIMARY_PROMPT_VERSION,
    screening_prompt,
)
from compas_audit.run_audit import run_experiment


def _write_core_resumes() -> pd.DataFrame:
    resumes = generate_resume_permutations(
        "config/core_audit.yaml",
        "data/templates/resume_templates.csv",
    )
    output = Path("outputs/core/resume_permutations.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    resumes.to_csv(output, index=False)
    return resumes


def test_core_resume_text_is_balanced_outside_treatments():
    resumes = _write_core_resumes()
    metrics = build_resume_metric_table(resumes)
    checks = build_balance_check_table(metrics)
    assert checks["pass"].all()
    assert checks.set_index("metric").loc["invariant_text_hash", "pass"]


def test_three_version2_prompts_are_distinct_and_valid():
    assert PRIMARY_PROMPT_VERSION == "v2.0-primary"
    versions = [
        "v2.0-primary",
        "v2.0-concise",
        "v2.0-rubric",
    ]
    prompts = {
        screening_prompt("Analyst", "Candidate: Alex Morgan", version)
        for version in versions
    }
    assert len(prompts) == 3
    assert set(versions).issubset(ALL_SCREENING_PROMPT_VERSIONS)


def test_prompt_version_is_part_of_observation_identity():
    _write_core_resumes()
    primary = run_experiment(
        "config/core_audit.yaml",
        "mock",
        limit=1,
        prompt_version="v2.0-primary",
        trials=1,
    )
    concise = run_experiment(
        "config/core_audit.yaml",
        "mock",
        limit=1,
        prompt_version="v2.0-concise",
        trials=1,
    )
    assert primary.loc[0, "observation_id"] != concise.loc[0, "observation_id"]
    assert primary.loc[0, "prompt_sha256"] != concise.loc[0, "prompt_sha256"]


def test_mock_manipulation_check_detects_both_treatments():
    _write_core_resumes()
    results = run_manipulation_checks("config/core_audit.yaml", "mock")
    summary = summarize_manipulation_checks(results).set_index("check")
    assert len(results) == 128
    assert summary.loc["career_gap", "accuracy"] == pytest.approx(1.0)
    assert summary.loc["education_pathway", "accuracy"] == pytest.approx(1.0)
    assert summary.loc["both", "accuracy"] == pytest.approx(1.0)


def test_invalid_manipulation_value_is_rejected():
    with pytest.raises(ValueError, match="0 or 12"):
        validate_manipulation_response(
            {
                "detected_career_gap_months": 6,
                "detected_education_pathway": "traditional",
                "career_gap_evidence": "six months",
                "education_evidence": "traditional",
            }
        )
