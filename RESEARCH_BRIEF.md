# Research brief: LLM Hiring Bias Audit

## Project in one sentence

This study tests whether a language model changes an otherwise identical candidate's hiring evaluation when the résumé shows a 12-month career gap or a non-traditional education pathway, and whether the effect differs between frontline and knowledge-work roles.

## Research context

This project follows [The Frontline Exposure Gap](https://doi.org/10.5281/zenodo.21522366), which measures where observed AI use reaches the workforce. That paper finds that frontline occupations account for 31.7% of U.S. employment but 11.1% of task-matched AI usage.

Both projects grew out of the same operating experience. While running a 27-person manufacturing and retail business, I watched planning, procurement, pricing, and reporting digitize faster than production-floor and customer-facing work. The first project measures that adoption divide. This project studies a possible gatekeeping effect: whether models used in hiring treat career continuity and education pathway differently across occupational settings.

## Research question

The audit estimates the effects of:

1. a 12-month career gap;
2. a traditional versus non-traditional education pathway;
3. career gap × frontline occupation;
4. non-traditional education × frontline occupation.

Career interruptions and alternative education routes affect caregivers, returning workers, veterans, immigrants, career changers, and people who cannot follow a continuous full-time path. The occupational interaction matters because the same signal may be interpreted differently in operational and knowledge-work roles.

## Design

The study uses 32 synthetic base candidate profiles across eight occupations. Each profile is expanded into four treatment variants:

- no career gap, traditional education;
- 12-month career gap, traditional education;
- no career gap, non-traditional education;
- 12-month career gap, non-traditional education.

Qualifications, experience, skills, achievements, employer history, education level, target role, formatting, résumé length, and control name remain fixed within each matched set.

The design produces **128 unique résumés** and **640 planned evaluations** using one exact model ID and one locked temperature.

Primary outcomes are fit score, interview recommendation, and model confidence. The analysis uses matched-set and occupation fixed effects, standard errors clustered by matched résumé, and Benjamini-Hochberg correction across the pre-specified treatment terms.

## Current evidence

The live audit has not been run.

The deterministic core placebo completed **640 of 640 evaluations** with **0 failures** and **0 refusals**. The estimator recovered the planted career-gap effect of **−0.45** and non-traditional-education effect of **−0.15** exactly. A constant mock recommendation outcome was reported as **not estimable** rather than interpreted from noise.

See [`results/core_placebo/core_placebo_validation_report.md`](results/core_placebo/core_placebo_validation_report.md).

These results validate the pipeline and estimator. They do not describe a deployed model, employer, or applicant.

## Failed name pretest

A separate perceived-name extension used 150 respondents and 1,200 complete ratings. The stimuli failed the locked balance thresholds for familiarity, perceived socioeconomic status, and unusualness. The export also lacked consent and attention-check fields.

The thresholds were not changed after seeing the results. The name extension remains blocked pending a replacement study. Names are treated as perceived signals, not evidence of anyone's identity.

## Current scope

The current study includes:

- external preregistration before the first live request;
- the 640-evaluation core audit;
- pre-specified models and failure checks;
- a public run manifest, synthetic audit data, tables, figures, code, and paper.

A replacement name study, live name-signal extension, human hiring-manager benchmark, and multi-model replication are separate future projects.

## Research practice shown in the repository

- matched experimental audit design;
- Python data pipelines and validation tests;
- clustered inference and fixed-effects models;
- external preregistration enforced in code;
- full retention of failures, refusals, prompts, and run metadata;
- reporting of failed validation and non-estimable outcomes without changing the rules after seeing results.

<!-- label refresh -->
