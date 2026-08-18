# Limitations

LLM Hiring Bias Audit is a controlled synthetic audit, not a study of real applicants, employers, or hiring outcomes.

The main limitations are:

- Names are perceived signals. Census and SSA aggregates do not establish a person's race, ethnicity, gender, nationality, or socioeconomic status.
- Source screening is not a substitute for the locked human perception pretest required by the separate name-signal extension.
- Eight occupations improve coverage but cannot support economy-wide claims.
- Synthetic resumes simplify the information and strategic behavior present in real hiring.
- Repeated calls estimate model instability under the locked setup, not across every deployment environment.
- Fit scores and interview recommendations are model-generated judgments rather than observed employment decisions.
- Explanation themes are generated text and are treated as secondary outcomes.
- Treatment effects may depend on the exact model ID, prompt wording, run date, temperature, API implementation, and provider infrastructure.
- Occupational comparisons use public national aggregates and do not capture local labor-market variation.
- The Gemini feasibility sample is operational and quota-limited: 18 valid returned outputs across all eight occupations, not a complete 32-observation inferential sample.
- The current Claude execution is prospectively code-locked rather than externally preregistered; earlier OSF-ready materials are retained only as historical project artifacts.
- No live Claude output has yet been collected, so the repository does not currently support a substantive claim about Claude hiring-screening behavior.

Economic interpretation is limited to possible mechanisms involving labor-market access, occupational mobility, career interruptions, non-traditional education, frontline versus knowledge-work screening, and algorithmic gatekeeping within the study sample.
