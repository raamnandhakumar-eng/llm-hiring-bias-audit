# Gemini feasibility pilot protocol

This pilot is an additive execution check for the existing LLM Hiring Bias Audit. It does not replace or revise the repository's Version 1 or Version 2 materials.

## Status

The pilot is non-confirmatory. On August 17, 2026, the first transport attempt targeted `gemini-2.5-flash`. All 32 requests returned the same provider `404 NOT_FOUND` because that model was unavailable to new API users. No Gemini screening output was returned or analyzed.

Before any successful Gemini response was observed, the pilot target was updated to `gemini-3.6-flash`. The next attempt established successful connectivity and parsing, but only 6 of 32 calls completed before provider `429 RESOURCE_EXHAUSTED` responses appeared.

A subsequent attempt added fixed 15-second pacing. That attempt produced 18 parsed responses and 14 provider `429 RESOURCE_EXHAUSTED` responses. The provider errors included an explicit retry interval. This confirmed that fixed pacing alone was not sufficient for the project's free-tier quota window.

The pilot runner therefore permits **transport-only retries** for `429 RESOURCE_EXHAUSTED` responses when no model output has been returned. It waits for the provider-supplied retry interval plus a one-second buffer and records the number of transport attempts, rate-limit retries, and total retry wait for each observation. Model outputs, parser failures, refusals, or semantically invalid responses are not retried. This operational change does not alter the selected resumes, randomized execution order, prompts, model, output schema, Claude design, hypotheses, or analysis plan.

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
- 1 model output per résumé
- **32 Gemini screening outputs total**

The matched sets are selected deterministically before any API request.

## Model and execution

- Provider: Google Gemini API
- Model: `gemini-3.6-flash`
- Prompt: `v2.0-primary`
- Sampling: provider-default sampling; Gemini 3.6 sampling parameters such as temperature are not sent
- Thinking level: `minimal`
- Transport retry policy: retry only provider `429 RESOURCE_EXHAUSTED` responses that returned no model output; wait for the provider-supplied retry interval plus one second; maximum five rate-limit retries per observation
- Output: JSON using the same structured screening schema as the core study

## Interpretation

Pilot outputs are descriptive and operational only. No confirmatory treatment-effect estimates, hypothesis-test claims, or cross-provider conclusions will be based on these 32 calls.

## Sequence

1. Freeze a local SHA-256 lock of the Claude confirmatory design.
2. Run the 32-call Gemini feasibility pilot.
3. Preserve the complete pilot output and manifest without overwriting them.
4. Make no Claude-design changes based on pilot outcomes.
5. Run the full Claude confirmatory audit next.
