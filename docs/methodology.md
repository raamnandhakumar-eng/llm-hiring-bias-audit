# Methodology

## Estimand

The primary estimand is the conditional difference in screening outcomes associated with a controlled resume signal, holding the base template and stated qualifications constant. The main interaction asks whether that difference changes between frontline and knowledge-work roles.

## Experimental design

Each standardized base résumé is permuted across education pathway and career-gap condition, then evaluated in repeated trials. A control name is fixed within each matched set. The core audit estimates no name effect. The separate name-signal extension remains blocked by its failed perception pretest.

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

Standard errors are clustered by `matched_set_id`, the independent matched base profile. Clustering by individual résumé is a sensitivity check. Benjamini-Hochberg q-values control the false discovery rate across the four preregistered terms in the three primary linear models. The binary outcome is reported as a linear probability model for direct percentage-point interpretation, with logit as a robustness check when feasible.

## Placebo validation

`mock-auditor-v3` contains transparent planted score effects and balanced deterministic trial noise. Its purpose is to verify exact recovery of the locked estimand, parsing behavior, repeated-trial handling, and output generation. Placebo p-values are not substantive findings.

## Reliability checks

The preregistered study includes two prompt paraphrases, randomized request order, equal-length treatment formatting, manipulation checks, repeated-call variance, and parser-failure rates by treatment. A later model snapshot is a separate replication.

## Limits

This synthetic audit measures model behavior under a specific configuration. It does not measure actual employer discrimination, downstream hiring outcomes, legal liability, or a person's true protected status. Results can change across models, dates, prompts, and provider infrastructure.

## Responsible disclosure

Reproduce disparities with a locked configuration, estimate practical magnitude and uncertainty, test sensitivity, document the exact model and date, protect credentials and raw data, and avoid causal or legal claims unsupported by the design.
