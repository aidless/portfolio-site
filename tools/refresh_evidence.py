#!/usr/bin/env python3
"""Online refresh: compare pinned evidence quotes with upstream HEADs.

Reports differences. Does not rewrite evidence/sources.json or the site.
Exit 0 when every default-branch file still supports its claim and every
recorded open-PR expectation still matches. Exit 1 on drift or fetch failure.

Offline `make check` does not run this tool.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check_provenance  # noqa: E402


def _token() -> str | None:
    return os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")


def fetch_text(url: str, timeout: float = 30.0) -> str:
    headers = {
        "User-Agent": "portfolio-site-evidence-refresh",
        "Accept": "application/vnd.github+json",
    }
    token = _token()
    if token and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def default_head(repo: str) -> str:
    payload = json.loads(fetch_text(f"https://api.github.com/repos/{repo}/commits/HEAD"))
    sha = payload.get("sha", "")
    if not check_provenance.HEX40.fullmatch(sha):
        raise ValueError(f"{repo}: HEAD sha is not 40 hex: {sha!r}")
    return sha


def file_at(repo: str, sha: str, path: str) -> str:
    url = f"https://raw.githubusercontent.com/{repo}/{sha}/{path}"
    return fetch_text(url)


def main() -> int:
    sources = json.loads((ROOT / "evidence" / "sources.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    heads: dict[str, str] = {}
    files: dict[tuple[str, str, str], str] = {}

    def load(repo: str, sha: str, path: str) -> str:
        key = (repo, sha, path)
        if key not in files:
            files[key] = file_at(repo, sha, path)
        return files[key]

    for claim in sources["claims"]:
        repo = claim["repo"]
        label = claim["id"]
        try:
            if repo not in heads:
                heads[repo] = default_head(repo)
            head = heads[repo]
            text = load(repo, head, claim["path"])
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError, KeyError) as exc:
            errors.append(f"{label}: fetch failed: {exc}")
            continue
        holds = check_provenance.claim_holds(claim, text)
        moved = head != claim["commit"]
        state = "PRESENT" if holds else "ABSENT"
        suffix = " (HEAD moved)" if moved else ""
        print(f"{state}  {label} on {repo}@{head[:12]}{suffix}")
        if not holds:
            errors.append(
                f"{label}: default branch {head} no longer supports the pinned value {claim['value']}"
            )
        open_pr = claim.get("open_pr")
        if not open_pr:
            continue
        try:
            pr_text = load(repo, open_pr["head"], claim["path"])
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            errors.append(f"{label}: open PR fetch failed: {exc}")
            continue
        present = check_provenance.claim_holds(claim, pr_text)
        expected = open_pr["quote_on_head"]
        relation = "present" if present else "absent"
        print(
            f"PR    {label} #{open_pr['number']}@{open_pr['head'][:12]} "
            f"quote {relation}; recorded quote_on_head={expected}"
        )
        if present != expected:
            errors.append(
                f"{label}: open PR #{open_pr['number']} quote presence is {present}, "
                f"sources.json recorded {expected}"
            )
    if errors:
        print("\n".join(f"DIFF  {item}" for item in errors))
        return 1
    print("OK    pinned quotes still match default branch; open-PR notes still match")
    return 0


if __name__ == "__main__":
    sys.exit(main())
