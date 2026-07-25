# LLM Hiring Bias Audit

**A pre-specified, placebo-validated matched-résumé experiment on career gaps, education pathways, and occupational context.**

This repository studies a narrow, controlled question: **when qualifications are held fixed, does a language model evaluate a candidate differently because the résumé shows a 12-month career gap or a non-traditional education pathway?** It also tests whether those effects differ between frontline and knowledge-work occupations.

Within each matched set, experience, skills, achievements, employer history, education level, target role, formatting, and résumé length are held constant. Only the treatment signal changes.

> **Current status:** The research pipeline and estimator are complete and have been validated against a deterministic mock provider. **The live audit has not been run, and no findings about any deployed model are reported here.** This repository documents the method and its validation, not live-model results.

## Why this question matters

Career interruptions and non-traditional education are common among caregivers, career changers, returning workers, veterans, immigrants, and people who complete education through part-time or alternative routes. If AI systems screen or rank applicants, even small shifts in scores or recommendations could affect who receives further consideration.

The occupational comparison matters because the same résumé signal may be read differently across settings. A career gap may carry one meaning in a frontline operations role and another in knowledge work. The audit is designed to estimate that difference rather than assume it.

## Core experimental design

The core audit estimates the effects of:

1. a 12-month career gap;
2. a traditional versus non-traditional education pathway;
3. career gap × frontline occupation;
4. non-traditional education × frontline occupation.

The design contains:

- **8 occupations** — 4 frontline or operational, 4 knowledge-work;
- **4 base profiles per occupation → 32 matched base profiles**;
- **2 career-gap conditions × 2 education-pathway conditions**;
- **128 unique matched résumés**;
- **5 repeated trials per résumé → 640 planned evaluations**;
- **1 exact model ID and 1 locked temperature**.

A control name is held fixed within each matched set; the core analysis does not estimate a name effect. Full plan: [`docs/core_audit_preregistration.md`](docs/core_audit_preregistration.md).

## Pipeline and estimator validation

Before any live model call, the full workflow was run against a deterministic mock provider carrying planted effects of known magnitude. The core placebo completed **640 of 640 evaluations, 0 failures, and 0 refusals**, with randomized order and no selective reruns.

The estimator recovered the planted fit-score effects exactly:

| Treatment | Planted effect | Recovered effect |
|---|---:|---:|
| 12-month career gap | −0.450 | −0.450 |
| Non-traditional education | −0.150 | −0.150 |
| Career gap × frontline | 0.000 | 0.000 |
| Non-traditional education × frontline | 0.000 | 0.000 |

The mock recommendation outcome was constant, so the recommendation model was reported as **not estimable** rather than interpreted from noise. Report: [`results/core_placebo/core_placebo_validation_report.md`](results/core_placebo/core_placebo_validation_report.md).

*These results validate the software and estimator. They are not evidence about any model, employer, or applicant.*

## Four-month scope

The deliverable is the **core labor-market audit** only, sized to be completed, analyzed, written, and released in four months.

| Deliverable | Scope | Status |
|---|---|---|
| External preregistration | Public OSF or AsPredicted timestamp before the first live request | Prepared; submission pending |
| Core live audit | 128 matched résumés × 5 trials = 640 evaluations | Design locked; not run |
| Confirmatory analysis | Fit score, interview recommendation, confidence, occupational interactions | Code complete |
| Robustness and diagnostics | Failures, refusals, repeated-call variance, logistic model, treatment means | Code complete |
| Public output | Reproducible dataset, tables, figures, and a concise paper | Planned within four months |

Explicitly **future work, not promised deliverables:** a replacement name-perception study, the 2,560-evaluation name-signal extension, a human hiring-manager benchmark, and multi-model replication. *This scope decision was made before observing any live model output.*

## A preserved failed pretest

A separate extension was designed to test validated perceived-name signals. The first human pretest had **150 respondents and 1,200 complete ratings**. Signal recognition was strong, but the study breached all three locked balance thresholds:

| Balance measure | Observed | Maximum allowed |
|---|---:|---:|
| Familiarity | 0.947 | 0.750 |
| Perceived socioeconomic status | 1.130 | 0.750 |
| Unusualness | 1.713 | 0.750 |

The export also lacked consent and attention-check fields, so respondent eligibility could not be verified. Rather than relax the thresholds, the extension was moved out of scope and the negative result preserved. Names are treated as **perceived signals only**, never as evidence of any person's identity.

## Outcomes and analysis

Primary outcomes are fit score (1–10), binary interview recommendation, and model confidence (0–1).

Confirmatory analysis uses matched-set and occupation fixed effects; standard errors clustered by matched résumé; Benjamini-Hochberg correction across pre-specified treatment terms; linear models for fit score and confidence; a linear probability model for recommendation, with logistic regression when the outcome varies enough; and failure/refusal sensitivity checks. Every raw response, failure, refusal, prompt, exact model ID, timestamp, trial number, latency, and parser status is retained. Selective reruns are prohibited.

## Reproduce the validation pipeline

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
make reproduce                     # full pipeline
make core-reproduce                # 640-evaluation core placebo only
```

## Run the live audit

The live runner refuses to start without a valid external preregistration URL, which is recorded in the run manifest.

```bash
pip install -e ".[api]"
export EXTERNAL_PREREGISTRATION_URL="https://osf.io/xxxxx"
export ANTHROPIC_API_KEY="..."
export ANTHROPIC_MODEL="exact-model-id"
make core-live
```

API credentials must never be committed.

## Interpretation and limits

This is an audit of model behavior under a controlled synthetic design. It does not measure employer behavior, prove intent, establish unlawful discrimination, or identify anyone's demographic identity. Any live result will apply only to the exact model, prompt, run period, treatment definitions, and eight-occupation sample used. It should not be generalized to the whole labor market.

## Repository guide

- [`docs/core_audit_preregistration.md`](docs/core_audit_preregistration.md) — locked core design
- [`docs/osf_preregistration.md`](docs/osf_preregistration.md) and [`docs/aspredicted_preregistration.md`](docs/aspredicted_preregistration.md) — ready-to-submit registrations
- [`docs/ethics_statement.md`](docs/ethics_statement.md), [`docs/limitations.md`](docs/limitations.md), and [`docs/model_card.md`](docs/model_card.md)
- [`RESEARCH_PROPOSAL.md`](RESEARCH_PROPOSAL.md) — four-month research proposal

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

## License

MIT. See [`LICENSE`](LICENSE).

## Contact

Raam Nandhakumar — raam.nandhakumar@gmail.com

---

*The public project and Python distribution are named `llm-hiring-bias-audit`. The internal import namespace remains `compas_audit`, and the old `compas-*` command aliases remain only for compatibility with validated historical scripts.*
