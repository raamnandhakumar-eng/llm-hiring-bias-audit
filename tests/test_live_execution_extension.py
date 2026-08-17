from pathlib import Path

import pandas as pd
import yaml

from compas_audit.gemini_pilot import select_balanced_pilot_resumes


def _pilot_fixture() -> pd.DataFrame:
    rows = []
    for occupation_index in range(8):
        occupation_id = f"occupation_{occupation_index}"
        for set_index in range(2):
            matched_set_id = f"{occupation_id}_set_{set_index}"
            for education_pathway in ("traditional", "nontraditional"):
                for career_gap_months in (0, 12):
                    rows.append(
                        {
                            "occupation_id": occupation_id,
                            "matched_set_id": matched_set_id,
                            "education_pathway": education_pathway,
                            "career_gap_months": career_gap_months,
                        }
                    )
    return pd.DataFrame(rows)


def test_gemini_pilot_is_balanced_and_32_calls() -> None:
    pilot = select_balanced_pilot_resumes(_pilot_fixture())
    assert len(pilot) == 32
    assert pilot["occupation_id"].nunique() == 8
    assert pilot["matched_set_id"].nunique() == 8
    assert pilot.groupby("matched_set_id").size().eq(4).all()


def test_claude_confirmatory_outputs_are_separate_from_historical_core() -> None:
    config = yaml.safe_load(Path("config/claude_confirmatory.yaml").read_text())
    assert config["provider"]["model"] == "claude-sonnet-4-6"
    assert config["design"]["planned_evaluations"] == 640
    assert config["output_results"].startswith("outputs/claude_confirmatory/")
    assert config["output_manifest"].startswith("outputs/claude_confirmatory/")
    assert config["manipulation_checks"]["output_results"].startswith(
        "outputs/claude_confirmatory/"
    )


def test_historical_core_config_remains_anthropic_ready() -> None:
    core = yaml.safe_load(Path("config/core_audit.yaml").read_text())
    assert core["design"]["planned_evaluations"] == 640
    assert core["output_results"] == "outputs/core/screening_results.csv"
    assert core["provider"]["model"] == "set-via-ANTHROPIC_MODEL-before-live-run"
    assert core["external_preregistration"]["source_document"] == "docs/osf_preregistration.md"
