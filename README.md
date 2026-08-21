# LLM Hiring Bias Audit

A matched-résumé experiment on whether a language model changes its hiring evaluation when candidate qualifications are held fixed but a résumé reports a career gap or a non-traditional education pathway.

> **Current study status — 20 August 2026:** The prospectively code-locked Claude Sonnet 4.6 confirmatory program is complete. The primary experiment produced **640/640 valid screening evaluations** across 128 résumés, 32 matched profiles, and 8 occupations. Two pre-specified prompt-robustness replications each completed another 640/640 evaluations, for **1,920/1,920 successful Claude screening evaluations**. The clearest result is a statistically significant penalty for a **12-month career gap** in Claude's fit-score output: **-0.338 points in knowledge-work roles (p = 0.00081)** and **-0.225 points in frontline roles (p = 0.0067)**. The career-gap × frontline interaction was not statistically significant. Non-traditional-education effects were smaller and less robust.

This repository treats the project as a cumulative research program. **Version 1 and Version 2 results, failed validation stages, feasibility evidence, and historical design materials are preserved rather than rewritten after observing the Claude results.**

## Confirmatory result at a glance

| Outcome | Knowledge-work roles | Frontline roles | Interpretation |
|---|---:|---:|---|
| **12-month career gap → fit score** | **-0.338** (95% CI **[-0.523, -0.152]**, p = **0.00081**, **-0.70 SD**) | **-0.225** (95% CI **[-0.383, -0.067]**, p = **0.0067**, **-0.47 SD**) | Evidence of a career-gap penalty across the sampled occupational contexts |
| **12-month career gap → model confidence** | **-0.0199** (p = **0.00037**) | **-0.0146** (p = **0.0016**) | Claude was less confident when otherwise matched résumés contained a gap |
| **Non-traditional education → fit score** | -0.113 (p = 0.055) | -0.150 (p = 0.0158) | Smaller and less robust than the career-gap result |

The **career-gap × frontline interaction was not statistically significant**, so the study does not support a claim that the penalty is reliably larger in frontline than in knowledge-work roles. The non-traditional-education occupation-group interaction was also not statistically significant.

The recommendation outcome was **not estimable** in this execution because it lacked sufficient variation. The strongest empirical evidence therefore concerns **fit score and model confidence**, not real-world hiring decisions or employer behavior.

The career-gap result persisted under the two pre-specified alternative prompt formulations, `v2.0-concise` and `v2.0-rubric`.

## Research progression

The study developed in three cumulative versions.

| Version | Purpose | Evidence status |
|---|---|---|
| **Version 1 — original audit framework** | Build the matched-résumé generator, randomized execution, provider interface, structured parser, fixed-effects analysis, deterministic placebo tests, and gated perceived-name-signal extension | Core pipeline validated; name-signal extension stopped after its pretest failed locked balance criteria |
| **Version 2 — robustness and execution design** | Add power analysis, exact treatment documentation, résumé-balance tests, manipulation checks, prompt replications, effect sizes, stronger run controls, and feasibility testing | Design and mock validation completed; Gemini feasibility pilot preserved as non-confirmatory operational evidence |
| **Version 3 — Claude confirmatory evidence** | Execute the prospectively code-locked design on `claude-sonnet-4-6` and preserve primary and robustness outputs | **Completed: 640 primary evaluations + 1,280 prompt-robustness evaluations; career-gap penalty detected in fit score** |

Nothing in Version 3 retroactively changes Version 1 or Version 2 results. Earlier nulls, failed pretests, mock-validation outputs, and the incomplete Gemini pilot remain part of the research record.

## Research question

Does a résumé-screening language model respond differently to otherwise equivalent candidates when a résumé reports:

1. a 12-month career gap;
2. a non-traditional education pathway;
3. either signal in a frontline rather than knowledge-work occupation?

The estimand is the change in a model's structured screening output caused by a controlled résumé signal. It is **not** an estimate of employer behavior, applicant outcomes, model intent, or unlawful discrimination.

---

## Version 1 — original audit framework

Version 1 established the résumé generator, matched experimental design, randomized execution, provider interface, structured parser, failure retention, fixed-effects analysis, and deterministic placebo tests.

It contains two related tracks:

- **Core study:** 32 matched profiles, 128 résumés, and 640 planned model evaluations.
- **Perceived-name-signal extension:** 512 résumés and 2,560 planned evaluations across four name-signal groups.

### Name-signal pretest: stopped under the locked rules

The first human pretest included **150 respondents and 1,200 complete ratings**. The stimuli failed the locked balance rules for:

- familiarity;
- perceived socioeconomic status;
- unusualness.

