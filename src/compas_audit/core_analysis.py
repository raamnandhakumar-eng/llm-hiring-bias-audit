from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

PREREGISTERED_TREATMENT_TERMS = {
    "nontraditional",
    "has_gap",
    "nontraditional:frontline",
    "has_gap:frontline",
}


def prepare_core_audit_rows(
    raw_audit_rows: pd.DataFrame,
    include_failures: bool = False,
) -> pd.DataFrame:
    required_columns = {
        "occupation_tier",
        "education_pathway",
        "career_gap_months",
        "resume_id",
        "temperature",
    }
    missing_columns = required_columns - set(raw_audit_rows.columns)
    if missing_columns:
        raise ValueError(
            f"Input is missing required columns: {sorted(missing_columns)}"
        )

    prepared_rows = raw_audit_rows.copy()
    if "matched_set_id" not in prepared_rows:
        prepared_rows["matched_set_id"] = prepared_rows.get(
            "template_id",
            prepared_rows["resume_id"],
        )
    if "occupation_id" not in prepared_rows:
        prepared_rows["occupation_id"] = prepared_rows.get(
            "template_id",
            "unknown",
        )
    if "trial" not in prepared_rows and "trial_number" in prepared_rows:
        prepared_rows["trial"] = prepared_rows["trial_number"]

    response_errors = prepared_rows.get(
        "error",
        pd.Series("", index=prepared_rows.index),
    ).fillna("")
    prepared_rows["failed"] = ~response_errors.eq("")
    if not include_failures:
        prepared_rows = prepared_rows[
            ~prepared_rows["failed"]
        ].copy()

    prepared_rows["frontline"] = (
        prepared_rows["occupation_tier"]
        .eq("frontline")
        .astype(int)
    )
    prepared_rows["nontraditional"] = (
        prepared_rows["education_pathway"]
        .eq("nontraditional")
        .astype(int)
    )
    prepared_rows["has_gap"] = (
        pd.to_numeric(prepared_rows["career_gap_months"])
        .gt(0)
        .astype(int)
    )

    for outcome_column in ("fit_score", "recommend", "confidence"):
        if outcome_column not in prepared_rows:
            prepared_rows[outcome_column] = np.nan
        prepared_rows[outcome_column] = pd.to_numeric(
            prepared_rows[outcome_column],
            errors="coerce",
        )

    if not include_failures:
        prepared_rows = prepared_rows.dropna(
            subset=["fit_score", "recommend", "confidence"]
        )
        if prepared_rows.empty:
            raise ValueError(
                "No valid core-audit rows remain after filtering failures."
            )
        if prepared_rows["resume_id"].nunique() < 2:
            raise ValueError(
                "Clustered inference requires at least two unique resumes."
            )
    return prepared_rows


def build_core_model_formula(outcome_column: str) -> str:
    return (
        f"{outcome_column} ~ nontraditional + has_gap "
        "+ nontraditional:frontline + has_gap:frontline "
        "+ C(occupation_id) + C(matched_set_id) + C(temperature)"
    )


def fit_clustered_linear_model(
    valid_audit_rows: pd.DataFrame,
    outcome_column: str,
):
    cluster_covariance_settings = {
        "groups": valid_audit_rows["resume_id"],
        "use_correction": True,
    }
    return smf.ols(
        build_core_model_formula(outcome_column),
        data=valid_audit_rows,
    ).fit(
        cov_type="cluster",
        cov_kwds=cluster_covariance_settings,
    )


def fit_clustered_logistic_recommendation(
    valid_audit_rows: pd.DataFrame,
):
    if valid_audit_rows["recommend"].nunique() < 2:
        return None
    return smf.glm(
        build_core_model_formula("recommend"),
        data=valid_audit_rows,
        family=sm.families.Binomial(),
    ).fit(
        cov_type="cluster",
        cov_kwds={"groups": valid_audit_rows["resume_id"]},
    )


def build_coefficient_table(
    fitted_model: Any,
    outcome_column: str,
    model_type: str,
) -> pd.DataFrame:
    confidence_intervals = fitted_model.conf_int(alpha=0.05)
    return pd.DataFrame(
        {
            "outcome": outcome_column,
            "model_type": model_type,
            "term": fitted_model.params.index,
            "estimate": fitted_model.params.values,
            "std_error_clustered": fitted_model.bse.values,
            "p_value": fitted_model.pvalues.values,
            "ci_95_low": confidence_intervals.iloc[:, 0].values,
            "ci_95_high": confidence_intervals.iloc[:, 1].values,
        }
    )


