# LLM Hiring Bias Audit

A preregistration-ready matched-résumé audit of whether a language model changes its hiring evaluation when qualifications remain fixed but a résumé reports a career gap or a non-traditional education pathway.

> **Study status:** The design and analysis pipeline are complete and mock-validated. No live Anthropic model response has been collected or analyzed. This repository therefore reports design-validation results, not evidence of bias in a deployed model.

## Research question

Does a résumé-screening language model respond differently to otherwise equivalent candidates when a résumé reports:

1. a 12-month career gap;
2. a non-traditional education pathway;
3. either signal in a frontline rather than knowledge-work occupation?

The estimand is the change in a model's structured screening output caused by a controlled résumé signal. It is not an estimate of employer behavior, applicant outcomes, intent, or unlawful discrimination.

## Research program

Version 2 extends Version 1. Both designs and their full history remain in the repository.

| Version | Scope | Current status |
|---|---|---|
| **Version 1: original audit framework** | Core career-gap and education audit, plus a gated perceived-name-signal extension | Pipeline validated; name extension blocked by its failed pretest |
| **Version 2: robustness extension** | Power analysis, treatment-balance tests, prompt replications, manipulation checks, effect sizes, and stronger run controls | Design complete; external preregistration and live run pending |

### Version 1: original framework

Version 1 established the résumé generator, matched experimental design, randomized execution, provider interface, structured parser, failure retention, fixed-effects analysis, and deterministic placebo tests.

It contains two related tracks:

- **Core study:** 32 matched profiles, 128 résumés, and 640 planned model evaluations.
- **Perceived-name-signal extension:** 512 résumés and 2,560 planned evaluations across four name-signal groups.

The name-signal extension has not run. Its first human pretest included 150 respondents and 1,200 complete ratings. The stimuli failed the locked balance rules for familiarity, perceived socioeconomic status, and unusualness. Consent and attention-check fields were also absent. The thresholds were not relaxed after the data were reviewed.

Version 1 files remain available in [`config/audit.yaml`](config/audit.yaml), [`docs/preregistration.md`](docs/preregistration.md), and [`docs/deviations_from_preregistration.md`](docs/deviations_from_preregistration.md).

### Version 2: robustness extension

Version 2 retains the Version 1 core estimand and adds the following prospective safeguards before any live-model observation:

- scenario-based power analysis for the actual 640-evaluation design;
- exact treatment-wording documentation and automated résumé balance tests;
- an occupation-selection rationale using wages, education, employment scale, and observed AI exposure;
- one preregistered primary prompt and two prompt-robustness replications;
- a separate post-primary manipulation check;
- standardized effects, confidence intervals, and recommendation probability changes;
- repeated-call variance, failure, and refusal reporting;
- a blinded human-benchmark protocol and a later model-snapshot replication protocol;
- overwrite protection, preregistration hashes, and a guarded live-run workflow.

These changes were made before any live Anthropic output was observed.

## Live execution extension

The existing Version 1 and Version 2 materials remain preserved. A separate execution layer is prepared for the first live-model evidence:

- a **32-call Gemini feasibility pilot** for API, parser, refusal, failure, and latency checks only;
- a **640-call Claude Sonnet 4.6 confirmatory audit** using the existing Version 2 matched-résumé design;
- the existing Claude manipulation check and two prompt-robustness runs after the primary confirmatory sample is attempted;
- separate output directories so the live execution cannot overwrite historical validation artifacts.

The Gemini pilot is non-confirmatory and cannot be used to revise the Claude design. The Claude execution plan is documented separately in [`docs/osf_preregistration_claude_confirmatory.md`](docs/osf_preregistration_claude_confirmatory.md).

## Experimental design

| Design element | Specification |
|---|---|
| Occupational sample | Eight purposively selected occupations: four frontline or operational and four knowledge-work roles |
| Base profiles | Four profiles per occupation, yielding 32 matched sets |
| Career-gap treatment | No stated gap versus a standardized 12-month gap |
| Education treatment | Traditional versus standardized non-traditional pathway |
| Unique résumés | 128 in the core study |
| Repeated evaluations | Five calls per résumé |
| Confirmatory sample | 640 model evaluations |
| Primary outcomes | Fit score, interview recommendation, and model confidence |
| Model configuration | One exact model ID, one primary prompt, and temperature 0.0 |

