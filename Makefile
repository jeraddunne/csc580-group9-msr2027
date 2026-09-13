# Group 9 MSR 2027 pipeline. Works in Linux, macOS, and Windows Git Bash.
# Usage: make <target>. Run `make help` to list targets.

PY ?= python
VENV ?= .venv
ifeq ($(OS),Windows_NT)
  VENV_PY := $(VENV)/Scripts/python.exe
else
  VENV_PY := $(VENV)/bin/python
endif

.PHONY: help setup data data-all test lint format explore metrics tally reproduce clean pipeline figures

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

reproduce: data explore test ## Download data, regenerate outputs, and run tests

clean: ## Remove generated outputs and caches (keeps downloaded data)
	rm -rf results/*.csv figures/*.png .pytest_cache .ruff_cache .coverage htmlcov build dist src/*.egg-info
	find . -name __pycache__ -type d -prune -exec rm -rf {} +

# Aliases used in the sprint and report documents. Until the research pipeline for the
# selected question exists, both run the exploratory pipeline.
pipeline: explore ## Run the research pipeline end to end (alias, see docs/sprints)

figures: explore ## Regenerate every table and figure (alias)
