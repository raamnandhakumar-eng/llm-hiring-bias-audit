# Historical OSF draft: Claude confirmatory live audit

> **Status: NOT SUBMITTED AND SUPERSEDED.** This file is retained for provenance because it records an earlier proposed external-registration path. It was never externally registered and is **not** the governing protocol for the current Claude run. Some details below reflect pre-pilot assumptions, including the originally planned Gemini model and 32-call completion target.
>
> The current execution is prospectively code-locked rather than externally preregistered. See [`claude_confirmatory_protocol.md`](claude_confirmatory_protocol.md) for the governing Claude protocol and [`gemini_pilot_summary.md`](gemini_pilot_summary.md) for the completed feasibility record.

> **Original submission status:** Prepared but not externally registered. The text below is preserved as a historical draft.

**Existing project record:** Version 1 and Version 2 materials remain unchanged. This document proposed a live-execution layer to the already validated matched-résumé design.

**Original execution plan date:** August 17, 2026, before any live Gemini or Claude response for this study was observed.

## Original title

Career Gaps, Education Pathways, and Occupational Context in LLM Resume Screening: Claude Confirmatory Audit with a Gemini Feasibility Pilot

## Contributor

Sriramkrishnan Nandhakumar

## Research question

Holding candidate qualifications fixed, does a resume-screening language model change its fit score, interview recommendation, or confidence when the résumé shows either a 12-month career gap or a non-traditional education pathway? Do those effects differ between frontline and knowledge-work occupations?

## Relationship to the existing project

The repository already contains the Version 1 audit framework and Version 2 robustness extension. Those designs, validation results, power calculations, treatment-balance checks, prompt specifications, and historical files remain preserved.

This draft did not redefine those prior versions. It specified an earlier proposed sequence for collecting the first live-model evidence from the validated core design.

## Study status assumed by the original draft

- The matched-résumé design, parser, analysis code, power analysis, balance checks, manipulation check, prompt robustness code, and deterministic mock validation were complete.
- Mock outputs were software and estimator validation only and would not enter the live-model estimates.
- No live Gemini or Claude response for this study had been requested, observed, or analyzed when this draft was written.

## Provider sequence proposed in the original draft

### Gemini feasibility pilot

The original draft proposed a small non-confirmatory Gemini pilot using `gemini-2.5-flash`.

It proposed one complete four-condition matched set from each of the eight occupations and one call per résumé, for **32 calls total**.

The pilot was limited to operational feasibility: API connectivity, structured-output compliance, parser success, refusals/provider failures, latency, and preservation of raw outputs. Pilot treatment estimates were not intended as confirmatory evidence and were not to revise the Claude design.

The actual feasibility execution later used `gemini-3.6-flash` because `gemini-2.5-flash` was unavailable to the API project. The preserved feasibility evidence contains 18 valid returned outputs across all eight occupations before the free-tier requests-per-day quota became binding. See [`gemini_pilot_summary.md`](gemini_pilot_summary.md).

### Claude confirmatory audit

The confirmatory live audit remains locked to **Claude Sonnet 4.6 (`claude-sonnet-4-6`)** through the Anthropic API.

The Claude result remains the primary live-model result from this execution extension.

## Confirmatory hypotheses

All confirmatory tests are two-sided. Null and unexpected results will be reported.

1. A 12-month career gap changes fit score or interview-recommendation probability.
2. A non-traditional education pathway changes fit score or interview-recommendation probability.
3. The career-gap effect differs between frontline and knowledge-work occupations.
4. The education-pathway effect differs between frontline and knowledge-work occupations.

## Experimental design

The confirmatory design reuses the existing Version 2 core audit without changing the treatment construction or sample structure.

- 8 occupations: 4 frontline or operational and 4 knowledge-work
- 4 base profiles per occupation
- 32 matched base profiles
- 2 career-gap conditions: 0 months and 12 months
- 2 education-pathway conditions: traditional and non-traditional
- 128 unique matched résumés
- 5 repeated Claude calls per résumé
- 1 locked temperature
- **640 planned confirmatory Claude evaluations**

One control name remains fixed within each matched set. No name effect is estimated.

## Randomization

All 640 Claude résumé-trial jobs will be constructed before the first confirmatory API request and assigned a randomized execution order using the existing locked seed of 42.

Treatments will not be executed in separate time blocks.

## Model and prompt lock