Each matched profile produces four résumé variants:

| | Traditional education | Non-traditional education |
|---|---:|---:|
| No career gap | Control | Education treatment |
| 12-month career gap | Gap treatment | Combined treatment |

Within a matched set, the candidate name, target role, experience, skills, achievements, employer history, credential level, field, formatting, and non-treatment text remain fixed.

## Occupational sample

| Frontline or operational | Knowledge work |
|---|---|
| Production supervisors | Management analysts |
| Registered nurses | Project management specialists |
| Maintenance workers | Computer systems analysts |
| Logisticians | Financial analysts |

The sample is designed to create occupational contrast, not population representativeness. It spans median annual wages of roughly $49,600 to $105,900, multiple education pathways, and observed AI exposure from zero to 0.572. The complete rationale and sources are in [`docs/occupation_selection.md`](docs/occupation_selection.md).

## Statistical analysis

For outcome `Y`, the preregistered linear specification is:

```text
Y = β1(non-traditional education)
  + β2(career gap)
  + β3(non-traditional education × frontline)
  + β4(career gap × frontline)
  + occupation fixed effects
  + matched-set fixed effects
  + temperature fixed effects
  + error
```

- Fit score and confidence use linear models.
- Interview recommendation uses a linear probability model for percentage-point interpretation.
- Logistic regression is a robustness check when the outcome has sufficient variation.
- Standard errors are clustered by `matched_set_id`, the independent matched-profile unit.
- Benjamini-Hochberg correction covers 12 confirmatory tests: four terms across three primary outcomes.
- Results report point estimates, clustered standard errors, 95% confidence intervals, standardized effects, raw p-values, adjusted q-values, and recommendation probability changes.
- Every failed request, refusal, parser error, and raw response remains in the audit record. Selective reruns are prohibited.

Occupation-specific estimates are descriptive. The study is not powered for a large set of occupation-level hypothesis tests.

## Power analysis

The pre-run calculation separates treatment-cell variation from repeated-call noise and uses a two-sided t-test approximation with 32 independent matched profiles.

| Contrast | Fit-score MDE | Recommendation-probability MDE |
|---|---:|---:|
| Main effect | 0.25 points | 0.11 |
| Frontline interaction | 0.49 points | 0.22 |

These are 80% power minimum detectable effects under stated planning assumptions. They are not observed variance estimates. The design has reasonable power for moderate main effects but limited power for subtle occupational interactions.

![Minimum detectable effect by repetitions](docs/figures/power_by_repetitions.svg)

Assumptions and calculations: [`docs/power_analysis.md`](docs/power_analysis.md).

## Treatment validity and robustness

### Résumé balance

All 32 matched sets pass the deterministic pre-run checks for:

- word and sentence counts;
- skills count and years of experience;
- quantified-achievement count;
- the SHA-256 hash of all non-treatment text.

The exact treatment text is in [`docs/treatment_construction.md`](docs/treatment_construction.md). The generated balance report is in [`results/design/resume_balance_report.md`](results/design/resume_balance_report.md).

### Manipulation check

After the 640 primary observations are attempted, a separate factual prompt asks the same model to identify the stated career-gap duration and education pathway. This distinguishes a substantive null result from a case in which the model did not register the treatment.

### Prompt robustness

The primary prompt is `v2.0-primary`. Two post-primary replications, `v2.0-concise` and `v2.0-rubric`, reuse the same résumés, exact model ID, temperature, response schema, and five-call stopping rule. They are robustness analyses and cannot replace the primary estimate.

## Pipeline validation

The deterministic mock provider tests generation, randomization, parsing, repeated calls, model fitting, and reporting. It completed 640 of 640 core evaluations with no failures or refusals and recovered the planted fit-score effects exactly.

| Term | Planted effect | Recovered effect |
|---|---:|---:|
| 12-month career gap | -0.450 | -0.450 |
| Non-traditional education | -0.150 | -0.150 |
| Career gap × frontline | 0.000 | 0.000 |
| Education pathway × frontline | 0.000 | 0.000 |

