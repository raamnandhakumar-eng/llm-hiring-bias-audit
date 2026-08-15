# Power analysis for the 640-evaluation core audit

This planning analysis was fixed before any live-model output was observed. The mock provider validates code and cannot estimate real model variance.

## Actual core design

- 32 independent matched base profiles
- 4 treatment cells per profile
- 128 unique resumes
- 5 repeated calls per resume
- 640 primary live evaluations

The independent unit is the matched base profile. Primary uncertainty is clustered by `matched_set_id`, not by individual model call.

## Variance assumptions

The calculation separates condition-level variation from repeated-call noise. For fit score, the assumed standard deviations are 0.40 across treatment cells within a profile and 0.60 across repeated calls to the same resume. For interview recommendation, the corresponding probability-scale assumptions are 0.15 and 0.35. These values are planning assumptions, not observed facts.

## Results

| outcome                    | contrast    |   target_effect |   mde_alpha_05_power_80 |   mde_bonferroni_12_power_80 |   power_at_target_alpha_05 |
|:---------------------------|:------------|----------------:|------------------------:|-----------------------------:|---------------------------:|
| fit_score                  | main_effect |            0.3  |                   0.246 |                        0.338 |                      0.927 |
| fit_score                  | interaction |            0.5  |                   0.493 |                        0.676 |                      0.812 |
| recommendation_probability | main_effect |            0.15 |                   0.111 |                        0.152 |                      0.966 |
| recommendation_probability | interaction |            0.2  |                   0.222 |                        0.304 |                      0.715 |

Under the assumptions, 640 evaluations provide at least 80% power for the planned 0.30-point fit-score main effect and 0.15 recommendation-probability main effect. Power is weaker for small frontline interactions. The design is powered for interaction effects near 0.50 fit-score points and about 0.22 probability, not subtle subgroup effects.

The Bonferroni column is a conservative reference for 12 primary outcome-term tests. The preregistered analysis uses Benjamini-Hochberg correction and reports unadjusted confidence intervals alongside adjusted q-values.

## Why five repetitions

Repeating the same resume reduces call-level noise and measures model instability. The largest precision gains occur between one and five calls. Later calls have diminishing returns because condition-level variation remains. Five calls are a defensible stability choice, but adequacy depends on the realized variance reported after the run.

![Minimum detectable effect by repetitions](figures/power_by_repetitions.svg)

## Limits

Analytic power uses a two-sided t-test approximation with 32 independent matched profiles. It depends on uncertain variance assumptions. The final report will compare these assumptions with observed repeated-call variance. The sample and stopping rule will not change in response to live treatment estimates.

Reproduce with `python scripts/power_analysis.py`.
