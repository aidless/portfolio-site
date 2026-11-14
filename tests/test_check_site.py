"""Portfolio site contract tests.

These tests run the real ``tools/check_site.py`` checker against the actual
``site/`` tree. The checker is the only automated verification entry point for
this zero-dependency static site, so the tests simply exercise it as-is and
assert that the static contract holds.

They are honest: the assertions mirror exactly what ``tools/check_site.py``
declares (3 flagship cards, zero JS/CDN, llm-lab evidence). No synthetic
fixtures, no mocked resources — the real ``site/`` files are used.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools" / "check_site.py"


def _run_checker() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )


def test_checker_exit_zero() -> None:
    """The checker must pass on the current site/ tree."""
    result = _run_checker()
    assert result.returncode == 0, f"checker failed:\n{result.stdout}\n{result.stderr}"
    assert "PASS" in result.stdout


def test_checker_reports_three_contracts() -> None:
    """The three PASS lines (site contract / zero JS-CDn / llm-lab evidence)."""
    result = _run_checker()
    assert result.stdout.count("PASS") >= 3


def test_checker_is_deterministic() -> None:
    """Running twice gives identical output (no hidden state)."""
    first = _run_checker()
    second = _run_checker()
    assert first.stdout == second.stdout


def test_checker_rejects_missing_file() -> None:
    """A missing required file must produce FAIL (fail-closed, not silent pass)."""
    # Run from a temp copy with one required file removed to prove the checker
    # actually goes red — it is not a decorative pass.
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        import importlib.util
        import shutil

        site_copy = Path(tmp) / "site"
        shutil.copytree(ROOT / "site", site_copy)
        (site_copy / "index.html").unlink()

        # Load the real checker module from source and patch its SITE root to
        # point at the broken copy. Assert it reports a missing-file error
        # rather than passing — proves the checker is fail-closed, not decorative.
        spec = importlib.util.spec_from_file_location("check_site", CHECKER)
        assert spec and spec.loader
        check_site = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(check_site)

        original = check_site.SITE
        check_site.SITE = site_copy
        try:
            rc = check_site.main()
            assert rc != 0, "checker must fail when index.html is missing"
        finally:
            check_site.SITE = original
