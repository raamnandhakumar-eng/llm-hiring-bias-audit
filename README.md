# LLM Hiring Bias Audit

**Question:** Does a language model evaluate an otherwise identical candidate differently when a résumé shows a 12-month career gap or a non-traditional education pathway?

**Status:** Version 1 and the Version 2 extension are preserved in this repository. Both pipelines are mock-validated. **No live Anthropic audit has been run, so this repository reports no finding about a deployed model.**

**Interpretation rule:** Any live estimate will describe one exact model snapshot, prompt, date, and synthetic sample. It will not establish employer behavior, intent, unlawful discrimination, or effects on real applicants.

## Versions

| Version | Purpose | Status |
|---|---|---|
| **Version 1: original audit framework** | Builds the matched-résumé pipeline and the gated perceived-name-signal study | Preserved and mock-validated; live name extension blocked by the failed pretest |
| **Version 2: robustness extension** | Strengthens the 640-evaluation career-gap and education-pathway study before a live run | Code complete; external preregistration and live run pending |

Version 2 extends Version 1. It does not replace or rewrite the original design history.

## Version 1: original audit framework

Version 1 established the experiment, résumé generator, provider interface, structured parser, randomized execution, failure retention, fixed-effects analysis, and deterministic placebo validation.

It contains two linked study tracks:

- **Core audit:** 32 matched base profiles across eight occupations, four career-gap and education-pathway variants per profile, and five calls per résumé. This produces 128 résumés and 640 planned evaluations.
- **Perceived-name-signal extension:** four name-signal groups added to the same design. This produces 512 résumés and 2,560 planned evaluations.

The name extension remains blocked. Its human pretest included 150 respondents and 1,200 complete ratings, but the stimuli failed the locked familiarity, socioeconomic-status, and unusualness balance rules. Consent and attention-check fields were also missing. The thresholds were not relaxed.

Version 1 remains available through:

- [`config/audit.yaml`](config/audit.yaml) and [`docs/preregistration.md`](docs/preregistration.md) for the 2,560-evaluation name extension;
- [`config/core_audit.yaml`](config/core_audit.yaml) and [`docs/core_audit_preregistration.md`](docs/core_audit_preregistration.md) for the 640-evaluation core audit;
- [`docs/deviations_from_preregistration.md`](docs/deviations_from_preregistration.md) for the full design history;
- the original and core placebo results under [`results/`](results/).

## Version 2: robustness extension

Version 2 keeps the Version 1 core design and adds stronger pre-run validation, robustness checks, and reporting. The primary design remains 32 matched profiles, 128 résumés, and 640 evaluations.

### What Version 2 adds

| Upgrade | Implementation |
|---|---|
| Power analysis | MDEs, assumed variance, achieved power, and a repetition curve for the actual 640-evaluation design |
| Occupation selection | A documented contrast across work setting, wages, education, employment scale, and observed AI exposure |
| Treatment construction | Exact control and treatment wording with all other résumé content held fixed |
| Text balance | Automated checks for length, skills, experience, achievements, readability, and non-treatment text |
| Manipulation check | A separate post-primary prompt tests whether the model identifies the gap and education pathway |
| Prompt robustness | Two locked alternate hiring prompts run after the primary prompt |
| Effect sizes | Mean differences, 95% confidence intervals, standardized effects, and recommendation probability changes |
| Headline figure | A coefficient plot generated from live results, never from mock output presented as a finding |
| Human benchmark | Blinded assignment protocol and validation/analysis script |
| Model replication | A separate protocol for a later model snapshot |

## Version 2 power analysis

Under the fixed planning assumptions, the approximate 80% power minimum detectable effects are:

- **0.25 fit-score points** and **0.11 recommendation probability** for the two main effects;
- **0.49 fit-score points** and **0.22 recommendation probability** for frontline interactions.

Five calls per résumé improve precision and measure response instability. The curve also shows diminishing gains after the fifth call. These are planning assumptions, not observed model variance.

![Minimum detectable effect by repetitions](docs/figures/power_by_repetitions.svg)

Full calculation: [`docs/power_analysis.md`](docs/power_analysis.md).

## Shared core experimental design

Each of 32 base profiles is expanded into this 2 by 2 design:

| | Traditional education | Non-traditional education |
|---|---:|---:|
| No career gap | control | education treatment |
| 12-month career gap | gap treatment | combined treatment |

This creates 128 unique résumés. The five repeated calls produce 640 primary evaluations. One name is fixed within each matched set, and the core audit estimates no name effect.

The primary outcomes are:

