# Group 9 MSR 2027 pipeline. Works in Linux, macOS, and Windows Git Bash.
# Usage: make <target>. Run `make help` to list targets.

PY ?= python
VENV ?= .venv
ifeq ($(OS),Windows_NT)
  VENV_PY := $(VENV)/Scripts/python.exe
else
  VENV_PY := $(VENV)/bin/python
endif

.PHONY: help setup data data-all test lint format explore analyze metrics tally reproduce clean pipeline figures notebook-sources interview interview-checks verify-spec

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

setup: ## Create the virtual environment and install the package with dev tools
	$(PY) -m venv $(VENV)
	$(VENV_PY) -m pip install --upgrade pip
	$(VENV_PY) -m pip install -e ".[dev]"
	@echo "Activate with: source $(VENV)/bin/activate  (Linux/macOS)  or  source $(VENV)/Scripts/activate  (Git Bash)"

data: ## Download the GitSkills and core SpecMine samples into data/samples
	$(PY) scripts/download_samples.py --dataset all

data-all: ## Download every SpecMine sample file, including raw spec text
	$(PY) scripts/download_samples.py --dataset all --all-specmine

test: ## Run the test suite with coverage
	$(PY) -m pytest -q --cov=msr_pipeline --cov-report=term-missing

lint: ## Check code style and imports
	$(PY) -m ruff check .
	$(PY) -m ruff format --check .

format: ## Reformat code in place
	$(PY) -m ruff format .
	$(PY) -m ruff check --fix .

explore: ## Produce the exploratory tables and figures for both datasets
	$(PY) -m msr_pipeline explore --dataset all

metrics: ## Compute the Lean Six Sigma sprint metrics from GitHub
	$(PY) scripts/lss_metrics.py

tally: ## Tally the topic proposal ballots
	$(PY) scripts/tally_votes.py

reproduce: data explore analyze test ## Download data, regenerate outputs, and run tests

clean: ## Remove generated outputs and caches (keeps downloaded data)
	rm -rf results/*.csv figures/*.png .pytest_cache .ruff_cache .coverage htmlcov build dist src/*.egg-info
	find . -name __pycache__ -type d -prune -exec rm -rf {} +

analyze: ## Run the P-01 research analysis (RQ1 to RQ3, sensitivity) into results/ and figures/
	$(PY) -m msr_pipeline analyze

# Names used in the sprint and report documents.
pipeline: analyze ## Run the research pipeline end to end (P-01 analysis)

figures: analyze ## Regenerate every research table and figure

# Requirements engineering (RESEARCH_SPEC.md, elicitation/).
notebook-sources: ## Build the elicitation notebook's source pack into build/notebook_sources
	$(PY) scripts/build_notebook_sources.py

interview: ## Ask the notebook every question in elicitation/questions.yaml; writes the transcript
	$(PY) -m msr_pipeline elicit

interview-checks: ## Check the interview's data claims against the sample (V01 to V18)
	$(PY) scripts/check_interview_claims.py

verify-spec: ## Run the acceptance tests in RESEARCH_SPEC.md; writes results/spec_verification.csv
	$(PY) scripts/verify_spec.py