def add_benjamini_hochberg_results(
    coefficient_table: pd.DataFrame,
    alpha: float = 0.05,
) -> pd.DataFrame:
    adjusted_coefficients = coefficient_table.copy()
    adjusted_coefficients["q_value_bh"] = pd.NA
    adjusted_coefficients["reject_fdr_05"] = False
    preregistered_rows = adjusted_coefficients["term"].isin(
        PREREGISTERED_TREATMENT_TERMS
    )
    if preregistered_rows.any():
        reject_null, adjusted_p_values, _, _ = multipletests(
            adjusted_coefficients.loc[
                preregistered_rows,
                "p_value",
            ],
            alpha=alpha,
            method="fdr_bh",
        )
        adjusted_coefficients.loc[
            preregistered_rows,
            "q_value_bh",
        ] = adjusted_p_values
        adjusted_coefficients.loc[
            preregistered_rows,
            "reject_fdr_05",
        ] = reject_null
    return adjusted_coefficients


def build_placebo_recovery_table(
    coefficient_table: pd.DataFrame,
) -> pd.DataFrame:
    planted_effects = {
        "nontraditional": -0.15,
        "has_gap": -0.45,
        "nontraditional:frontline": 0.0,
        "has_gap:frontline": 0.0,
    }
    fit_score_coefficients = coefficient_table[
        coefficient_table["outcome"].eq("fit_score")
        & coefficient_table["model_type"].eq("linear")
        & coefficient_table["term"].isin(planted_effects)
    ].copy()
    fit_score_coefficients["expected_effect"] = (
        fit_score_coefficients["term"].map(planted_effects)
    )
    fit_score_coefficients["recovery_error"] = (
        fit_score_coefficients["estimate"]
        - fit_score_coefficients["expected_effect"]
    )
    fit_score_coefficients["abs_recovery_error"] = (
        fit_score_coefficients["recovery_error"].abs()
    )
    return fit_score_coefficients[
        [
            "term",
            "expected_effect",
            "estimate",
            "std_error_clustered",
            "p_value",
            "q_value_bh",
            "ci_95_low",
            "ci_95_high",
            "recovery_error",
            "abs_recovery_error",
        ]
    ].sort_values("term")


def build_treatment_mean_table(
    valid_audit_rows: pd.DataFrame,
) -> pd.DataFrame:
    evaluation_count_column = (
        "observation_id"
        if "observation_id" in valid_audit_rows
        else "resume_id"
    )
    return (
        valid_audit_rows.groupby(
            [
                "occupation_tier",
                "education_pathway",
                "career_gap_months",
            ],
            as_index=False,
        )
        .agg(
            evaluations=(evaluation_count_column, "size"),
            mean_fit_score=("fit_score", "mean"),
            interview_rate=("recommend", "mean"),
            mean_confidence=("confidence", "mean"),
        )
        .sort_values(
            [
                "occupation_tier",
                "education_pathway",
                "career_gap_months",
            ]
        )
    )


def build_failed_recommendation_sensitivity(
    all_audit_rows: pd.DataFrame,
) -> pd.DataFrame:
    sensitivity_rows = all_audit_rows.copy()
    sensitivity_rows["recommend_failed_as_zero"] = (
        sensitivity_rows["recommend"].fillna(0)
    )
    if sensitivity_rows["recommend_failed_as_zero"].nunique() < 2:
        return pd.DataFrame(
            columns=[
                "outcome",
                "model_type",
                "term",
                "estimate",
                "std_error_clustered",
                "p_value",
                "ci_95_low",
                "ci_95_high",
            ]
        )
    cluster_covariance_settings = {
        "groups": sensitivity_rows["resume_id"],
        "use_correction": True,
    }
    sensitivity_model = smf.ols(
        build_core_model_formula("recommend_failed_as_zero"),
        data=sensitivity_rows,
    ).fit(
        cov_type="cluster",
        cov_kwds=cluster_covariance_settings,
    )
    return build_coefficient_table(
        sensitivity_model,
        outcome_column="recommend_failed_as_zero",
        model_type="linear_sensitivity",
    )