- fit score from 1 to 10;
- interview recommendation as 0 or 1;
- model confidence from 0 to 1.

The primary analysis uses matched-set and occupation fixed effects. Standard errors are clustered by `matched_set_id`, the independent matched base profile. Benjamini-Hochberg correction covers the four locked terms across the three primary linear models.

## Eight-occupation contrast

The purposive sample contains four frontline or operational roles and four knowledge-work roles. It spans median wages from about $49,600 to $105,900, several education pathways, and observed AI exposure from zero to 0.572.

The roles and the selection rule are documented in [`docs/occupation_selection.md`](docs/occupation_selection.md). This is a structured contrast sample, not a representative sample of all U.S. occupations.

## Treatment balance

All 32 matched sets pass the exact pre-run checks:

- identical word and sentence counts;
- identical skills count and years of experience;
- identical quantified-achievement count;
- identical SHA-256 hash for all non-treatment text.

The exact wording is in [`docs/treatment_construction.md`](docs/treatment_construction.md), and the generated report is in [`results/design/resume_balance_report.md`](results/design/resume_balance_report.md).

## Mock validation, not a finding

The deterministic mock run completed 640 of 640 evaluations with no failures or refusals. It recovered the planted fit-score effects exactly:

| Treatment | Planted | Recovered |
|---|---:|---:|
| 12-month career gap | -0.450 | -0.450 |
| Non-traditional education | -0.150 | -0.150 |
| Career gap x frontline | 0.000 | 0.000 |
| Education pathway x frontline | 0.000 | 0.000 |

This validates the software and estimator only. It is not evidence about any model, employer, or applicant. See [`results/core_placebo/core_placebo_validation_report.md`](results/core_placebo/core_placebo_validation_report.md).

## Version 2 preregistration and live run

The live runner refuses to send a request without a permanent OSF or AsPredicted registration URL. Submit [`docs/osf_preregistration.md`](docs/osf_preregistration.md), record the public URL, and lock the exact model ID before running.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[api,dev]"

make v2-validate
make prereg-lock

export EXTERNAL_PREREGISTRATION_URL="https://osf.io/xxxxx"
export ANTHROPIC_API_KEY="set-securely-outside-git"
export ANTHROPIC_MODEL="exact-model-id"
make v2-live
```

`make v2-live` runs in this fixed sequence:

1. 640 primary evaluations with `v2.0-primary`;
2. primary analysis and coefficient figure;
3. 128 separate manipulation-check calls;
4. two prompt replications of 640 evaluations each;
5. a cross-prompt coefficient comparison.

Raw responses, failures, refusals, prompts, exact model ID, timestamps, trial numbers, latency, parser status, and manifests are preserved. Selective reruns are prohibited. API credentials must never be committed.

### Run through GitHub Actions

After merging Version 2, add `ANTHROPIC_API_KEY` as a repository Actions secret. Open **Actions > Live audit > Run workflow**, enter the permanent registration URL and exact model ID, then type `PREREGISTERED`. The guarded workflow runs the full validation first and uploads every attempted live result as a private workflow artifact, including partial output if the job fails.

## Human benchmark and later replication

The human benchmark has not been collected. The repository includes a blinded protocol, evaluator schema, and an analyzer that rejects invalid assignment or outcome data. See [`docs/human_baseline_protocol.md`](docs/human_baseline_protocol.md).

A later model snapshot must be registered and reported as a separate replication. See [`docs/model_replication_protocol.md`](docs/model_replication_protocol.md).

## Repository guide

- [`docs/preregistration.md`](docs/preregistration.md): Version 1 name-signal extension
- [`docs/deviations_from_preregistration.md`](docs/deviations_from_preregistration.md): Version 1 and Version 2 design history
- [`docs/core_audit_preregistration.md`](docs/core_audit_preregistration.md): complete confirmatory design
- [`docs/osf_preregistration.md`](docs/osf_preregistration.md): OSF-ready registration text
- [`docs/power_analysis.md`](docs/power_analysis.md): assumptions, MDEs, and repetition analysis
- [`docs/treatment_construction.md`](docs/treatment_construction.md): exact treatment changes
- [`docs/occupation_selection.md`](docs/occupation_selection.md): why these eight roles
- [`docs/limitations.md`](docs/limitations.md): interpretation boundaries
- [`RESEARCH_BRIEF.md`](RESEARCH_BRIEF.md): short research summary

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

The public project and Python distribution are named `llm-hiring-bias-audit`. The internal import namespace remains `compas_audit` for compatibility with validated historical scripts.
