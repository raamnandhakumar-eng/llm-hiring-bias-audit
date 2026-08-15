#!/usr/bin/env python3
"""Combine live effect estimates across the three preregistered prompts."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize prompt robustness outputs.")
    parser.add_argument("--core-dir", default="outputs/core")
    parser.add_argument("--output-dir", default="outputs/core/prompt_robustness")
    args = parser.parse_args()
    core = Path(args.core_dir)
    output = Path(args.output_dir)
    sources = {
        "Primary": core / "analysis" / "core_effect_sizes.csv",
        "Concise": output / "concise" / "analysis" / "core_effect_sizes.csv",
        "Rubric": output / "rubric" / "analysis" / "core_effect_sizes.csv",
    }
    missing = [str(path) for path in sources.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing prompt analysis files: {missing}")

    tables = []
    for prompt, path in sources.items():
        table = pd.read_csv(path)
        table.insert(0, "prompt", prompt)
        tables.append(table)
    combined = pd.concat(tables, ignore_index=True)
    output.mkdir(parents=True, exist_ok=True)
    combined.to_csv(output / "prompt_effect_size_comparison.csv", index=False)

    plotted = combined[
        combined["outcome"].eq("fit_score")
        & combined["contrast"].isin(
            {
                "career_gap_knowledge",
                "career_gap_frontline",
                "nontraditional_knowledge",
                "nontraditional_frontline",
            }
        )
    ].copy()
    labels = {
        "career_gap_knowledge": "Career gap, knowledge",
        "career_gap_frontline": "Career gap, frontline",
        "nontraditional_knowledge": "Non-traditional, knowledge",
        "nontraditional_frontline": "Non-traditional, frontline",
    }
    prompts = ["Primary", "Concise", "Rubric"]
    contrasts = list(labels)
    figure, axis = plt.subplots(figsize=(10, 6))
    offsets = {"Primary": -0.18, "Concise": 0.0, "Rubric": 0.18}
    for prompt in prompts:
        group = plotted[plotted["prompt"].eq(prompt)].set_index("contrast")
        y = [index + offsets[prompt] for index in range(len(contrasts))]
        estimate = [group.loc[contrast, "estimate"] for contrast in contrasts]
        low = [group.loc[contrast, "ci_95_low"] for contrast in contrasts]
        high = [group.loc[contrast, "ci_95_high"] for contrast in contrasts]
        axis.errorbar(
            estimate,
            y,
            xerr=[
                [estimate[i] - low[i] for i in range(len(estimate))],
                [high[i] - estimate[i] for i in range(len(estimate))],
            ],
            fmt="o",
            capsize=3,
            label=prompt,
        )
    axis.axvline(0, color="#C84236", linewidth=1.2)
    axis.set_yticks(range(len(contrasts)), [labels[item] for item in contrasts])
    axis.set_xlabel("Change in fit score with 95% confidence interval")
    axis.set_title("Treatment estimates across three hiring prompts")
    axis.legend(frameon=False)
    axis.grid(axis="x", alpha=0.2)
    figure.tight_layout()
    figure.savefig(output / "prompt_robustness_coefficients.svg", bbox_inches="tight")
    plt.close(figure)
    print(f"Wrote prompt comparison to {output}")


if __name__ == "__main__":
    main()
