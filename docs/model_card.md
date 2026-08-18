# LLM Hiring Bias Audit model card

## Intended use

LLM Hiring Bias Audit measures whether one exact language model changes structured resume-screening outputs when controlled synthetic career signals change and qualifications remain fixed.

The core study tests career gaps and education pathways across frontline and knowledge-work occupations. It is a research audit and must not be used to rank real applicants or make employment decisions.

## Current model status

- Placebo provider: `mock-auditor-v2` completed for the original 1,280-evaluation software validation.
- Core placebo provider: `mock-auditor-v3` completed the 640-evaluation core pipeline and estimator validation.
- Name-extension placebo provider: `mock-auditor-v3` is used only for software validation of the blocked extension.
- Gemini feasibility provider: `gemini-3.6-flash`; 18 valid returned screening outputs were preserved across all 8 occupations, 18/18 parsed successfully, and 0/18 were refusals before the free-tier requests-per-day quota became binding. These outputs are non-confirmatory.
- Claude confirmatory provider: `claude-sonnet-4-6`; selected and locked, **not yet run**.
- Primary prompt: `v2.0-primary`; `v2.0-concise` and `v2.0-rubric` are post-primary robustness prompts.

## Prospective Claude design lock

The current Claude execution does not require external OSF or AsPredicted registration. Before the first Claude API request, `scripts/lock_claude_confirmatory.py` creates `docs/claude_confirmatory_design_lock.json`, a SHA-256 manifest covering the confirmatory configuration, prompts, provider and execution code, analysis code, and synthetic résumé templates.

The Claude run is therefore described as **prospectively code-locked**, not externally preregistered.

Earlier OSF-ready and AsPredicted-ready materials remain preserved as historical Version 1/Version 2 artifacts. They are not presented as evidence that an external preregistration occurred.

## Inputs

Synthetic resumes, a fixed target-role description, a locked system prompt, and a locked user-prompt format.

## Outputs

Primary structured outputs are fit score, interview recommendation, and confidence. Free-text explanations are secondary.

## Data retention

Every raw response, refusal, parsing failure, provider failure, error type, prompt, exact model identifier, timestamp, temperature, trial number, execution order, and latency is retained. The run manifest also records whether external preregistration was present. Selective reruns of observed model outputs are prohibited.

## Known limitations

Model behavior may change across exact model IDs, dates, prompts, temperatures, and providers. The occupational sample is purposive and synthetic. The Gemini feasibility sample is incomplete by design because provider quota became binding, and it is not used for treatment-effect inference. Audit results do not establish employer behavior, legal liability, model intent, effects on actual applicants, economy-wide effects, or actual demographic identity.
