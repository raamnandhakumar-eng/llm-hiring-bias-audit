# Confirmatory execution protocol pointer

This file is the stable protocol entry point checked by `run_all.py`.

It does **not** create or claim a new external preregistration. The authoritative prospective record for the Claude confirmatory execution remains:

- [`docs/claude_confirmatory_protocol.md`](docs/claude_confirmatory_protocol.md)
- `docs/claude_confirmatory_design_lock.json`
- [`config/claude_confirmatory.yaml`](config/claude_confirmatory.yaml)

The locked confirmatory design is unchanged:

- model: `claude-sonnet-4-6`
- temperature: `0.0`
- 8 occupations
- 32 matched base profiles
- 128 synthetic resumes
- 2 × 2 career-gap × education-pathway design
- 5 evaluations per resume
- 640 primary evaluations
- randomized execution order
- no selective reruns of observed model outputs

This convenience file was added only to provide a single, obvious protocol check for the one-command runner. It does not alter the hypotheses, treatments, sample, analysis, prior results, or historical research record.
