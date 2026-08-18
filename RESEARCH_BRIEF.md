# Research brief: LLM Hiring Bias Audit

## Project in one sentence

This study tests whether a language model changes an otherwise identical candidate's hiring evaluation when the résumé shows a 12-month career gap or a non-traditional education pathway, and whether the effect differs between frontline and knowledge-work roles.

## Research context

This project follows [The Frontline Exposure Gap](https://doi.org/10.2139/ssrn.7162039), which measures where observed AI use reaches the workforce. That paper finds that frontline occupations account for 31.7% of U.S. employment but 11.1% of task-matched AI usage.

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

The Claude confirmatory design produces **128 unique résumés** and **640 primary evaluations** using the exact model ID `claude-sonnet-4-6`, the primary prompt `v2.0-primary`, and temperature `0.0`.

Primary outcomes are fit score, interview recommendation, and model confidence. The analysis uses matched-set and occupation fixed effects, standard errors clustered by matched base profile, and Benjamini-Hochberg correction across 12 pre-specified linear-model tests.

The Version 2 design also fixes the treatment wording, verifies balance in résumé text, reports effect sizes and recommendation probability changes, runs a separate manipulation check, and repeats the audit under two locked prompt variants.

## Current evidence

### Gemini feasibility pilot

A non-confirmatory Gemini pilot is complete. Using `gemini-3.6-flash`, the project preserved **18 valid screening responses across all eight occupations** before the free-tier requests-per-day quota became binding.

- **18/18 returned outputs parsed successfully**;
- **0/18 were refusals**;
- **8/8 occupations were represented**;
- no Gemini outcome is used for treatment-effect inference or to alter the Claude design.

This establishes live-provider connectivity, structured-response compatibility, parser behavior, logging, and synthetic résumé execution against a real external model. It is an operational feasibility result, not a substantive hiring-bias result.

See [`docs/gemini_pilot_summary.md`](docs/gemini_pilot_summary.md).

### Claude confirmatory audit

No live Claude screening response has been collected or analyzed. The next stage is the **640-evaluation prospectively code-locked Claude Sonnet 4.6 audit**.

Before the first Claude API request, the runner creates a SHA-256 manifest of the design, prompts, provider implementation, analysis code, execution scripts, and résumé templates. The current execution is therefore described as **prospectively code-locked**, not externally preregistered.

See [`docs/claude_confirmatory_protocol.md`](docs/claude_confirmatory_protocol.md).

### Mock validation

The planning analysis gives approximate 80% power minimum detectable effects of 0.25 fit-score points and 0.11 recommendation probability for main effects. Frontline interactions need about twice those effect sizes under the stated assumptions.

The deterministic core placebo completed **640 of 640 evaluations** with **0 failures** and **0 refusals**. The estimator recovered the planted career-gap effect of **−0.45** and non-traditional-education effect of **−0.15** exactly. A constant mock recommendation outcome was reported as **not estimable** rather than interpreted from noise.

See [`results/core_placebo/core_placebo_validation_report.md`](results/core_placebo/core_placebo_validation_report.md).

These mock results validate the pipeline and estimator. They do not describe a deployed model, employer, or applicant.

## Failed name pretest

A separate perceived-name extension used 150 respondents and 1,200 complete ratings. The stimuli failed the locked balance thresholds for familiarity, perceived socioeconomic status, and unusualness. The export also lacked consent and attention-check fields.

The thresholds were not changed after seeing the results. The name extension remains blocked pending a replacement study. Names are treated as perceived signals, not evidence of anyone's identity.

## Current scope

The current research program includes:

- a completed Gemini feasibility pilot with no confirmatory use;
- a prospective SHA-256 design/code lock before the first Claude response;
- the 640-evaluation Claude primary audit;
- pre-specified models and failure checks;
- power analysis and exact treatment-balance checks;
- post-primary manipulation and prompt-robustness checks;
- a run manifest, synthetic audit data, tables, figures, code, and paper outputs.

Earlier OSF-ready materials remain in the repository as historical Version 1/Version 2 artifacts, but the current Claude execution does not claim external preregistration.

A replacement name study and live name-signal extension are separate future projects. The repository prepares, but does not claim to have completed, a human benchmark and later model-snapshot replication.

## Research practice shown in the repository

- matched experimental audit design;
- Python data pipelines and validation tests;
- clustered inference and fixed-effects models;
- prospective code/design locking before Claude outcomes;
- separation of feasibility evidence from confirmatory inference;
- full retention of failures, refusals, prompts, and run metadata;
- reporting of failed validation, quota-limited execution, and non-estimable outcomes without changing the substantive rules after seeing results.
