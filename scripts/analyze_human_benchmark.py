#!/usr/bin/env python3
"""Validate and compare blinded human evaluations with the live model audit."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from compas_audit.core_analysis import (
    build_preregistered_effect_size_table,
    fit_clustered_linear_model,
    prepare_core_audit_rows,
)

REQUIRED_HUMAN_COLUMNS = {
    "evaluator_id",
    "resume_id",
    "assignment_block",
    "presentation_order",
    "fit_score",
    "recommend",
    "confidence",
}


def validate_human_rows(human: pd.DataFrame, resumes: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED_HUMAN_COLUMNS - set(human.columns)
    if missing:
        raise ValueError(f"Human file is missing columns: {sorted(missing)}")
    if human[["evaluator_id", "resume_id"]].duplicated().any():
        raise ValueError("An evaluator reviewed the same resume more than once.")
    merged = human.merge(
        resumes[
            [
                "resume_id",
                "matched_set_id",
                "occupation_id",
                "occupation_tier",
                "education_pathway",
                "career_gap_months",
            ]
        ],
        on="resume_id",
        how="left",
        validate="many_to_one",
    )
    if merged["matched_set_id"].isna().any():
        unknown = merged.loc[merged["matched_set_id"].isna(), "resume_id"].unique()
        raise ValueError(f"Human file contains unknown resume IDs: {unknown.tolist()}")
    duplicate_sets = merged.duplicated(["evaluator_id", "matched_set_id"], keep=False)
    if duplicate_sets.any():
        raise ValueError("An evaluator saw more than one treatment variant from a matched set.")
    for column, lower, upper in (
        ("fit_score", 1, 10),
        ("recommend", 0, 1),
        ("confidence", 0, 1),
    ):
        merged[column] = pd.to_numeric(merged[column], errors="coerce")
        if merged[column].isna().any() or not merged[column].between(lower, upper).all():
            raise ValueError(f"{column} must be numeric and between {lower} and {upper}.")
    if not merged["recommend"].isin({0, 1}).all():
        raise ValueError("recommend must be coded 0 or 1.")
    merged["temperature"] = 0.0
    merged["error"] = ""
    return merged


def analyze_human_effects(human: pd.DataFrame) -> pd.DataFrame:
    prepared = prepare_core_audit_rows(human)
    models = [
        (fit_clustered_linear_model(prepared, outcome), outcome, "linear")
        for outcome in ("fit_score", "confidence")
    ]
    if prepared["recommend"].nunique() >= 2:
        models.append(
            (fit_clustered_linear_model(prepared, "recommend"), "recommend", "linear")
        )
    return build_preregistered_effect_size_table(models, prepared)


def build_agreement_table(human: pd.DataFrame, model: pd.DataFrame) -> pd.DataFrame:
    model_means = model.groupby("resume_id", as_index=False).agg(
        model_fit_score=("fit_score", "mean"),
        model_recommend=("recommend", "mean"),
        model_confidence=("confidence", "mean"),
    )
    paired = human.merge(model_means, on="resume_id", how="inner")
    if paired.empty:
        raise ValueError("Human and model files have no resume IDs in common.")
    return pd.DataFrame(
        [
            {
                "paired_human_reviews": len(paired),
                "unique_resumes": paired["resume_id"].nunique(),
                "fit_score_pearson": paired["fit_score"].corr(
                    paired["model_fit_score"]
                ),
                "confidence_pearson": paired["confidence"].corr(
                    paired["model_confidence"]
                ),
                "recommendation_agreement": (
                    paired["recommend"].eq(paired["model_recommend"].ge(0.5))
                ).mean(),
                "mean_human_fit": paired["fit_score"].mean(),
                "mean_model_fit": paired["model_fit_score"].mean(),
            }
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze the human hiring benchmark.")
    parser.add_argument("--human", required=True)
    parser.add_argument(
        "--resumes",
        default="outputs/core/resume_permutations.csv",
    )
    parser.add_argument(
        "--model",
        default="outputs/core/screening_results.csv",
    )
    parser.add_argument("--output-dir", default="outputs/human_benchmark")
    args = parser.parse_args()

    human = validate_human_rows(pd.read_csv(args.human), pd.read_csv(args.resumes))
    model = pd.read_csv(args.model)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    effects = analyze_human_effects(human)
    agreement = build_agreement_table(human, model)
    effects.to_csv(output / "human_treatment_effects.csv", index=False)
    agreement.to_csv(output / "human_model_agreement.csv", index=False)
    pd.DataFrame(
        [
            {
                "human_reviews": len(human),
                "evaluators": human["evaluator_id"].nunique(),
                "unique_resumes": human["resume_id"].nunique(),
                "matched_sets": human["matched_set_id"].nunique(),
            }
        ]
    ).to_csv(output / "human_benchmark_quality.csv", index=False)
    print(agreement.to_string(index=False))


if __name__ == "__main__":
    main()
