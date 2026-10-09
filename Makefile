PYTHON ?= python3

.PHONY: install test lint demo-safe demo-blocked dashboard

install:
	$(PYTHON) -m pip install -e '.[dev]'

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m ruff check src tests

demo-safe:
	$(PYTHON) -m originfence.cli demo safe

demo-blocked:
	$(PYTHON) -m originfence.cli demo blocked

dashboard:
	$(PYTHON) -m originfence.cli dashboard
