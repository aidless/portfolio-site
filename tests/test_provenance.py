"""Offline provenance: site phrases must match committed upstream quotes.

The checker reads evidence/sources.json and the snapshot files. It does not
use the network. These tests exercise that function on the real tree and on
a tiny fixture that is missing a quoted phrase.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools" / "check_provenance.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_provenance", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_real_tree_matches_snapshots() -> None:
    module = _load()
    errors = module.evaluate(ROOT)
    assert errors == [], "\n".join(errors)


def test_missing_site_phrase_fails(tmp_path: Path) -> None:
    module = _load()
    claim = {
        "id": "fixture.quote",
        "kind": "quote",
        "repo": "example/repo",
        "commit": "a" * 40,
        "path": "README.md",
        "snapshot": "evidence/snapshots/fixture.txt",
        "quote": "alpha 10/12 omega",
        "value": "10/12",
        "site_text": "10/12",
    }
    snap = tmp_path / "evidence" / "snapshots"
    snap.mkdir(parents=True)
    (snap / "fixture.txt").write_text(
        "repo: example/repo\n"
        "commit: " + ("a" * 40) + "\n"
        "path: README.md\n"
        "fetched_at: 2026-11-16\n"
        "\n"
        "alpha 10/12 omega\n",
        encoding="utf-8",
    )
    (tmp_path / "evidence").mkdir(exist_ok=True)
    (tmp_path / "evidence" / "sources.json").write_text(
        json.dumps({"schema": 1, "fetched_at": "2026-11-16", "claims": [claim]}),
        encoding="utf-8",
    )
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text("<p>no ratio here</p>", encoding="utf-8")
    errors = module.evaluate(tmp_path)
    assert errors, "a site that drops the quoted value must fail"
    assert any("10/12" in item for item in errors)


def test_stale_counts_are_not_on_the_site() -> None:
    html = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
    assert "16/16" not in html
    assert "391 passed" not in html


def test_jsonl_ratio_counts_non_null_rows() -> None:
    module = _load()
    rows = [
        {"strategy": "structure", "recall@5": True},
        {"strategy": "structure", "recall@5": False},
        {"strategy": "structure", "recall@5": None},
        {"strategy": "fixed", "recall@5": True},
    ]
    assert module.jsonl_ratio(rows, "structure", "recall@5") == "1/2"


def test_quote_claim_holds_only_when_the_line_is_present() -> None:
    module = _load()
    claim = {"kind": "quote", "quote": "6 passed", "value": "6 passed"}
    assert module.claim_holds(claim, "pytest → 6 passed")
    assert not module.claim_holds(claim, "pytest → 5 passed")
