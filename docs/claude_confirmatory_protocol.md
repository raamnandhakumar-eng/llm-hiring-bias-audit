# Claude confirmatory audit protocol

## Status

The Gemini feasibility pilot is complete and is not used for confirmatory inference. The next live-model stage is a prospectively code-locked audit of `claude-sonnet-4-6`.

No Claude screening response has been collected or analyzed at the time this protocol is written.

## Confirmatory design

The Claude audit preserves the existing Version 2 matched-resume design:

- 8 occupations;
- 32 matched base profiles;
- 128 synthetic resumes;
- 2 × 2 career-gap × education-pathway treatment structure;
- 5 evaluations per resume;
- 640 primary evaluations;
- exact model ID `claude-sonnet-4-6`;
- primary prompt `v2.0-primary`;
- temperature `0.0`;
- randomized execution order;
- no selective reruns of observed model outputs;
- clustered inference by `matched_set_id`;
- Benjamini-Hochberg correction across the 12 primary linear tests.

The primary outcomes remain fit score, interview recommendation, and model confidence.

## Prospective code lock

Before the first Claude API request, `scripts/lock_claude_confirmatory.py` writes a SHA-256 manifest of the confirmatory design, prompts, provider implementation, analysis code, and resume templates to `docs/claude_confirmatory_design_lock.json`.

The lock is created before any Claude response is observed. It is the prospective audit record for this execution layer.

External OSF or AsPredicted registration is not required for this Claude run. The repository retains earlier OSF-ready materials as historical Version 1/Version 2 research artifacts, but the current Claude execution is described as **prospectively code-locked**, not externally preregistered.

## Gemini pilot boundary

The Gemini pilot returned 18 valid screening responses across all eight occupations before the free-tier requests-per-day quota became binding. All 18 returned outputs parsed successfully and none was classified as a refusal.

Those outputs are operational evidence only. They are not used to revise the Claude hypotheses, treatment construction, occupations, sample size, prompts, model choice, stopping rule, or statistical specification.

## Post-primary checks

Only after all 640 primary Claude observations are attempted:

1. run the factual manipulation check;
2. run the two locked prompt-robustness variants (`v2.0-concise` and `v2.0-rubric`);
3. preserve every success, refusal, parser failure, and provider failure;
4. report effect sizes, uncertainty, and multiplicity-adjusted results without replacing the primary estimate with a robustness result.

## Interpretation

The audit estimates behavior of one exact Claude model under one controlled synthetic screening configuration. It does not establish employer behavior, applicant outcomes, unlawful discrimination, model intent, or population-wide hiring effects.