Consent and attention-check fields were also absent. The thresholds were **not relaxed after the data were reviewed**, and the name-signal extension did not advance to the model audit.

Version 1 files remain available in [`config/audit.yaml`](config/audit.yaml), [`docs/preregistration.md`](docs/preregistration.md), and [`docs/deviations_from_preregistration.md`](docs/deviations_from_preregistration.md).

---

## Version 2 — robustness and execution design

Version 2 retained the Version 1 core estimand and added prospective safeguards before any live Anthropic observation:

- scenario-based power analysis for the 640-evaluation design;
- exact treatment-wording documentation;
- automated résumé-balance tests;
- an occupation-selection rationale using wages, education, employment scale, and observed AI exposure;
- one pre-specified primary prompt and two prompt-robustness replications;
- a separate post-primary manipulation check;
- standardized effects and confidence intervals;
- repeated-call variance, failure, and refusal reporting;
- a blinded human-benchmark protocol and later model-snapshot replication protocol;
- overwrite protection, design hashes, and guarded live-run workflows.

These changes were made before live Anthropic outcomes were observed.

### Pipeline validation

The deterministic mock provider tested generation, randomization, parsing, repeated calls, estimation, and reporting. It completed **640/640 core evaluations** with no failures or refusals and recovered the planted fit-score effects exactly.

| Term | Planted effect | Recovered effect |
|---|---:|---:|
| 12-month career gap | -0.450 | -0.450 |
| Non-traditional education | -0.150 | -0.150 |
| Career gap × frontline | 0.000 | 0.000 |
| Education pathway × frontline | 0.000 | 0.000 |

The mock recommendation outcome was constant, so the recommendation model was reported as **not estimable**. These are software/estimator validation results, not evidence about a live language model, employer, or applicant.

Validation report: [`results/core_placebo/core_placebo_validation_report.md`](results/core_placebo/core_placebo_validation_report.md).

### Power analysis

The pre-run calculation separated treatment-cell variation from repeated-call noise and used a two-sided t-test approximation with 32 independent matched profiles.

| Contrast | Fit-score MDE | Recommendation-probability MDE |
|---|---:|---:|
| Main effect | 0.25 points | 0.11 |
| Frontline interaction | 0.49 points | 0.22 |

These are **80% power minimum detectable effects** under the stated planning assumptions. They are not observed variance estimates. The design had reasonable power for moderate main effects but limited power for subtle occupational interactions.

![Minimum detectable effect by repetitions](docs/figures/power_by_repetitions.svg)

Assumptions and calculations: [`docs/power_analysis.md`](docs/power_analysis.md).

### Résumé balance

All 32 matched sets passed deterministic pre-run checks for:

- word and sentence counts;
- skills count and years of experience;
- quantified-achievement count;
- the SHA-256 hash of all non-treatment text.

Treatment construction: [`docs/treatment_construction.md`](docs/treatment_construction.md)  
Balance report: [`results/design/resume_balance_report.md`](results/design/resume_balance_report.md)

### Gemini feasibility pilot: preserved, non-confirmatory

Before the Claude confirmatory execution, a limited Gemini feasibility stage tested operational behavior only. Using `gemini-3.6-flash`, the project preserved:

- **18 valid screening outputs**;
- coverage across **all 8 occupations**;
- **18/18 successful parses**;
- **0/18 refusals**.

The free-tier requests-per-day quota prevented completion of the originally scheduled 32 calls. The pilot was explicitly **non-confirmatory** and its screening outputs were not used to revise the hypotheses, résumés, occupations, sample size, Claude prompt, model, stopping rule, or statistical specification.

Operational record: [`docs/gemini_pilot_summary.md`](docs/gemini_pilot_summary.md).

---

## Version 3 — Claude Sonnet 4.6 confirmatory evidence

### Prospective code lock

The confirmatory live stage was fixed to:

- provider/model: **Anthropic Claude Sonnet 4.6 (`claude-sonnet-4-6`)**;
- 128 synthetic résumés;
- 32 matched profiles;
- 8 occupations;
- 5 evaluations per résumé;
- **640 primary evaluations**;
- primary prompt `v2.0-primary`;
- temperature `0.0`;
- randomized execution order;
- no selective reruns of observed model outputs.

Immediately before the first Claude request, the runner created `docs/claude_confirmatory_design_lock.json`, a SHA-256 manifest covering the confirmatory design, prompts, provider implementation, analysis code, execution scripts, and résumé templates.

This execution is therefore described as **prospectively code-locked**, not externally preregistered.

Protocol: [`docs/claude_confirmatory_protocol.md`](docs/claude_confirmatory_protocol.md).

