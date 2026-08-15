#!/usr/bin/env python3
"""Build deterministic treatment-construction and resume-balance checks."""

from __future__ import annotations

import argparse
from pathlib import Path

from compas_audit.balance import (
    build_balance_check_table,
    build_resume_metric_table,
    summarize_metrics_by_condition,
)
from compas_audit.generate import generate_resume_permutations


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit matched resume balance.")
    parser.add_argument("--config", default="config/core_audit.yaml")
    parser.add_argument("--templates", default="data/templates/resume_templates.csv")
    parser.add_argument("--output-dir", default="results/design")
    args = parser.parse_args()

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    resumes = generate_resume_permutations(args.config, args.templates)
    metrics = build_resume_metric_table(resumes)
    checks = build_balance_check_table(metrics)
    summary = summarize_metrics_by_condition(metrics)

    metrics.to_csv(output / "resume_text_metrics.csv", index=False)
    checks.to_csv(output / "resume_balance_checks.csv", index=False)
    summary.to_csv(output / "resume_balance_by_condition.csv", index=False)

    report = [
        "# Resume treatment balance report",
        "",
        "This report is deterministic and was generated before any live-model output.",
        "",
        "## Exact within-set checks",
        "",
        checks.to_markdown(index=False),
        "",
        "## Mean text metrics by treatment cell",
        "",
        summary.to_markdown(index=False),
        "",
        "The readability score may move slightly because the treatment wording is the "
        "signal being manipulated. Skills, experience, achievements, names, occupation, "
        "and all non-treatment text remain fixed within each matched set.",
        "",
    ]
    (output / "resume_balance_report.md").write_text(
        "\n".join(report),
        encoding="utf-8",
    )
    if not checks["pass"].all():
        failed = checks.loc[~checks["pass"], "metric"].tolist()
        raise RuntimeError(f"Resume balance checks failed: {failed}")
    print(f"Wrote resume balance checks to {output}")


if __name__ == "__main__":
    main()