The confirmatory model is `claude-sonnet-4-6`.

The primary prompt version is `v2.0-primary`. Temperature is `0.0`. Maximum output tokens are `500`.

The exact model ID, API/library version, system prompt, user prompt, temperature, maximum-token setting, run date, execution order, trial number, latency, raw response, parser status, and error type will be retained.

The model ID, prompt, temperature, treatments, primary outcomes, and sample size will not change during the confirmatory run.

## Primary outcomes

1. Fit score from 1 to 10.
2. Binary interview recommendation.
3. Confidence score from 0 to 1.

Secondary and diagnostic outcomes include refusals, parser failures, provider/API failures, response length, latency, repeated-call variance, and predefined explanation themes.

## Manipulation check

After all 640 primary Claude calls have been attempted, the same Claude model will receive one factual-extraction prompt for each of the 128 unique résumés.

The manipulation check asks the model to identify the explicitly stated career-gap duration and education pathway. It is diagnostic and is never shown during the primary hiring evaluation.

## Prompt robustness

After the primary Claude run and manipulation check, the same 128 résumés will be evaluated under two locked alternate prompts:

- `v2.0-concise`
- `v2.0-rubric`

Each prompt receives five calls per résumé, producing 640 calls per prompt and 1,280 robustness evaluations in total.

These runs do not replace the primary `v2.0-primary` estimate.

## Exclusion and failure rules

A response is excluded from structured-outcome regression only when:

- the provider request fails;
- no JSON object can be parsed;
- a required response field is missing;
- fit score is outside 1 to 10;
- confidence is outside 0 to 1;
- recommendation is not Boolean.

Every failed or refused request remains in the raw dataset. No observation will be selectively rerun because of its outcome, refusal, or parsing status.

## Stopping rule

All 640 randomized primary Claude observations will be attempted once.

There will be no:

- early stopping based on results;
- sample-size increase based on observed p-values or effect sizes;
- selective reruns;
- change to the model, prompt, treatments, or outcomes after observing live results.

If an external outage interrupts execution, all completed and failed observations will be preserved. Any restart will be documented before analysis and will not delete the original records.

## Primary statistical specification

For fit score, recommendation, and confidence, the locked linear specification is:

`outcome ~ nontraditional + has_gap + nontraditional:frontline + has_gap:frontline + occupation fixed effects + matched-set fixed effects + temperature fixed effects`

Fit score and confidence use linear regression. Recommendation uses a linear probability model for the primary percentage-point interpretation. Logistic regression will be reported as a robustness check when estimable.

Standard errors are clustered by `matched_set_id`, the independent matched-profile unit. Clustering by individual résumé is a sensitivity analysis.

## Multiple testing

Benjamini-Hochberg correction will be applied to the 12 primary Claude linear-model tests formed by four pre-specified treatment/interaction terms across three primary outcomes.

The Gemini pilot, logistic model, prompt-robustness runs, manipulation check, and descriptive occupation-level analyses do not enter this correction family.

The report will include point estimates, clustered standard errors, 95% confidence intervals, standardized effects, raw p-values, adjusted q-values, and recommendation probability changes.

## Power

The existing Version 2 planning analysis is retained. With 32 independent matched profiles and five repeated calls per résumé, approximate 80%-power minimum detectable effects are about:

- 0.25 fit-score points for main effects;
- 0.11 recommendation probability for main effects;
- 0.49 fit-score points for frontline interactions;
- 0.22 recommendation probability for frontline interactions.

The sample will not change after live variance is observed.

## Interpretation

The audit estimates whether controlled résumé signals alter Claude outputs under one exact model ID, prompt, date range, and purposive synthetic occupational sample.

It does not establish employer behavior, unlawful discrimination, model intent, effects on actual applicants, or economy-wide labor-market effects.

The Gemini pilot is operational only and is not a competing confirmatory study.

## Data and code availability

The planned public release will preserve the existing repository history and add:

- the prospective Claude design-lock manifest;
- the Gemini pilot summary and preserved outputs;
- the Claude confirmatory run manifest and raw/parsed outputs;
- manipulation-check outputs;
- prompt-robustness outputs;
- coefficient tables and confidence intervals;
- run-quality summaries and figures;
- a dated deviations log if required.

API credentials will never be published.

## Historical external-registration note

This document was **not submitted** to OSF or AsPredicted. There is no external registration URL associated with this draft. The current Claude runner does not require one.
