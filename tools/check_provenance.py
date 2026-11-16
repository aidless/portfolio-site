#!/usr/bin/env python3
"""Offline check: site phrases match the committed upstream snapshots.

This tool does not contact the network. It fails if a quoted line, a counted
excerpt, or a JSONL ratio in evidence/ disagrees with evidence/sources.json
or with site/index.html.
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HEX40 = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_CLAIM_KEYS = {
    "id",
    "kind",
    "repo",
    "commit",
    "path",
    "snapshot",
    "value",
    "site_text",
}


def jsonl_ratio(rows: list[dict], strategy: str, field: str) -> str:
    """Count true values over rows where strategy matches and field is not null."""
    scoped = [
        row
        for row in rows
        if row.get("strategy") == strategy and row.get(field) is not None
    ]
    hits = sum(1 for row in scoped if row.get(field) is True)
    return f"{hits}/{len(scoped)}"


def claim_holds(claim: dict, text: str) -> bool:
    """Return whether upstream file text still supports this claim."""
    kind = claim.get("kind")
    if kind == "quote":
        return claim["quote"] in text
    if kind == "lines":
        if any(line not in text for line in claim["lines"]):
            return False
        pattern = claim.get("count_pattern")
        if pattern:
            return len(re.findall(pattern, text, re.M)) == int(claim["value"])
        return True
    if kind == "jsonl_ratio":
        rows = [json.loads(line) for line in text.splitlines() if line.strip()]
        return jsonl_ratio(rows, claim["strategy"], claim["field"]) == claim["value"]
    return False


def _split_snapshot(text: str) -> tuple[dict[str, str], str]:
    header, sep, body = text.partition("\n\n")
    if not sep:
        raise ValueError("snapshot is missing the blank line after its header")
    fields: dict[str, str] = {}
    for line in header.splitlines():
        if ": " not in line:
            raise ValueError(f"snapshot header line has no key: {line}")
        key, value = line.split(": ", 1)
        fields[key] = value
    if body.endswith("\n"):
        body = body[:-1]
    return fields, body


def _load_sources(root: Path) -> dict:
    path = root / "evidence" / "sources.json"
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(root: Path) -> list[str]:
    """Return a list of provenance errors. Empty means the tree matches."""
    errors: list[str] = []
    try:
        sources = _load_sources(root)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"evidence/sources.json: {exc}"]

    fetched_at = sources.get("fetched_at")
    if not isinstance(fetched_at, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fetched_at):
        errors.append("sources.json fetched_at must be YYYY-MM-DD")
    claims = sources.get("claims")
    if not isinstance(claims, list) or not claims:
        errors.append("sources.json claims must be a non-empty list")
        return errors

    html_path = root / "site" / "index.html"
    try:
        html = html_path.read_text(encoding="utf-8")
    except OSError as exc:
        return errors + [f"site/index.html: {exc}"]

    for forbidden in sources.get("forbidden_site_text", []):
        if forbidden in html:
            errors.append(f"site still contains withdrawn text: {forbidden}")

    seen_ids: set[str] = set()
    for claim in claims:
        missing = REQUIRED_CLAIM_KEYS - set(claim)
        label = claim.get("id", "<missing id>")
        if label in seen_ids:
            errors.append(f"{label}: duplicate claim id")
        seen_ids.add(str(label))
        if missing:
            errors.append(f"{label}: missing keys {sorted(missing)}")
            continue
        if not HEX40.fullmatch(claim["commit"]):
            errors.append(f"{label}: commit is not a 40-hex SHA")
        snapshot_path = root / claim["snapshot"]
        if not snapshot_path.is_file():
            errors.append(f"{label}: missing snapshot {claim['snapshot']}")
            continue
        try:
            header, body = _split_snapshot(snapshot_path.read_text(encoding="utf-8"))
        except ValueError as exc:
            errors.append(f"{label}: {exc}")
            continue
        for key, expected in (
            ("repo", claim["repo"]),
            ("commit", claim["commit"]),
            ("path", claim["path"]),
            ("fetched_at", fetched_at),
        ):
            if header.get(key) != expected:
                errors.append(
                    f"{label}: snapshot {key} is {header.get(key)!r}, expected {expected!r}"
                )
        kind = claim["kind"]
        if kind == "quote":
            if body != claim["quote"]:
                errors.append(f"{label}: snapshot body is not the recorded quote")
            elif claim["value"] not in claim["quote"]:
                errors.append(f"{label}: value is not inside the quote")
        elif kind == "lines":
            lines = body.split("\n") if body else []
            if lines != claim["lines"]:
                errors.append(f"{label}: snapshot lines differ from sources.json")
            elif str(len(lines)) != str(claim["value"]):
                errors.append(
                    f"{label}: counted {len(lines)} lines, value is {claim['value']}"
                )
        elif kind == "jsonl_ratio":
            try:
                rows = [json.loads(line) for line in body.splitlines() if line.strip()]
                got = jsonl_ratio(rows, claim["strategy"], claim["field"])
            except (json.JSONDecodeError, KeyError) as exc:
                errors.append(f"{label}: jsonl ratio failed: {exc}")
                got = None
            if got is not None and got != claim["value"]:
                errors.append(f"{label}: jsonl ratio is {got}, value is {claim['value']}")
        else:
            errors.append(f"{label}: unknown kind {kind}")
            continue
        if claim["value"] not in claim["site_text"]:
            errors.append(f"{label}: site_text does not contain value {claim['value']}")
        if claim["site_text"] not in html:
            errors.append(f"{label}: site is missing {claim['site_text']}")
        open_pr = claim.get("open_pr")
        if open_pr is not None:
            if not HEX40.fullmatch(str(open_pr.get("head", ""))):
                errors.append(f"{label}: open_pr.head is not a 40-hex SHA")
            if not isinstance(open_pr.get("quote_on_head"), bool):
                errors.append(f"{label}: open_pr.quote_on_head must be a boolean")
            if not isinstance(open_pr.get("number"), int):
                errors.append(f"{label}: open_pr.number must be an integer")
            if not open_pr.get("note"):
                errors.append(f"{label}: open_pr.note is empty")
    return errors


def _selftest() -> int:
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
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        snap = root / "evidence" / "snapshots"
        snap.mkdir(parents=True)
        (snap / "fixture.txt").write_text(
            "repo: example/repo\n"
            f"commit: {'a' * 40}\n"
            "path: README.md\n"
            "fetched_at: 2026-11-16\n"
            "\n"
            "alpha 10/12 omega\n",
            encoding="utf-8",
        )
        (root / "evidence" / "sources.json").write_text(
            json.dumps(
                {"schema": 1, "fetched_at": "2026-11-16", "claims": [claim]},
            ),
            encoding="utf-8",
        )
        site = root / "site"
        site.mkdir()
        (site / "index.html").write_text("<p>no ratio here</p>", encoding="utf-8")
        errors = evaluate(root)
        if not any("10/12" in item for item in errors):
            print("FAIL  provenance selftest: dropped site phrase did not fail")
            return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in args:
        if _selftest() != 0:
            return 1
    errors = evaluate(ROOT)
    if errors:
        print("\n".join(f"FAIL  {item}" for item in errors))
        return 1
    count = len(_load_sources(ROOT).get("claims", []))
    print(f"PASS  provenance: {count} claims match evidence/sources.json and site/index.html")
    if "--selftest" in args:
        print("PASS  provenance selftest: a site missing the quoted value fails")
    return 0


if __name__ == "__main__":
    sys.exit(main())
