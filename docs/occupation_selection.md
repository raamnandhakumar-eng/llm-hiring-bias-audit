# Why these eight occupations

The audit uses a purposive contrast sample. It is not a representative sample of all U.S. jobs. The eight occupations were fixed before the live run to span work setting, wages, education pathways, employment scale, and observed AI exposure.

| Occupation | Broad group | 2025 median wage | Typical education | Observed AI exposure | Exposure band |
|---|---|---:|---|---:|---|
| Production supervisors | Frontline or operational | $74,443 | High school plus experience | 0.000 | Q0 |
| Registered nurses | Frontline or operational | $97,552 | Associate or bachelor's degree plus license | 0.060 | Q2 |
| Maintenance workers | Frontline or operational | $49,587 | High school plus technical training | 0.000 | Q0 |
| Logisticians | Frontline or operational | $82,326 | Bachelor's degree | 0.157 | Q3 |
| Management analysts | Knowledge work | $101,858 | Bachelor's degree | 0.244 | Q3 |
| Project management specialists | Knowledge work | $102,315 | Bachelor's degree | Not available | Not available |
| Computer systems analysts | Knowledge work | $105,851 | Bachelor's degree | 0.276 | Q4 |
| Financial analysts | Knowledge work | $102,752 | Bachelor's degree | 0.572 | Q4 |

## Selection logic

- **Work setting:** four roles are tied to production, patient care, facilities, or physical supply chains. Four center on analysis, systems, finance, or coordination.
- **Wages:** the sample ranges from about $49,600 to $105,900 in annual median pay.
- **Education:** the sample includes high-school, technical, associate, bachelor's, and licensed pathways.
- **Employment scale:** selected roles include both very large occupations and smaller specialist occupations.
- **AI exposure:** the sample includes zero-observed-use occupations, middle-exposure occupations, and high-exposure knowledge work.
- **Screening plausibility:** every role commonly uses written resumes and has qualifications that can be represented in a standardized synthetic profile.

## Important boundaries

The frontline label describes operational context. It does not mean every task is physical. Logisticians, nurses, and supervisors perform both information and in-person work.

Gender composition was not used to select occupations and is not a treatment. The core study does not infer gender or estimate gender effects. Adding gender composition after selecting the sample would not improve identification and could invite unsupported demographic interpretation.

The project-management occupation does not have an exact match in the exposure release used here. It remains in the design because it was selected for the occupation contrast before live results. The missing exposure value is shown rather than imputed.

## Sources

- Wages and employment: BLS OEWS, May 2025 national estimates.
- Education and occupation definitions: O*NET 30.3.
- Exposure: Anthropic Economic Index occupation snapshot, carried through the documented exposure pipeline.

Machine-readable sources are in `data/occupations/occupation_registry.csv` and `data/occupations/ai_exposure_snapshot.csv`.
