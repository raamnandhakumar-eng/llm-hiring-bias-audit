# AsPredicted-ready preregistration

> **Study title:** Career Gaps, Education Pathways, and Occupational Context in LLM Resume Screening
>
> **Status:** Ready to paste into AsPredicted before the first live model request.

## 1. Have any data been collected for this study already?

No live model responses have been collected or viewed for the confirmatory study.

The code has been tested using a deterministic mock provider with planted effects. Those placebo outputs validate the software and estimator only. They will not be included in the live-model confirmatory estimates.

A separate name-perception pretest was conducted for a different, currently blocked extension. No perceived-name effect is part of this registered core study.

## 2. What is the main question or hypothesis being tested?

Holding qualifications fixed:

1. a 12-month career gap changes the model's fit score or interview-recommendation probability;
2. a non-traditional education pathway changes the model's fit score or interview-recommendation probability;
3. the career-gap effect differs between frontline and knowledge-work occupations;
4. the education-pathway effect differs between frontline and knowledge-work occupations.

All confirmatory tests are two-sided. Null and unexpected findings will be reported.

## 3. Describe the key dependent variables and how they will be measured

Primary outcomes:

- fit score, from 1 to 10;
- binary interview recommendation;
- model confidence, from 0 to 1.

Secondary diagnostic outcomes:

- refusal;
- parser failure;
- provider/API failure;
- response length;
- latency;
- repeated-call variance;
- predefined explanation-theme counts.

## 4. How many and which conditions will participants be assigned to?

There are no human participants in the live model audit.

The study uses 32 synthetic base candidate profiles across eight occupations. Each base profile is expanded into four resume conditions in a 2 × 2 design:

- no career gap, traditional education;
- 12-month career gap, traditional education;
- no career gap, non-traditional education;
- 12-month career gap, non-traditional education.

This produces 128 unique matched resumes. Each resume will be evaluated five times, producing 640 planned model evaluations.

A control name is fixed across all four variants within each matched set. No name effect is estimated.

## 5. Specify exactly which analyses will be conducted

For fit score and confidence, estimate linear regression models.

For interview recommendation, estimate a linear probability model. Report logistic regression as a robustness check when the outcome has sufficient variation.

Locked model:

`outcome ~ nontraditional + has_gap + nontraditional:frontline + has_gap:frontline + occupation fixed effects + matched-set fixed effects + temperature fixed effects`

Standard errors will be clustered by matched base profile (`matched_set_id`), the independent matched unit. Clustering by individual résumé is a sensitivity check.

Benjamini-Hochberg correction will be applied across the four preregistered treatment terms for the primary outcomes:

- nontraditional;
- has_gap;
- nontraditional × frontline;
- has_gap × frontline.

The correction family contains 12 tests: four terms across fit score, recommendation, and confidence. Report estimates, clustered standard errors, raw p-values, adjusted q-values, 95% confidence intervals, standardized effects, and recommendation probability changes.

Preregistered robustness and diagnostic analyses:

- logistic recommendation model when estimable;
- failed recommendations coded as not recommended;
- treatment means by occupation tier;
- failure and refusal rates by treatment;
- repeated-call variance;
- occupation-specific descriptive estimates;
- clustering by individual résumé as a sensitivity check;
- two prompt replications using `v2.0-concise` and `v2.0-rubric`;
- a separate post-primary manipulation check.

## 6. Describe exactly how outliers and exclusions will be defined and handled

No resume or model response will be removed because its outcome is surprising, unfavorable, or inconsistent with the hypotheses.

A response is excluded from structured-outcome regression only when:

- the provider request fails;
- no JSON object can be parsed;
- a required response field is missing;
- fit score is outside 1–10;
- confidence is outside 0–1;
- recommendation is not Boolean.

Every failed response remains in the raw dataset. No failed or refused observation will be selectively rerun.

## 7. How many observations will be collected and how was this number determined?

The primary study will attempt exactly 640 evaluations:

- 8 occupations;
- 4 base profiles per occupation;
- 2 career-gap conditions;
- 2 education-pathway conditions;
- 5 trials per resume.

`8 × 4 × 2 × 2 × 5 = 640`.

The sample size is fixed before the live run. There will be no early stopping or sample-size adjustment based on observed results.

The fixed planning analysis assumes 32 independent matched profiles and separates condition-level variance from repeated-call noise. Approximate 80% power MDEs are 0.25 fit-score points and 0.11 recommendation probability for main effects, and 0.49 and 0.22 for interactions. Five calls were selected because later calls produce diminishing precision gains.

## 8. Anything else you would like to preregister?

The initial live audit will use **Google Gemini 2.5 Flash (`gemini-2.5-flash`)**. This is the preregistered primary model. The runner uses the pinned `google-genai` SDK, temperature 0.0, and a Gemini 2.5 Flash thinking budget of 0.

After the Gemini primary outputs have been preserved, the same experimental structure is planned to be replicated on **Claude**. The Claude result is a separate cross-provider replication and will not be pooled into the Gemini primary test family. The exact Claude model ID and run date will be registered before the first Claude request.

All 640 Gemini primary jobs will be randomized before the first API request. Treatments will not be run in separate time blocks.

The `v2.0-primary` prompt, model ID, temperature, and maximum-token setting will remain fixed throughout the confirmatory run. The exact model ID, API version, full prompts, timestamps, trial number, execution order, latency, raw response, parser status, and error type will be retained.

After all 640 primary observations are attempted, two 640-evaluation Gemini prompt replications and one 128-call Gemini factual manipulation check will run. They are robustness and diagnostic samples and do not change the confirmatory stopping rule.

The primary study concerns one Gemini model, one prompt, one run period, and a purposive sample of eight synthetic occupations. The planned Claude replication tests cross-provider transfer. Neither establishes employer behavior, unlawful discrimination, model intent, effects on actual applicants, or economy-wide labor-market effects.

Any change after registration will be dated in `docs/deviations_from_preregistration.md` and labeled confirmatory or exploratory before reporting.

## After submission

Record the permanent AsPredicted URL and export it before the live run:

```bash
export EXTERNAL_PREREGISTRATION_URL="https://aspredicted.org/xxxxx.pdf"
```
