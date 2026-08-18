# Methodology

## Estimand

The primary estimand is the conditional difference in screening outcomes associated with a controlled resume signal, holding the base template and stated qualifications constant. The main interaction asks whether that difference changes between frontline and knowledge-work roles.

## Experimental design

Each standardized base résumé is permuted across education pathway and career-gap condition, then evaluated in repeated trials. A control name is fixed within each matched set. The core audit estimates no name effect. The separate name-signal extension remains blocked by its failed perception pretest.

The Claude confirmatory stage uses 32 matched base profiles across eight occupations, producing 128 résumés and 640 primary evaluations at five repeated calls per résumé. The exact model is `claude-sonnet-4-6`, the primary prompt is `v2.0-primary`, and temperature is fixed at `0.0`.

## Outcomes

Primary outcomes are fit score, binary recommendation, and model confidence. Diagnostics include within-résumé variance, response failure, refusal, and coded risk-factor language.

## Econometric specification

```text
Y_it = beta_0
     + non-traditional education
     + non-traditional education x frontline
     + career gap
     + career gap x frontline
     + occupation fixed effects
     + matched-set fixed effects
     + temperature fixed effects
     + error_it
```

Standard errors are clustered by `matched_set_id`, the independent matched base profile. Clustering by individual résumé is a sensitivity check. Benjamini-Hochberg q-values control the false discovery rate across the four **pre-specified** terms in the three primary linear models. The binary outcome is reported as a linear probability model for direct percentage-point interpretation, with logit as a robustness check when feasible.

## Prospective locking

The current Claude execution is **prospectively code-locked**, not externally preregistered. Before the first Claude API request, `scripts/lock_claude_confirmatory.py` creates a SHA-256 manifest covering the confirmatory configuration, prompts, provider and execution code, analysis code, and synthetic résumé templates.

Earlier OSF-ready materials are retained as historical Version 1/Version 2 artifacts and are not represented as an external preregistration of the current Claude run.

## Gemini feasibility stage

A non-confirmatory Gemini feasibility pilot preceded the Claude run. The preserved pilot evidence contains 18 valid `gemini-3.6-flash` outputs across all eight occupations; all 18 parsed successfully and none was classified as a refusal. Provider requests-per-day quota prevented completion of the originally scheduled 32 calls.

The Gemini outputs are used only to establish API connectivity, structured-output compatibility, parser behavior, refusal handling, and logging. They are not used to change the Claude hypotheses, treatment construction, occupation sample, model, prompt, sample size, stopping rule, or statistical specification.

## Placebo validation

`mock-auditor-v3` contains transparent planted score effects and balanced deterministic trial noise. Its purpose is to verify exact recovery of the locked estimand, parsing behavior, repeated-trial handling, and output generation. Placebo p-values are not substantive findings.

## Reliability checks

The pre-specified study includes two prompt paraphrases, randomized request order, equal-length treatment formatting, manipulation checks, repeated-call variance, and parser-failure rates by treatment. A later model snapshot is a separate replication.

## Limits

This synthetic audit measures model behavior under a specific configuration. It does not measure actual employer discrimination, downstream hiring outcomes, legal liability, or a person's true protected status. Results can change across models, dates, prompts, and provider infrastructure. The Gemini feasibility sample is operational only and incomplete because of provider quota.

## Responsible disclosure

Reproduce disparities with a locked configuration, estimate practical magnitude and uncertainty, test sensitivity, document the exact model and date, protect credentials and raw data, and avoid causal or legal claims unsupported by the design.
