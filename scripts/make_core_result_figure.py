#!/usr/bin/env python3
"""Create the main coefficient figure from completed core-audit results."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PLOTTED_CONTRASTS = {
    "career_gap_knowledge": "12-month gap, knowledge work",
    "career_gap_frontline": "12-month gap, frontline",
    "nontraditional_knowledge": "Non-traditional education, knowledge work",
    "nontraditional_frontline": "Non-traditional education, frontline",
}


def make_figure(effect_sizes: pd.DataFrame, output_path: Path) -> None:
    required = {
        "outcome",
        "contrast",
        "estimate",
        "ci_95_low",
        "ci_95_high",
    }
    missing = required - set(effect_sizes.columns)
    if missing:
        raise ValueError(f"Effect-size table is missing columns: {sorted(missing)}")
    plotted = (
        effect_sizes[
            effect_sizes["outcome"].eq("fit_score")
            & effect_sizes["contrast"].isin(PLOTTED_CONTRASTS)
        ]
        .set_index("contrast")
        .reindex(PLOTTED_CONTRASTS)
    )
    if plotted[["estimate", "ci_95_low", "ci_95_high"]].isna().any().any():
        raise ValueError("The fit-score table does not contain all four planned contrasts.")

    estimates = plotted["estimate"].to_numpy()
    lower = plotted["ci_95_low"].to_numpy()
    upper = plotted["ci_95_high"].to_numpy()
    positions = list(range(len(plotted)))

    figure, axis = plt.subplots(figsize=(10.5, 5.8))
    axis.errorbar(
        estimates,
        positions,
        xerr=[estimates - lower, upper - estimates],
        fmt="o",
        color="#22314E",
        ecolor="#5A6A85",
        markersize=8,
        capsize=4,
        linewidth=2,
    )
    axis.axvline(0, color="#C84236", linewidth=1.5)
    axis.set_yticks(
        positions,
        [PLOTTED_CONTRASTS[item] for item in plotted.index],
    )
    axis.invert_yaxis()
    axis.set_xlabel("Change in fit score, with 95% confidence interval")
    axis.set_title(
        "Career-gap and education-pathway effects",
        loc="left",
        fontsize=15,
        fontweight="bold",
        pad=34,
    )
    axis.text(
        0,
        1.012,
        "Negative values indicate a lower model evaluation",
        transform=axis.transAxes,
        color="#5A6475",
        fontsize=10,
    )
    axis.grid(axis="x", alpha=0.18)
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.tick_params(axis="y", length=0)
    figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image_format = output_path.suffix.lstrip(".") or "svg"
    figure.savefig(output_path, format=image_format, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the primary live-result figure.")
    parser.add_argument(
        "--input",
        default="outputs/core/analysis/core_effect_sizes.csv",
    )
    parser.add_argument(
        "--output",
        default="outputs/core/analysis/core_treatment_effects.svg",
    )
    args = parser.parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(
            f"No core effect-size table at {input_path}. Run the live audit and analysis first."
        )
    make_figure(pd.read_csv(input_path), Path(args.output))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
