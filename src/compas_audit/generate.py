from __future__ import annotations

import argparse
import hashlib
import itertools
from pathlib import Path

import pandas as pd

from .common import load_config, stable_id


def _build_qualification_hash(resume_template: pd.Series) -> str:
    qualification_fields = [
        "occupation_id",
        "target_role",
        "years_experience",
        "education",
        "skills",
        "employer_history",
        "experience_summary",
        "achievement",
    ]
    qualification_text = "\n".join(
        str(resume_template.get(field_name, ""))
        for field_name in qualification_fields
    )
    return hashlib.sha256(qualification_text.encode("utf-8")).hexdigest()


def _build_treatment_descriptions(
    education_pathway: str,
    career_gap_months: int,
    education_credential: str,
) -> tuple[str, str]:
    education_pathway_description = (
        f"Traditional pathway; completed {education_credential} through full-time study"
        if education_pathway == "traditional"
        else f"Non-traditional pathway; completed {education_credential} through part-time study"
    )
    employment_continuity_description = (
        "Continuous work history; no career break was recorded"
        if career_gap_months == 0
        else "Twelve-month career break; return to work was completed"
    )
    return education_pathway_description, employment_continuity_description


def render_resume_text(
    resume_template: pd.Series,
    candidate_name: str,
    education_pathway: str,
    career_gap_months: int,
) -> str:
    education_description, continuity_description = _build_treatment_descriptions(
        education_pathway,
        career_gap_months,
        str(resume_template["education"]),
    )
    return "\n".join(
        [
            f"Candidate: {candidate_name}",
            f"Target role: {resume_template['target_role']}",
            f"Experience: {resume_template['years_experience']} years",
            f"Education: {education_description}",
            f"Employment continuity: {continuity_description}",
            f"Skills: {resume_template['skills']}",
            f"Employer history: {resume_template['employer_history']}",
            f"Experience summary: {resume_template['experience_summary']}",
            f"Selected achievement: {resume_template['achievement']}",
        ]
    )


def generate_resume_permutations(
    config_path: str,
    templates_path: str,
) -> pd.DataFrame:
    audit_config = load_config(config_path)
    resume_templates = pd.read_csv(templates_path)
    candidate_names_by_signal = audit_config["signals"]["names"]
    education_pathways = audit_config["signals"]["education_pathway"]
    career_gap_options = audit_config["signals"]["career_gap_months"]

    resume_records: list[dict[str, object]] = []
    for _, resume_template in resume_templates.iterrows():
        profile_slot = int(resume_template["profile_slot"])
        for name_signal_group, candidate_names in candidate_names_by_signal.items():
            if len(candidate_names) < 2:
                raise ValueError(
                    f"{name_signal_group} must contain at least two candidate names."
                )
            candidate_name = candidate_names[
                (profile_slot - 1) % len(candidate_names)
            ]
            for education_pathway, career_gap_months in itertools.product(
                education_pathways,
                career_gap_options,
            ):
                matched_set_id = str(resume_template["matched_set_id"])
                resume_id = stable_id(
                    matched_set_id,
                    name_signal_group,
                    education_pathway,
                    career_gap_months,
                )
                resume_text = render_resume_text(
                    resume_template,
                    candidate_name,
                    education_pathway,
                    int(career_gap_months),
                )
                resume_records.append(
                    {
                        "resume_id": resume_id,
                        "matched_set_id": matched_set_id,
                        "base_profile_id": resume_template["base_profile_id"],
                        "profile_slot": profile_slot,
                        "template_id": resume_template["template_id"],
                        "occupation_id": resume_template["occupation_id"],
                        "occupation_tier": resume_template["occupation_tier"],
                        "target_role": resume_template["target_role"],
                        "onet_soc_code": resume_template.get("onet_soc_code", ""),
                        "onet_title": resume_template.get("onet_title", ""),
                        "source_url": resume_template.get("source_url", ""),
                        "signal_group": name_signal_group,
                        "candidate_name": candidate_name,
                        "education_pathway": education_pathway,
                        "career_gap_months": int(career_gap_months),
                        "years_experience": int(
                            resume_template["years_experience"]
                        ),
                        "qualification_hash": _build_qualification_hash(
                            resume_template
                        ),
                        "resume_word_count": len(resume_text.split()),
                        "resume_text": resume_text,
                    }
                )

    resume_permutations = pd.DataFrame.from_records(resume_records)
    if resume_permutations.empty:
        raise ValueError("No resume permutations were generated.")

    expected_resumes_per_matched_set = (
        len(candidate_names_by_signal)
        * len(education_pathways)
        * len(career_gap_options)
    )
    matched_set_sizes = resume_permutations.groupby("matched_set_id").size()
    if not matched_set_sizes.eq(expected_resumes_per_matched_set).all():
        raise ValueError(
            "Treatment allocation is incomplete within one or more matched sets."
        )
    qualification_variants_per_set = resume_permutations.groupby(
        "matched_set_id"
    )["qualification_hash"].nunique()
    if qualification_variants_per_set.max() != 1:
        raise ValueError("Qualifications changed within a matched set.")

    return resume_permutations.sort_values(
        [
            "occupation_id",
            "matched_set_id",
            "signal_group",
            "education_pathway",
            "career_gap_months",
        ]
    ).reset_index(drop=True)


# keep older scripts working
def build_resume_text(
    row: pd.Series,
    name: str,
    education_pathway: str,
    gap_months: int,
) -> str:
    return render_resume_text(
        row,
        name,
        education_pathway,
        gap_months,
    )


def generate_permutations(
    config_path: str,
    templates_path: str,
) -> pd.DataFrame:
    return generate_resume_permutations(config_path, templates_path)


def main() -> None:
    argument_parser = argparse.ArgumentParser(
        description="Generate matched synthetic resume permutations."
    )
    argument_parser.add_argument("--config", default="config/audit.yaml")
    argument_parser.add_argument(
        "--templates",
        default="data/templates/resume_templates.csv",
    )
    command_args = argument_parser.parse_args()

    audit_config = load_config(command_args.config)
    output_path = Path(
        audit_config.get(
            "output_resumes",
            "outputs/resume_permutations.csv",
        )
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    resume_permutations = generate_resume_permutations(
        command_args.config,
        command_args.templates,
    )
    resume_permutations.to_csv(output_path, index=False)
    print(f"wrote {len(resume_permutations)} resumes to {output_path}")


if __name__ == "__main__":
    main()
