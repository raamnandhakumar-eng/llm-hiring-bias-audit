# Gemini feasibility pilot protocol

This pilot is an additive execution check for the existing LLM Hiring Bias Audit. It does not replace or revise the repository's Version 1 or Version 2 materials.

## Status

**Feasibility established; pilot closed.** The Gemini exercise is non-confirmatory and no Gemini outcome is used to revise the Claude design.

On August 17, 2026, the first transport attempt targeted `gemini-2.5-flash`. All 32 requests returned the same provider `404 NOT_FOUND` because that model was unavailable to new API users. No Gemini screening output was returned or analyzed.

Before any successful Gemini response was observed, the pilot target was updated to `gemini-3.6-flash`. A subsequent paced attempt returned **18 valid Gemini screening responses across all eight occupations**. All 18 returned responses parsed successfully under the locked JSON schema and none was classified as a refusal. The remaining 14 planned calls returned provider `429 RESOURCE_EXHAUSTED` errors.

The provider error identified the binding constraint as `GenerateRequestsPerDayPerProjectPerModel-FreeTier`, with an active limit of 20 requests for `gemini-3.6-flash`. A later transport-only retry attempt was cancelled by GitHub after the one-hour workflow timeout because a requests-per-day quota cannot be resolved by short-interval retries.

The feasibility objective was therefore considered met after the 18 successfully returned and parsed responses. No additional Gemini calls are required before the Claude confirmatory audit. The pilot is not treated as a completed 32-observation inferential sample.

## Purpose

The Gemini run is a **non-confirmatory feasibility pilot**. It checks only whether the live execution path behaves as expected before the full Claude audit.

The pilot may be used to assess:

- API connectivity;
- JSON and parser success;
- refusal and provider-failure behavior;
- latency;
- output and manifest preservation.

The pilot will **not** be used to revise the hypotheses, résumé treatments, occupations, sample size, primary outcomes, statistical specification, prompt versions, Claude model, or Claude stopping rule.

## Planned pilot sample

The planned pilot used one complete matched set from each of the eight occupations, with all four career-gap × education-pathway treatment combinations.

- 8 occupations
- 1 matched set per occupation
- 4 treatment variants per matched set
- 1 model output per résumé
- 32 planned Gemini screening outputs

The matched sets were selected deterministically before any API request. Because the pilot is operational rather than inferential, the quota-limited stopping point is reported transparently rather than selectively rerunning or changing the design.

## Model and execution

- Provider: Google Gemini API
- Model: `gemini-3.6-flash`
- Prompt: `v2.0-primary`
- Sampling: provider-default sampling; Gemini 3.6 sampling parameters such as temperature are not sent
- Thinking level: `minimal`
- Returned live outputs: 18
- Parser success among returned outputs: 18/18
- Refusals among returned outputs: 0/18
- Occupations represented among returned outputs: 8/8
- Binding provider constraint: free-tier requests-per-day quota
- Output: JSON using the same structured screening schema as the core study

The runner may retry short-window `429 RESOURCE_EXHAUSTED` transport failures only when no model output has been returned. Requests-per-day quota errors are not retried.

## Interpretation

Gemini outputs are descriptive and operational only. No confirmatory treatment-effect estimates, hypothesis-test claims, or cross-provider conclusions are based on the pilot.

## Sequence

1. Freeze a local SHA-256 lock of the Claude confirmatory design.
2. Establish Gemini execution feasibility without changing the Claude design.
3. Preserve the pilot attempt history and quota failures transparently.
4. Make no Claude-design changes based on pilot outcomes.
5. Proceed to the full Claude confirmatory audit.
