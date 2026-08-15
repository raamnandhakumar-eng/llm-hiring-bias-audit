#!/usr/bin/env python3
"""Pre-run power calculations for the 640-evaluation core matched audit."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.stats.power import TTestPower

ASSUMPTIONS = (
    {
        "outcome": "fit_score",
        "condition_level_sd": 0.40,
        "within_resume_call_sd": 0.60,
        "main_effect_target": 0.30,
        "interaction_target": 0.50,
        "unit": "score points",
    },
    {
        "outcome": "recommendation_probability",
        "condition_level_sd": 0.15,
        "within_resume_call_sd": 0.35,
        "main_effect_target": 0.15,
        "interaction_target": 0.20,
        "unit": "probability",
    },
)


def achieved_power(
    effect: float,
    standard_deviation: float,
    matched_sets: int,
    alpha: float = 0.05,
) -> float:
    return float(
        TTestPower().power(
            effect_size=abs(effect) / standard_deviation,
            nobs=matched_sets,
            alpha=alpha,
            alternative="two-sided",
        )
    )


def contrast_standard_deviation(
    condition_level_sd: float,
    within_resume_call_sd: float,
    repetitions: int,
    contrast: str,
) -> float:
    if repetitions < 1:
        raise ValueError("repetitions must be at least 1")
    cell_component = math.sqrt(
        condition_level_sd**2 + within_resume_call_sd**2 / repetitions
    )
    if contrast == "main_effect":
        return cell_component
    if contrast == "interaction":
        return 2 * cell_component
    raise ValueError(f"Unknown contrast: {contrast}")


def minimum_detectable_effect(
    standard_deviation: float,
    matched_sets: int,
    alpha: float = 0.05,
    power: float = 0.80,
) -> float:
    standardized_effect = TTestPower().solve_power(
        effect_size=None,
        nobs=matched_sets,
        alpha=alpha,
        power=power,
        alternative="two-sided",
    )
    return float(standardized_effect * standard_deviation)


def build_power_table(matched_sets: int, repetitions: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for item in ASSUMPTIONS:
        for contrast in ("main_effect", "interaction"):
            contrast_sd = contrast_standard_deviation(
                item["condition_level_sd"],
                item["within_resume_call_sd"],
                repetitions,
                contrast,
            )
            target = item[
                "main_effect_target" if contrast == "main_effect" else "interaction_target"
            ]
            rows.append(
                {
                    "outcome": item["outcome"],
                    "contrast": contrast,
                    "matched_sets": matched_sets,
                    "treatment_cells_per_set": 4,
                    "repetitions_per_resume": repetitions,
                    "unique_resumes": matched_sets * 4,
                    "planned_evaluations": matched_sets * 4 * repetitions,
                    "condition_level_sd": item["condition_level_sd"],
                    "within_resume_call_sd": item["within_resume_call_sd"],
                    "contrast_sd_after_repeats": contrast_sd,
                    "target_effect": target,
                    "mde_alpha_05_power_80": minimum_detectable_effect(
                        contrast_sd,
                        matched_sets,
                    ),
                    "mde_bonferroni_12_power_80": minimum_detectable_effect(
                        contrast_sd,
                        matched_sets,
                        alpha=0.05 / 12,
                    ),
                    "power_at_target_alpha_05": achieved_power(
                        target,
                        contrast_sd,
                        matched_sets,
                    ),
                    "unit": item["unit"],
                }
            )
    return pd.DataFrame(rows)


def build_repetition_table(matched_sets: int, maximum_repetitions: int = 10) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for repetitions in range(1, maximum_repetitions + 1):
        rows.extend(build_power_table(matched_sets, repetitions).to_dict(orient="records"))
    return pd.DataFrame(rows)


def make_power_figure(repetition_table: pd.DataFrame, output_path: Path) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    labels = {"main_effect": "Main effect", "interaction": "Interaction"}
    for axis, outcome in zip(
        axes,
        ("fit_score", "recommendation_probability"),
        strict=True,
    ):
        subset = repetition_table[repetition_table["outcome"].eq(outcome)]
        for contrast in ("main_effect", "interaction"):
            group = subset[subset["contrast"].eq(contrast)]
            axis.plot(
                group["repetitions_per_resume"],
                group["mde_alpha_05_power_80"],
                marker="o",
                linewidth=2,
                label=labels[contrast],
            )
        axis.axvline(5, color="#C84236", linestyle="--", linewidth=1.5)
        axis.set_title(
            "Fit score" if outcome == "fit_score" else "Interview recommendation"
        )
        axis.set_xlabel("Repeated calls per resume")
        axis.set_ylabel("Minimum detectable effect")
        axis.grid(alpha=0.2)
        axis.legend(frameon=False)
    figure.suptitle(
        "Five repetitions improve precision, with diminishing returns",
        fontsize=14,
        fontweight="bold",
    )
    figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image_format = output_path.suffix.lstrip(".") or "svg"
    figure.savefig(output_path, format=image_format, bbox_inches="tight")
    plt.close(figure)


def write_report(table: pd.DataFrame, report_path: Path) -> None:
    displayed = table[
        [
            "outcome",
            "contrast",
            "target_effect",
            "mde_alpha_05_power_80",
            "mde_bonferroni_12_power_80",
            "power_at_target_alpha_05",
        ]
    ].copy()
    for column in displayed.columns[2:]:
        displayed[column] = displayed[column].map(lambda value: f"{value:.3f}")

    report = [
        "# Power analysis for the 640-evaluation core audit",
        "",
        "This planning analysis was fixed before any live-model output was observed. "
        "The mock provider validates code and cannot estimate real model variance.",
        "",
        "## Actual core design",
        "",
        "- 32 independent matched base profiles",
        "- 4 treatment cells per profile",
        "- 128 unique resumes",
        "- 5 repeated calls per resume",
        "- 640 primary live evaluations",
        "",
        "The independent unit is the matched base profile. Primary uncertainty is "
        "clustered by `matched_set_id`, not by individual model call.",
        "",
        "## Variance assumptions",
        "",
        "The calculation separates condition-level variation from repeated-call noise. "
        "For fit score, the assumed standard deviations are 0.40 across treatment cells "
        "within a profile and 0.60 across repeated calls to the same resume. For interview "
        "recommendation, the corresponding probability-scale assumptions are 0.15 and 0.35. "
        "These values are planning assumptions, not observed facts.",
        "",
        "## Results",
        "",
        displayed.to_markdown(index=False),
        "",
        "Under the assumptions, 640 evaluations provide at least 80% power for the planned "
        "0.30-point fit-score main effect and 0.15 recommendation-probability main effect. "
        "Power is weaker for small frontline interactions. The design is powered for "
        "interaction effects near 0.50 fit-score points and about 0.22 probability, not "
        "subtle subgroup effects.",
        "",
        "The Bonferroni column is a conservative reference for 12 primary outcome-term tests. "
        "The preregistered analysis uses Benjamini-Hochberg correction and reports unadjusted "
        "confidence intervals alongside adjusted q-values.",
        "",
        "## Why five repetitions",
        "",
        "Repeating the same resume reduces call-level noise and measures model instability. "
        "The largest precision gains occur between one and five calls. Later calls have "
        "diminishing returns because condition-level variation remains. Five calls are a "
        "defensible stability choice, but adequacy depends on the realized variance reported "
        "after the run.",
        "",
        "![Minimum detectable effect by repetitions](figures/power_by_repetitions.svg)",
        "",
        "## Limits",
        "",
        "Analytic power uses a two-sided t-test approximation with 32 independent matched "
        "profiles. It depends on uncertain variance assumptions. The final report will compare "
        "these assumptions with observed "
        "repeated-call variance. The sample and stopping rule will not change in response to live "
        "treatment estimates.",
        "",
        "Reproduce with `python scripts/power_analysis.py`.",
        "",
    ]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run core-audit power calculations.")
    parser.add_argument("--matched-sets", type=int, default=32)
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--output-dir", default="results/design")
    parser.add_argument("--report", default="docs/power_analysis.md")
    parser.add_argument("--figure", default="docs/figures/power_by_repetitions.svg")
    args = parser.parse_args()

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    table = build_power_table(args.matched_sets, args.repetitions)
    repetitions = build_repetition_table(args.matched_sets)
    table.to_csv(output / "power_analysis.csv", index=False)
    repetitions.to_csv(output / "power_by_repetitions.csv", index=False)
    make_power_figure(repetitions, Path(args.figure))
    write_report(table, Path(args.report))
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()