def write_core_audit_report(
    output_directory: Path,
    raw_audit_rows: pd.DataFrame,
    valid_audit_rows: pd.DataFrame,
    coefficient_table: pd.DataFrame,
    placebo_recovery_table: pd.DataFrame,
) -> None:
    preregistered_coefficients = coefficient_table[
        coefficient_table["term"].isin(
            PREREGISTERED_TREATMENT_TERMS
        )
    ]
    mean_absolute_recovery_error = (
        float(placebo_recovery_table["abs_recovery_error"].mean())
        if not placebo_recovery_table.empty
        else float("nan")
    )
    report_lines = [
        "# Core labor-market audit report",
        "",
        "This track tests career-gap and education-pathway effects while holding "
        "candidate names fixed within matched sets. It does not estimate "
        "perceived-name-signal effects.",
        "",
        "## Run quality",
        "",
        f"- Evaluations attempted: **{len(raw_audit_rows):,}**",
        f"- Valid evaluations: **{len(valid_audit_rows):,}**",
        (
            "- Failed evaluations: "
            f"**{len(raw_audit_rows) - len(valid_audit_rows):,}**"
        ),
        (
            "- Unique matched resumes: "
            f"**{valid_audit_rows['resume_id'].nunique():,}**"
        ),
        (
            "- Base profiles: "
            f"**{valid_audit_rows['matched_set_id'].nunique():,}**"
        ),
        (
            "- Occupations: "
            f"**{valid_audit_rows['occupation_id'].nunique():,}**"
        ),
        "- Recommendation model estimable: "
        f"**{'Yes' if valid_audit_rows['recommend'].nunique() >= 2 else 'No'}**",
        "",
        "## Primary coefficients",
        "",
        preregistered_coefficients.to_markdown(index=False),
        "",
    ]
    if not placebo_recovery_table.empty:
        report_lines.extend(
            [
                "## Mock-provider recovery diagnostic",
                "",
                (
                    "This section is meaningful only for the deterministic "
                    "mock provider."
                ),
                "",
                (
                    "Mean absolute recovery error: "
                    f"**{mean_absolute_recovery_error:.3f}**."
                ),
                "",
                placebo_recovery_table.to_markdown(index=False),
                "",
            ]
        )
    (output_directory / "core_audit_report.md").write_text(
        "\n".join(report_lines),
        encoding="utf-8",
    )


def analyze_core_audit(
    input_path: str,
    output_dir: str,
    fdr_alpha: float = 0.05,
) -> None:
    output_directory = Path(output_dir)
    output_directory.mkdir(parents=True, exist_ok=True)
    raw_audit_rows = pd.read_csv(input_path)
    valid_audit_rows = prepare_core_audit_rows(raw_audit_rows)
    all_audit_rows = prepare_core_audit_rows(
        raw_audit_rows,
        include_failures=True,
    )

    fitted_models = [
        (
            fit_clustered_linear_model(
                valid_audit_rows,
                "fit_score",
            ),
            "fit_score",
            "linear",
        ),
        (
            fit_clustered_linear_model(
                valid_audit_rows,
                "confidence",
            ),
            "confidence",
            "linear",
        ),
    ]
    recommendation_models_estimable = (
        valid_audit_rows["recommend"].nunique() >= 2
    )
    if recommendation_models_estimable:
        fitted_models.append(
            (
                fit_clustered_linear_model(
                    valid_audit_rows,
                    "recommend",
                ),
                "recommend",
                "linear",
            )
        )
        logistic_recommendation_model = (
            fit_clustered_logistic_recommendation(valid_audit_rows)
        )
        if logistic_recommendation_model is not None:
            fitted_models.append(
                (
                    logistic_recommendation_model,
                    "recommend",
                    "logistic",
                )
            )

    coefficient_table = pd.concat(
        [
            build_coefficient_table(
                fitted_model,
                outcome_column,
                model_type,
            )
            for fitted_model, outcome_column, model_type in fitted_models
        ],
        ignore_index=True,
    )
    coefficient_table = add_benjamini_hochberg_results(
        coefficient_table,
        alpha=fdr_alpha,
    )
    placebo_recovery_table = build_placebo_recovery_table(
        coefficient_table
    )
    failure_sensitivity_table = (
        build_failed_recommendation_sensitivity(all_audit_rows)
    )

    run_quality_table = pd.DataFrame(
        [
            {
                "input_rows": len(raw_audit_rows),
                "valid_rows": len(valid_audit_rows),
                "failed_rows": (
                    len(raw_audit_rows) - len(valid_audit_rows)
                ),
                "unique_resumes": (
                    valid_audit_rows["resume_id"].nunique()
                ),
                "unique_base_profiles": (
                    valid_audit_rows["matched_set_id"].nunique()
                ),
                "unique_occupations": (
                    valid_audit_rows["occupation_id"].nunique()
                ),
                "name_signal_effects_estimated": False,
                "recommendation_models_estimable": (
                    recommendation_models_estimable
                ),
            }
        ]
    )

    coefficient_table.to_csv(
        output_directory / "core_coefficients.csv",
        index=False,
    )
    placebo_recovery_table.to_csv(
        output_directory / "core_placebo_recovery.csv",
        index=False,
    )
    failure_sensitivity_table.to_csv(
        output_directory / "core_failure_sensitivity.csv",
        index=False,
    )
    build_treatment_mean_table(valid_audit_rows).to_csv(
        output_directory / "core_treatment_means.csv",
        index=False,
    )
    run_quality_table.to_csv(
        output_directory / "core_run_quality.csv",
        index=False,
    )
    write_core_audit_report(
        output_directory,
        raw_audit_rows,
        valid_audit_rows,
        coefficient_table,
        placebo_recovery_table,
    )


