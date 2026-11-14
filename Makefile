PYTHON ?= python3

.PHONY: eval

eval:
	$(PYTHON) eval/run_cases.py
	@if $(PYTHON) -c "import pytest" >/dev/null 2>&1; then $(PYTHON) -m pytest -q tests; else echo "pytest 未安装，跳过既有 tests（run_cases 已跑）"; fi
