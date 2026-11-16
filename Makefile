PYTHON ?= python3

.PHONY: eval check refresh

check:
	$(PYTHON) tools/check_site.py
	$(PYTHON) tools/check_provenance.py --selftest

refresh:
	$(PYTHON) tools/refresh_evidence.py

eval:
	$(PYTHON) eval/run_cases.py
	@if $(PYTHON) -c "import pytest" >/dev/null 2>&1; then $(PYTHON) -m pytest -q tests; else echo "pytest 未安装，跳过既有 tests（run_cases 已跑）"; fi
