from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable

import pandas as pd

TREATMENT_PREFIXES = ("Education:", "Employment continuity:")
WORD_PATTERN = re.compile(r"\b[\w'-]+\b")
NUMBER_PATTERN = re.compile(r"(?<!\w)(?:\$?\d[\d,.]*%?|\d+ percentage points?)")
SENTENCE_PATTERN = re.compile(r"[.!?]+")
VOWEL_GROUP_PATTERN = re.compile(r"[aeiouy]+", re.IGNORECASE)


def _line_value(resume_text: str, prefix: str) -> str:
    for line in str(resume_text).splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()
    return ""


def invariant_resume_text(resume_text: str) -> str:
    return "\n".join(
        line
        for line in str(resume_text).splitlines()
        if not line.startswith(TREATMENT_PREFIXES)
    )


def invariant_text_hash(resume_text: str) -> str:
    return hashlib.sha256(
        invariant_resume_text(resume_text).encode("utf-8")
    ).hexdigest()


def _count_syllables(word: str) -> int:
    cleaned = re.sub(r"[^a-z]", "", word.casefold())
    if not cleaned:
        return 0
    groups = len(VOWEL_GROUP_PATTERN.findall(cleaned))
    if cleaned.endswith("e") and groups > 1:
        groups -= 1
    return max(1, groups)


def flesch_reading_ease(text: str) -> float:
    words = WORD_PATTERN.findall(str(text))
    if not words:
        return float("nan")
    sentences = max(1, len(SENTENCE_PATTERN.findall(str(text))))
    syllables = sum(_count_syllables(word) for word in words)
    return float(
        206.835
        - 1.015 * (len(words) / sentences)
        - 84.6 * (syllables / len(words))
    )


def build_resume_metric_table(resumes: pd.DataFrame) -> pd.DataFrame:
    required = {
        "resume_id",
        "matched_set_id",
        "education_pathway",
        "career_gap_months",
        "years_experience",
        "resume_text",
    }
    missing = required - set(resumes.columns)
    if missing:
        raise ValueError(f"Resume table is missing columns: {sorted(missing)}")

    records: list[dict[str, object]] = []
    for row in resumes.to_dict(orient="records"):
        text = str(row["resume_text"])
        skills = _line_value(text, "Skills:")
        achievement = _line_value(text, "Selected achievement:")
        records.append(
            {
                "resume_id": row["resume_id"],
                "matched_set_id": row["matched_set_id"],
                "education_pathway": row["education_pathway"],
                "career_gap_months": int(row["career_gap_months"]),
                "word_count": len(WORD_PATTERN.findall(text)),
                "sentence_count": max(1, len(SENTENCE_PATTERN.findall(text))),
                "skills_count": len(
                    [item for item in skills.split(";") if item.strip()]
                ),
                "years_experience": int(row["years_experience"]),
                "quantified_achievement_count": len(NUMBER_PATTERN.findall(achievement)),
                "readability_flesch": round(flesch_reading_ease(text), 3),
                "invariant_text_hash": invariant_text_hash(text),
                "education_line": _line_value(text, "Education:"),
                "continuity_line": _line_value(text, "Employment continuity:"),
            }
        )
    return pd.DataFrame.from_records(records)


def build_balance_check_table(metrics: pd.DataFrame) -> pd.DataFrame:
    invariant_metrics = (
        "skills_count",
        "years_experience",
        "quantified_achievement_count",
        "invariant_text_hash",
    )
    expected_balanced_metrics = (
        "word_count",
        "sentence_count",
    )
    checks: list[dict[str, object]] = []
    for metric in (*invariant_metrics, *expected_balanced_metrics):
        unique_counts = metrics.groupby("matched_set_id")[metric].nunique(dropna=False)
        checks.append(
            {
                "metric": metric,
                "maximum_variants_within_matched_set": int(unique_counts.max()),
                "matched_sets_with_imbalance": int((unique_counts > 1).sum()),
                "pass": bool(unique_counts.max() == 1),
            }
        )
    return pd.DataFrame(checks)


def summarize_metrics_by_condition(
    metrics: pd.DataFrame,
    metric_names: Iterable[str] = (
        "word_count",
        "sentence_count",
        "skills_count",
        "years_experience",
        "quantified_achievement_count",
        "readability_flesch",
    ),
) -> pd.DataFrame:
    return (
        metrics.groupby(
            ["education_pathway", "career_gap_months"],
            as_index=False,
        )[list(metric_names)]
        .mean(numeric_only=True)
        .sort_values(["education_pathway", "career_gap_months"])
    )
