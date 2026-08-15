.PHONY: install test validate-names simulate-name-pretest generate placebo analyze \
	power figures reproduce live core-generate core-placebo core-analyze \
	core-reproduce core-live select-balanced-names clean balance \
	v2-validate v2-live core-manipulation core-prompt-robustness \
	core-figure prereg-lock human-benchmark

install:
	python -m pip install -e ".[dev]"

test:
	ruff check .
	pytest -q

validate-names:
	hiring-audit-validate-names --config config/audit.yaml

simulate-name-pretest:
	hiring-audit-simulate-name-pretest --config config/audit.yaml

generate:
	hiring-audit-generate --config config/audit.yaml

placebo: generate
	hiring-audit-run --config config/audit.yaml --provider mock

analyze:
	hiring-audit-analyze --input outputs/screening_results.csv --output-dir outputs/analysis

power:
	python scripts/power_analysis.py

balance:
	python scripts/audit_resume_balance.py

figures:
	python scripts/make_result_figures.py

reproduce:
	bash scripts/reproduce_all_results.sh

live:
	bash scripts/run_live_audit.sh

core-generate:
	hiring-audit-generate --config config/core_audit.yaml

core-placebo: core-generate
	hiring-audit-run \
		--config config/core_audit.yaml \
		--provider mock \
		--results-path outputs/core_placebo/screening_results.csv \
		--manifest-path outputs/core_placebo/run_manifest.json

core-analyze:
	hiring-audit-analyze-core \
		--input outputs/core_placebo/screening_results.csv \
		--output-dir outputs/core_placebo/analysis

core-reproduce:
	bash scripts/reproduce_core_placebo.sh

core-live:
	bash scripts/run_core_live_audit.sh

core-manipulation:
	hiring-audit-manipulation-check --config config/core_audit.yaml --provider anthropic

core-prompt-robustness:
	bash scripts/run_prompt_robustness.sh

core-figure:
	python scripts/make_core_result_figure.py

prereg-lock:
	python scripts/lock_preregistration.py

human-benchmark:
	@test -n "$(HUMAN_FILE)" || (echo "Set HUMAN_FILE to the evaluator CSV." >&2; exit 1)
	python scripts/analyze_human_benchmark.py --human "$(HUMAN_FILE)"

v2-validate:
	python scripts/power_analysis.py
	python scripts/audit_resume_balance.py
	bash scripts/reproduce_core_placebo.sh
	hiring-audit-manipulation-check \
		--config config/core_audit.yaml \
		--provider mock \
		--results-path outputs/core_placebo/manipulation_checks.csv \
		--summary-path outputs/core_placebo/manipulation_check_summary.csv
	pytest -q

v2-live:
	bash scripts/run_v2_live_audit.sh

select-balanced-names:
	hiring-audit-select-balanced-names \
		--input results/name_validation/replacement_candidate_summary.csv

clean:
	rm -rf outputs/*.csv outputs/*.json outputs/analysis outputs/core