The mock recommendation outcome is constant, so the recommendation model is reported as not estimable. These results validate the software and estimator only. They are not findings about a language model, employer, or applicant.

Validation report: [`results/core_placebo/core_placebo_validation_report.md`](results/core_placebo/core_placebo_validation_report.md).

## Preregistration and live-run gate

The OSF-ready registration is prepared but has not been externally submitted. The live runner requires a permanent HTTPS OSF or AsPredicted URL and records it in each observation and run manifest. The exact model ID must also be fixed before execution.

Relevant files:

- [`docs/osf_preregistration.md`](docs/osf_preregistration.md)
- [`docs/core_audit_preregistration.md`](docs/core_audit_preregistration.md)
- [`docs/preregistration_lock.json`](docs/preregistration_lock.json)
- [`docs/external_preregistration_checklist.md`](docs/external_preregistration_checklist.md)

## Reproducibility

### Validate the design without live API calls

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
make v2-validate
```

This runs the power analysis, résumé balance audit, 640-evaluation mock pipeline, 128 manipulation-check tests, and automated test suite.

### Run after external preregistration

```bash
pip install -e ".[api,dev]"
export EXTERNAL_PREREGISTRATION_URL="https://osf.io/xxxxx"
export ANTHROPIC_API_KEY="set-securely-outside-git"
export ANTHROPIC_MODEL="exact-model-id"
make v2-live
```

The live program runs the 640 primary evaluations first, then the manipulation check and two prompt replications. It preserves every attempt and refuses to overwrite existing live output.

A guarded manual GitHub Actions workflow is also included. Store `ANTHROPIC_API_KEY` as a repository secret, then supply the permanent registration URL, exact model ID, and `PREREGISTERED` confirmation through **Actions > Live audit**.

## Interpretation and limitations

This audit can estimate whether controlled résumé signals change one model's outputs under one fixed configuration. It cannot establish:

- effects on real applicants or hiring decisions;
- employer discrimination or legal liability;
- model intent;
- demographic identity from a person's name;
- representativeness across occupations, models, prompts, providers, dates, or deployment settings.

The eight occupations form a purposive contrast sample. Synthetic résumés simplify real application materials. Repeated calls measure instability within the locked setup, not across deployment environments. Explanations generated by the model are secondary outcomes.

Full limitations: [`docs/limitations.md`](docs/limitations.md).

## Planned extensions

- collect a successful independent name-perception pretest before any name-signal audit;
- compare model and blinded human evaluations using [`docs/human_baseline_protocol.md`](docs/human_baseline_protocol.md);
- replicate the registered design on a later model snapshot using [`docs/model_replication_protocol.md`](docs/model_replication_protocol.md).

These extensions are separate studies and will not be folded into the confirmatory Version 2 result after outcomes are observed.

## Repository map

| Path | Purpose |
|---|---|
| [`config/`](config/) | Locked study configurations |
| [`data/templates/`](data/templates/) | Synthetic base résumé templates |
| [`data/occupations/`](data/occupations/) | Occupation registry and exposure snapshot |
| [`src/compas_audit/`](src/compas_audit/) | Generation, execution, validation, and analysis code |
| [`scripts/`](scripts/) | Reproduction, power, robustness, and live-run entry points |
| [`docs/`](docs/) | Preregistrations, methods, ethics, and protocols |
| [`results/`](results/) | Committed design and mock-validation outputs |

## Citation

See [`CITATION.cff`](CITATION.cff), or:

```bibtex
@misc{nandhakumar2026audit,
  author = {Nandhakumar, Sriramkrishnan},
  title  = {LLM Hiring Bias Audit},
  year   = {2026},
  url    = {https://github.com/raamnandhakumar-eng/llm-hiring-bias-audit}
}
```

MIT licensed. Contact: Sriramkrishnan “Raam” Nandhakumar, raam.nandhakumar@gmail.com.

The public project and Python distribution are named `llm-hiring-bias-audit`. The internal import namespace remains `compas_audit` to preserve compatibility with validated historical scripts.
