# Resume treatment balance report

This report is deterministic and was generated before any live-model output.

## Exact within-set checks

| metric                       |   maximum_variants_within_matched_set |   matched_sets_with_imbalance | pass   |
|:-----------------------------|--------------------------------------:|------------------------------:|:-------|
| skills_count                 |                                     1 |                             0 | True   |
| years_experience             |                                     1 |                             0 | True   |
| quantified_achievement_count |                                     1 |                             0 | True   |
| invariant_text_hash          |                                     1 |                             0 | True   |
| word_count                   |                                     1 |                             0 | True   |
| sentence_count               |                                     1 |                             0 | True   |

## Mean text metrics by treatment cell

| education_pathway   |   career_gap_months |   word_count |   sentence_count |   skills_count |   years_experience |   quantified_achievement_count |   readability_flesch |
|:--------------------|--------------------:|-------------:|-----------------:|---------------:|-------------------:|-------------------------------:|---------------------:|
| nontraditional      |                   0 |      78.2188 |          2.03125 |              5 |               6.25 |                        1.71875 |             -31.1122 |
| nontraditional      |                  12 |      78.2188 |          2.03125 |              5 |               6.25 |                        1.71875 |             -30.0284 |
| traditional         |                   0 |      78.2188 |          2.03125 |              5 |               6.25 |                        1.71875 |             -30.0284 |
| traditional         |                  12 |      78.2188 |          2.03125 |              5 |               6.25 |                        1.71875 |             -28.9444 |

The readability score may move slightly because the treatment wording is the signal being manipulated. Skills, experience, achievements, names, occupation, and all non-treatment text remain fixed within each matched set.
