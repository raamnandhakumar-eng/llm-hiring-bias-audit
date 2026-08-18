# Gemini feasibility pilot summary

## Status

**Complete for feasibility purposes.** The Gemini stage is closed and no further Gemini execution is planned before the Claude confirmatory audit.

The pilot is non-confirmatory. It is not used to estimate treatment effects or to revise the Claude design.

## What was established

Using `gemini-3.6-flash`, the audit obtained **18 valid screening responses spanning all eight occupations** before the free-tier requests-per-day quota became binding.

- returned Gemini outputs: **18**
- successfully parsed outputs: **18/18 (100%)**
- refusals among returned outputs: **0/18**
- occupations represented: **8/8**
- inferential use: **none**

This establishes that the live provider path, prompt, structured JSON response, parser, logging, and synthetic-resume inputs work against a real external model.

## Preserved run provenance

The preserved 18-response evidence comes from GitHub Actions run **32082061296** (`Gemini feasibility pilot #3`).

- artifact name: `gemini-pilot-32082061296`
- artifact ID: `9305606430`
- artifact SHA-256 digest: `d09b2d3c88ba84bcc6ea954984c378b9ee9009a0d58694f4fb3a49a2cf565a4f`
- manifest rows: 32 scheduled observations
- successful rows: 18
- failed rows: 14
- exact model ID: `gemini-3.6-flash`
- prompt version: `v2.0-primary`
- randomized execution order: yes
- selective reruns permitted: no

The artifact contains the run manifest and the full 32-row attempt record, including the 18 returned model outputs and the 14 provider-failure rows.

## Attempt history

1. The first transport attempt targeted `gemini-2.5-flash`; the provider returned `404 NOT_FOUND` for all requests because that model was unavailable to the API project. No model screening output was observed.
2. The target was updated before any successful Gemini output to `gemini-3.6-flash`. A subsequent attempt produced 6 valid parsed outputs before quota responses.
3. A paced attempt produced the preserved pilot evidence used here: **18 valid outputs across all eight occupations**, all parsed successfully, with no refusals. The remaining scheduled calls were blocked by provider quota.
4. A final operational attempt added transport-only retry handling but encountered the free-tier requests-per-day cap and reached the one-hour GitHub Actions timeout. No additional completed pilot dataset replaced the preserved 18-response attempt.

The final code distinguishes short-window rate limits from per-day quota limits so daily quota errors are not retried indefinitely.

## Research boundary

No Gemini screening outcome is used to alter:

- the Claude model (`claude-sonnet-4-6`);
- the 8 occupations;
- the 32 matched base profiles;
- the 128 synthetic resumes;
- the career-gap or education treatments;
- the 640-evaluation primary sample;
- the primary or robustness prompts;
- the stopping rule;
- the statistical specification;
- the primary outcomes.

The Gemini pilot is therefore reported as an **operational feasibility check**, not a substantive finding or cross-provider result.

## Next stage

The next live-model stage is the prospectively code-locked Claude confirmatory audit documented in [`claude_confirmatory_protocol.md`](claude_confirmatory_protocol.md).
