# Gemini feasibility pilot protocol

This pilot is an additive execution check for the existing LLM Hiring Bias Audit. It does not replace or revise the repository's Version 1 or Version 2 materials.

## Status

The protocol is prospective. It must be frozen before the first live Gemini request.

## Purpose

The Gemini run is a **non-confirmatory feasibility pilot**. It checks only whether the live execution path behaves as expected before the full Claude audit.

The pilot may be used to assess:

- API connectivity;
- JSON and parser success;
- refusal and provider-failure behavior;
- latency;
- output and manifest preservation.

The pilot will **not** be used to revise the hypotheses, résumé treatments, occupations, sample size, primary outcomes, statistical specification, prompt versions, Claude model, or Claude stopping rule.

## Pilot sample

The pilot uses one complete matched set from each of the eight occupations. Each selected matched set contains all four career-gap × education-pathway treatment combinations.

- 8 occupations
- 1 matched set per occupation
- 4 treatment variants per matched set
- 1 call per résumé
- **32 Gemini calls total**

The matched sets are selected deterministically before any API request.

## Model and execution

- Provider: Google Gemini API
- Model: `gemini-2.5-flash`
- Prompt: `v2.0-primary`
- Temperature: `0.0`
- Thinking budget: `0`
- Output: JSON using the same structured screening schema as the core study

## Interpretation

Pilot outputs are descriptive and operational only. No confirmatory treatment-effect estimates, hypothesis-test claims, or cross-provider conclusions will be based on these 32 calls.

## Sequence

1. Freeze and externally preregister the Claude confirmatory design.
2. Run the 32-call Gemini feasibility pilot.
3. Preserve the complete pilot output and manifest without overwriting them.
4. Make no design changes based on pilot outcomes.
5. Run the full preregistered Claude confirmatory audit next.