### Execution record

The GitHub Actions confirmatory program completed successfully.

- **Primary run:** 640/640 screening evaluations completed successfully.
- **Manipulation checks:** 128/128 valid rows correctly recovered the career-gap treatment, 128/128 correctly recovered the education-pathway treatment, and 128/128 correctly recovered both jointly.
- **Concise prompt replication:** 640/640 evaluations completed.
- **Rubric prompt replication:** 640/640 evaluations completed.
- **Total Claude screening evaluations:** **1,920/1,920 successful calls** across the primary and two robustness prompts.
- The workflow artifact and prospective design lock were preserved after execution.

Execution record: [GitHub Actions run 32406903487](https://github.com/raamnandhakumar-eng/llm-hiring-bias-audit/actions/runs/32406903487)

### Primary fit-score finding

| Fit-score contrast | Estimate | 95% CI | p-value | Standardized effect |
|---|---:|---:|---:|---:|
| Career gap, knowledge-work roles | **-0.338** | **[-0.523, -0.152]** | **0.00081** | **-0.70 SD** |
| Career gap, frontline roles | **-0.225** | **[-0.383, -0.067]** | **0.0067** | **-0.47 SD** |

The career-gap × frontline interaction was **not statistically significant**. The evidence therefore supports a career-gap penalty across the sampled occupational contexts, but not a claim that it is reliably larger in one occupation group.

### Model-confidence finding

Claude's reported confidence also fell for résumés containing a 12-month career gap:

- knowledge-work roles: approximately **-0.0199** (`p = 0.00037`);
- frontline roles: approximately **-0.0146** (`p = 0.0016`).

### Education-pathway finding

The non-traditional-education fit-score estimates were smaller and less robust:

- knowledge-work roles: approximately **-0.113** (`p = 0.055`);
- frontline roles: approximately **-0.150** (`p = 0.0158`).

The occupation-group interaction was not statistically significant. Under the study's multiple-testing framework, the education-pathway evidence does not support the same strength of conclusion as the career-gap finding.

### Prompt robustness

The career-gap result persisted under both pre-specified alternative prompt formulations:

- `v2.0-concise`;
- `v2.0-rubric`.

These replications strengthen the interpretation that the primary career-gap finding is not an artifact of one prompt wording.

### Recommendation outcome

The recommendation outcome was **not estimable** in the Claude execution because it lacked sufficient variation. The confirmatory evidence therefore concerns **fit score and model confidence**, not an estimated probability of real-world hiring.

---

## Experimental design

| Design element | Specification |
|---|---|
| Occupational sample | Eight purposively selected occupations: four frontline/operational and four knowledge-work roles |
| Base profiles | Four profiles per occupation, yielding 32 matched sets |
| Career-gap treatment | No stated gap versus a standardized 12-month gap |
| Education treatment | Traditional versus standardized non-traditional pathway |
| Unique résumés | 128 |
| Repeated evaluations | Five calls per résumé |
| Primary confirmatory sample | 640 model evaluations |
| Prompt-robustness sample | 1,280 additional model evaluations |
| Primary outcomes | Fit score, interview recommendation, and model confidence |
| Claude configuration | `claude-sonnet-4-6`, `v2.0-primary`, temperature 0.0 |

Each matched profile produces four résumé variants:

| | Traditional education | Non-traditional education |
|---|---:|---:|
| No career gap | Control | Education treatment |
| 12-month career gap | Gap treatment | Combined treatment |

Within a matched set, candidate name, target role, experience, skills, achievements, employer history, credential level, field, formatting, and all non-treatment text remain fixed.

## Occupational sample

| Frontline or operational | Knowledge work |
|---|---|
| Production supervisors | Management analysts |
| Registered nurses | Project management specialists |
| Maintenance workers | Computer systems analysts |
| Logisticians | Financial analysts |

The eight occupations are a purposive contrast sample, not a population-representative sample. The selection spans multiple education pathways, employment scales, wages, and observed AI-exposure levels.

Complete rationale and sources: [`docs/occupation_selection.md`](docs/occupation_selection.md).

## Statistical analysis

For outcome `Y`, the pre-specified linear specification is:

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
- Interview recommendation uses a linear probability model when estimable.
- Logistic regression is a robustness check when the outcome has sufficient variation.
- Standard errors are clustered by `matched_set_id`, the independent matched-profile unit.
- Benjamini-Hochberg correction covers 12 confirmatory tests: four terms across three primary outcomes.
- Reporting includes point estimates, clustered standard errors, 95% confidence intervals, standardized effects, raw p-values, adjusted q-values, and recommendation-probability changes where estimable.
- Every failed request, refusal, parser error, and raw response remains in the audit record. Selective reruns are prohibited.

Occupation-specific estimates are descriptive. The study was not powered for a large family of occupation-level hypothesis tests.

## Prospective design lock and historical preregistration materials

The Claude execution did **not** rely on an externally submitted OSF or AsPredicted registration. Instead, `scripts/lock_claude_confirmatory.py` created the prospective SHA-256 design lock immediately before the first Claude request. The workflow fixed the exact Claude model ID and refused to overwrite existing live outputs.

Earlier OSF-ready and AsPredicted-ready materials remain in the repository as historical Version 1/Version 2 artifacts. They are preserved, but they are not presented as evidence that an external preregistration occurred.

Current execution files:

- [`docs/claude_confirmatory_protocol.md`](docs/claude_confirmatory_protocol.md)
- `docs/claude_confirmatory_design_lock.json`
- [`config/claude_confirmatory.yaml`](config/claude_confirmatory.yaml)
- [`scripts/run_claude_confirmatory.sh`](scripts/run_claude_confirmatory.sh)

Historical preregistration-ready files remain under `docs/`, including:

- `docs/osf_preregistration.md`;
- `docs/aspredicted_preregistration.md`;
- `docs/preregistration_lock.json`.

## Reproducibility

### Validate the design without live API calls

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
make v2-validate
```

This runs the power analysis, résumé-balance audit, 640-evaluation mock pipeline, 128 manipulation-check tests, and automated test suite.

### Run the Claude confirmatory program

```bash
pip install -e ".[api,dev]"
export ANTHROPIC_API_KEY="set-securely-outside-git"
export ANTHROPIC_MODEL="claude-sonnet-4-6"
bash scripts/run_claude_confirmatory.sh
```

The script creates the prospective design lock before the first Claude request, runs the 640 primary evaluations, then the manipulation check and two prompt replications. It preserves every attempted result and refuses to overwrite existing live output.

A guarded manual GitHub Actions workflow is included. Store `ANTHROPIC_API_KEY` as a repository secret, then use **Actions > Claude confirmatory live audit** and type `RUN_CLAUDE`.

The older **Live audit** workflow remains in the repository as the historical Version 2 OSF-gated route. It is not the current Claude execution route.

## Historical pre-Claude status snapshot

The paragraph below is preserved verbatim from the README state immediately before the Claude confirmatory result was incorporated. It is historical, not current.

> **Study status:** The design and analysis pipeline are complete and mock-validated. A non-confirmatory Gemini feasibility pilot returned **18 valid screening responses across all 8 occupations; 18/18 parsed successfully and 0/18 were refusals** before the free-tier requests-per-day quota became binding. **No live Claude response has been collected or analyzed.** The next stage is a prospectively code-locked 640-evaluation audit on `claude-sonnet-4-6`. The repository does not yet claim substantive evidence of bias in a deployed model.

This snapshot is retained to make the project chronology auditable and to avoid rewriting the pre-result record after observing the confirmatory evidence.

## Interpretation and limitations

This audit estimates whether controlled résumé signals change **one model snapshot's outputs under one fixed experimental configuration**. It cannot establish:

- effects on real applicants or hiring decisions;
- employer discrimination or legal liability;
- model intent;
- demographic identity from a person's name;
- representativeness across occupations, models, prompts, providers, dates, or deployment settings.

The eight occupations form a purposive contrast sample. Synthetic résumés simplify real application materials. Repeated calls measure instability within the locked setup, not across deployment environments. Model-generated explanations are secondary outcomes.

Full limitations: [`docs/limitations.md`](docs/limitations.md).

## Planned extensions

- collect a successful independent name-perception pretest before any future name-signal audit;
- compare model and blinded human evaluations using [`docs/human_baseline_protocol.md`](docs/human_baseline_protocol.md);
- replicate the locked design on a later model snapshot using [`docs/model_replication_protocol.md`](docs/model_replication_protocol.md).

These extensions are separate studies and will not be folded retroactively into the Claude confirmatory result.

## Repository map

| Path | Purpose |
|---|---|
| [`config/`](config/) | Locked study configurations |
| [`data/templates/`](data/templates/) | Synthetic base résumé templates |
| [`data/occupations/`](data/occupations/) | Occupation registry and exposure snapshot |
| [`src/compas_audit/`](src/compas_audit/) | Generation, execution, validation, and analysis code |
| [`scripts/`](scripts/) | Reproduction, power, robustness, and live-run entry points |
| [`docs/`](docs/) | Methods, ethics, pilot records, protocols, design locks, and historical preregistration-ready materials |
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
