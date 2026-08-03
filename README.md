# LLM Hiring Bias Audit

**Independent research project · 2026**  
**Python · Anthropic API integration · Experimental audit design · Algorithmic fairness**

Matched-résumé audit testing whether a 12-month career gap or non-traditional education pathway changes an LLM hiring evaluation, and whether those effects differ between frontline and knowledge-work occupations.

## Project snapshot

- Designed a matched-résumé experiment across **8 occupations**: 4 frontline or operational roles and 4 knowledge-work roles.
- Built **32 matched base profiles**, producing **128 unique résumés** across career-gap and education-pathway conditions.
- Implemented a Python pipeline for **640 planned live evaluations** using one exact model ID, one locked temperature, and five repeated trials per résumé.
- Specified matched-set and occupation fixed effects, standard errors clustered by matched résumé, and Benjamini-Hochberg correction across pre-specified treatment terms.
- Validated the complete workflow on a deterministic mock provider: **640/640 evaluations completed, with 0 failures and 0 refusals**, and the estimator recovered planted effects exactly.
- Retired a 150-respondent name-perception pretest after all three pre-specified balance thresholds failed, rather than weakening the criteria after seeing the results.
- Enforced an external preregistration URL in code before any live model request can run.

> **Current status:** The pipeline and estimator are complete and validated against a deterministic mock provider. **The live Anthropic audit has not been run, and this repository reports no findings about a deployed model.**

## Research program

This is the second project in a broader research program on AI and labor markets. The first paper, [The Frontline Exposure Gap](https://doi.org/10.5281/zenodo.21522366), measures where observed AI use reaches the workforce. It found that frontline occupations account for **31.7% of U.S. employment but only 11.1% of task-matched AI usage**.

Both projects grew from seven years running a 27-person manufacturing and retail business, where planning, procurement, and reporting digitized much faster than production-floor work. The first project measures that adoption divide. This project asks the next question: when a language model becomes a hiring gatekeeper, does it evaluate otherwise equivalent workers differently because of career continuity or education pathway?

## Research question

When qualifications are held fixed, does a language model change its evaluation because a résumé shows:

1. a 12-month career gap;
2. a traditional versus non-traditional education pathway;
3. a career gap in a frontline rather than knowledge-work role;
4. a non-traditional education pathway in a frontline rather than knowledge-work role?

Within each matched set, experience, skills, achievements, employer history, education level, target role, formatting, résumé length, and control name remain fixed. Only the treatment signal changes.

The concern is deployment, not only model intent. A model can appear capable in isolation and still affect labor-market access when its scores or recommendations determine who reaches human review.

## Design

- **8 occupations** — 4 frontline or operational, 4 knowledge-work
- **4 base profiles per occupation** — 32 matched base profiles
- **2 career-gap conditions × 2 education-pathway conditions**
- **128 unique matched résumés**
- **5 repeated trials per résumé** — 640 planned live evaluations
- **1 exact model ID and 1 locked temperature**

A control name is fixed within each matched set. The core analysis does not estimate a name effect.

Full plan: [`docs/core_audit_preregistration.md`](docs/core_audit_preregistration.md).

## Pipeline validation

Before any live model call, the full workflow was run against a deterministic mock provider with planted effects of known magnitude. The core placebo completed **640 of 640 evaluations, with 0 failures and 0 refusals**. Execution order was randomized and selective reruns were disabled.

| Treatment | Planted effect | Recovered effect |
|---|---:|---:|
| 12-month career gap | −0.450 | −0.450 |
| Non-traditional education | −0.150 | −0.150 |
| Career gap × frontline | 0.000 | 0.000 |
| Non-traditional education × frontline | 0.000 | 0.000 |

The mock recommendation outcome was constant, so the recommendation model was reported as **not estimable** rather than interpreted from noise.

Report: [`results/core_placebo/core_placebo_validation_report.md`](results/core_placebo/core_placebo_validation_report.md).

*These results validate the software and estimator. They are not evidence about any model, employer, or applicant.*

## Current study scope

| Item | Status |
|---|---|
| External preregistration | Prepared; submission pending |
| Core live audit | Design locked; not run |
| Fit-score, recommendation, confidence, and interaction models | Code complete |
| Failure, refusal, repeated-call, and treatment-mean checks | Code complete |
| Public dataset, tables, figures, and paper | Planned after the live run |

A replacement name-perception study, the 2,560-evaluation name-signal extension, a human hiring-manager benchmark, and multi-model replication are outside the current study.

## Retired name-perception pretest

A separate extension was designed to test perceived-name signals. The first human pretest had **150 respondents and 1,200 complete ratings**. Signal recognition was strong, but the stimuli breached all three locked balance thresholds:

| Balance measure | Observed | Maximum allowed |
|---|---:|---:|
| Familiarity | 0.947 | 0.750 |
| Perceived socioeconomic status | 1.130 | 0.750 |
| Unusualness | 1.713 | 0.750 |

The export also lacked consent and attention-check fields, so respondent eligibility could not be verified. The thresholds were not relaxed after seeing the data. The extension remains blocked, and names are treated as perceived signals rather than evidence of anyone's identity.

## Outcomes and analysis

Primary outcomes are fit score (1–10), binary interview recommendation, and model confidence (0–1).

The confirmatory analysis uses matched-set and occupation fixed effects, standard errors clustered by matched résumé, and Benjamini-Hochberg correction across the pre-specified treatment terms. Fit score and confidence use linear models. Recommendation uses a linear probability model, with logistic regression when the outcome has enough variation.

Every raw response, failure, refusal, prompt, exact model ID, timestamp, trial number, latency, and parser status is retained. Selective reruns are prohibited.

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

API credentials must not be committed.

## Limits

This is a controlled synthetic audit of one model configuration. It does not measure employer behavior, prove intent, establish unlawful discrimination, or identify anyone's demographic identity.

Any live result will apply only to the exact model, prompt, run period, treatment definitions, and eight-occupation sample used. It should not be generalized to the whole labor market.

## Repository guide

- [`RESEARCH_BRIEF.md`](RESEARCH_BRIEF.md) — project context and study summary
- [`docs/core_audit_preregistration.md`](docs/core_audit_preregistration.md) — locked core design
- [`docs/osf_preregistration.md`](docs/osf_preregistration.md) and [`docs/aspredicted_preregistration.md`](docs/aspredicted_preregistration.md) — ready-to-submit registrations
- [`docs/ethics_statement.md`](docs/ethics_statement.md), [`docs/limitations.md`](docs/limitations.md), and [`docs/model_card.md`](docs/model_card.md)

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

Sriramkrishnan “Raam” Nandhakumar — raam.nandhakumar@gmail.com

---

*The public project and Python distribution are named `llm-hiring-bias-audit`. The internal import namespace remains `compas_audit`, and the old `compas-*` command aliases remain only for compatibility with validated historical scripts.*