PRIMARY_TERMS = PREREGISTERED_TREATMENT_TERMS


def prepare_core_data(
    frame: pd.DataFrame,
    include_failures: bool = False,
) -> pd.DataFrame:
    return prepare_core_audit_rows(
        frame,
        include_failures=include_failures,
    )


def core_model_formula(outcome: str) -> str:
    return build_core_model_formula(outcome)


def fit_core_linear_model(
    data: pd.DataFrame,
    outcome: str,
):
    return fit_clustered_linear_model(data, outcome)


def fit_core_logistic_recommendation(data: pd.DataFrame):
    return fit_clustered_logistic_recommendation(data)


def coefficient_frame(
    model: Any,
    outcome: str,
    model_type: str,
) -> pd.DataFrame:
    return build_coefficient_table(model, outcome, model_type)


def apply_fdr(
    coefficients: pd.DataFrame,
    alpha: float = 0.05,
) -> pd.DataFrame:
    return add_benjamini_hochberg_results(
        coefficients,
        alpha=alpha,
    )


def placebo_recovery(coefficients: pd.DataFrame) -> pd.DataFrame:
    return build_placebo_recovery_table(coefficients)


def treatment_means(data: pd.DataFrame) -> pd.DataFrame:
    return build_treatment_mean_table(data)


def failure_sensitivity(
    data_with_failures: pd.DataFrame,
) -> pd.DataFrame:
    return build_failed_recommendation_sensitivity(
        data_with_failures
    )


def write_report(
    output: Path,
    raw: pd.DataFrame,
    data: pd.DataFrame,
    coefficients: pd.DataFrame,
    recovery: pd.DataFrame,
) -> None:
    write_core_audit_report(
        output,
        raw,
        data,
        coefficients,
        recovery,
    )


def analyze_core(
    input_path: str,
    output_dir: str,
    fdr_alpha: float = 0.05,
) -> None:
    analyze_core_audit(
        input_path,
        output_dir,
        fdr_alpha=fdr_alpha,
    )


def main() -> None:
    argument_parser = argparse.ArgumentParser(
        description=(
            "Analyze the career-gap and education-pathway core audit."
        )
    )
    argument_parser.add_argument(
        "--input",
        default="outputs/core/screening_results.csv",
    )
    argument_parser.add_argument(
        "--output-dir",
        default="outputs/core/analysis",
    )
    argument_parser.add_argument(
        "--fdr-alpha",
        type=float,
        default=0.05,
    )
    command_args = argument_parser.parse_args()
    analyze_core_audit(
        command_args.input,
        command_args.output_dir,
        fdr_alpha=command_args.fdr_alpha,
    )


if __name__ == "__main__":
    main()
