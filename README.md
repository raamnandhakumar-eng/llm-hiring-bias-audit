# LLM Hiring Bias Audit

Matched-resume audit for testing whether a 12-month career gap or non-traditional education pathway changes an LLM hiring evaluation.

## Status

- Core design: locked
- Planned live run: 128 resumes × 5 trials = 640 evaluations
- Mock validation: complete
- Live Claude audit: not run
- External preregistration: prepared but not submitted
- Name pretest: submitted but not approved
- Name-signal extension: blocked and outside the four-month scope

The mock run validates the code and estimator. It is not evidence about Claude, employers, or real applicants.

## Requirements

- Python 3.10 or later
- `make`
- Anthropic API access for live runs only

## Install

```bash
git clone https://github.com/raamnandhakumar-eng/llm-hiring-bias-audit.git
cd llm-hiring-bias-audit
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
```

## Run the mock validation

```bash
make core-reproduce
```

Run the full validation workflow:

```bash
make reproduce
```

## Run the live core audit

Submit the external preregistration first, then set the required environment variables:

```bash
python -m pip install -e ".[api]"
export EXTERNAL_PREREGISTRATION_URL="https://osf.io/xxxxx"
export ANTHROPIC_API_KEY="..."
export ANTHROPIC_MODEL="exact-model-id"
make core-live
```

The live runner rejects missing or invalid OSF and AsPredicted URLs. API keys must not be committed.

## Outputs

- Core results: `outputs/core/`
- Core placebo report: `results/core/placebo_validation_report.md`
- Name-pretest results: `results/name_validation/`

## Design files

- Core plan: [`docs/core_audit_preregistration.md`](docs/core_audit_preregistration.md)
- OSF text: [`docs/osf_preregistration.md`](docs/osf_preregistration.md)
- AsPredicted text: [`docs/aspredicted_preregistration.md`](docs/aspredicted_preregistration.md)
- Design changes: [`docs/deviations_from_preregistration.md`](docs/deviations_from_preregistration.md)
- Limits: [`docs/limitations.md`](docs/limitations.md)

## Limits

This audit measures model behavior under a controlled synthetic design. It does not measure employer behavior, prove intent, establish unlawful discrimination, or identify anyone's demographic identity.

Any live result applies only to the model, prompt, run period, treatments, and occupations used in that run.

## License

MIT. See [`LICENSE`](LICENSE).
