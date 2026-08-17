# Gemini feasibility pilot protocol

The Gemini run is a **non-confirmatory feasibility pilot**. It is not the primary audit and its treatment estimates will not be used as confirmatory evidence.

## Purpose

The pilot checks whether the live provider path works as intended before the preregistered Claude confirmatory audit. It is limited to operational questions:

- API connectivity;
- JSON compliance and parser success;
- refusal and provider-failure behavior;
- latency;
- preservation of raw outputs and manifests.

The pilot must not be used to revise hypotheses, treatment wording, occupations, sample size, primary outcomes, statistical models, prompt versions, or the Claude stopping rule.

## Sample

The pilot contains one complete matched set from each of the eight occupations. Each matched set contains all four career-gap × education-pathway conditions.

- 8 occupations;
- 1 matched set per occupation;
- 4 treatment variants per matched set;
- 1 call per resume;
- **32 total Gemini calls**.

The selection is deterministic and occurs before API execution.

## Model

- Provider: Google Gemini API
- Model: `gemini-2.5-flash`
- Prompt: `v2.0-primary`
- Temperature: 0.0
- Thinking budget: 0
- Output format: JSON

## Interpretation

Pilot outcomes are descriptive only. No p-values, confirmatory treatment-effect claims, or model-comparison claims will be based on these 32 calls.

## Sequence

1. Freeze and externally preregister the Claude confirmatory design.
2. Run the 32-call Gemini feasibility pilot.
3. Preserve the pilot output without overwriting it.
4. Make no design changes based on pilot outcomes.
5. Run the full Claude confirmatory audit next.
