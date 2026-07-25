# LLM Hiring Bias Audit

Code for a matched-resume audit of career gaps and education pathways in LLM hiring evaluations.

## Setup

```bash
git clone https://github.com/raamnandhakumar-eng/llm-hiring-bias-audit.git
cd llm-hiring-bias-audit
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
```

## Usage

Run the mock audit:

```bash
make core-reproduce
```

Run the live audit after submitting the external registration:

```bash
python -m pip install -e ".[api]"
export EXTERNAL_PREREGISTRATION_URL="https://osf.io/xxxxx"
export ANTHROPIC_API_KEY="..."
export ANTHROPIC_MODEL="exact-model-id"
make core-live
```
