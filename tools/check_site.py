#!/usr/bin/env python3
"""Static contract checks for the zero-dependency portfolio site."""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
INDEX = SITE / "index.html"
CSS = SITE / "style.css"

REQUIRED_IDS = {
    "top",
    "work",
    "agent-runbook",
    "llm-runbook",
    "study-runbook",
    "ledger",
    "boundaries",
}
REQUIRED_TEXT = {
    "AI 应用工程作品集",
    "三条求职证据线",
    "真实用户 0",
    "生产 / SLO 声明",
    "NONE",
    "agent-platform",
    "llm-lab",
    "study-buddy",
    "rag-qa",
    "16/16",
    "391 passed",
    "10/12",
    "0 个真实用户",
}
REQUIRED_LOCAL_FILES = {
    "style.css",
    "assets/agent-platform.webp",
    "assets/llm-lab.webp",
    "assets/study-buddy.webp",
    "evidence/llm-lab-report.html",
    "evidence/llm-lab-result.json",
}
FORBIDDEN_TEXT = {
    "四个公开 Demo",
    "四个可点、可复现",
    "全部 CI 绿 · Pages 可点",
}
FORBIDDEN_PATTERNS = {
    "absolute home path": re.compile(r"(?:/home/|/Users/|[A-Za-z]:\\\\)"),
    "likely API key": re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9]"),
    "GitHub token": re.compile(r"gh[pousr]_[A-Za-z0-9]"),
}


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.project_articles = 0
        self.images: list[dict[str, str | None]] = []
        self.resources: list[tuple[str, str]] = []
        self.tags: list[tuple[str, dict[str, str | None]]] = []
        self.details_count = 0
        self.scripts_count = 0
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        self.tags.append((tag, values))
        if values.get("id"):
            self.ids.add(values["id"] or "")
        classes = set((values.get("class") or "").split())
        if tag == "article" and "project" in classes:
            self.project_articles += 1
        if tag == "img":
            self.images.append(values)
        if tag == "script":
            self.scripts_count += 1
        if tag == "details":
            self.details_count += 1
        if tag == "link" and values.get("href"):
            self.resources.append(("link", values["href"] or ""))
        if tag in {"a", "img", "script", "source"} and values.get(
            "src" if tag != "a" else "href"
        ):
            self.resources.append(
                (tag, values.get("src" if tag != "a" else "href") or "")
            )

    def handle_data(self, data: str) -> None:
        self._text.append(data)

    @property
    def text(self) -> str:
        return re.sub(r"\s+", " ", "".join(self._text))


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def check_local_resource(errors: list[str], source: str, raw: str) -> None:
    if raw.startswith(("#", "data:", "mailto:", "tel:")):
        return
    parts = urlsplit(raw)
    if parts.scheme in {"http", "https"} or parts.netloc:
        return
    if not parts.path:
        return
    target = (SITE / unquote(parts.path)).resolve()
    try:
        target.relative_to(SITE.resolve())
    except ValueError:
        fail(errors, f"{source}: local resource escapes site/: {raw}")
        return
    if not target.is_file():
        fail(errors, f"{source}: missing local resource: {raw}")


def main() -> int:
    errors: list[str] = []
    required_files = {"index.html", *REQUIRED_LOCAL_FILES}
    for required in sorted(required_files):
        if not (SITE / required).is_file():
            fail(errors, f"missing required file: site/{required}")
    if errors:
        print("\n".join(f"FAIL  {item}" for item in errors))
        return 1

    html = INDEX.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")
    parser = SiteParser()
    parser.feed(html)

    missing_ids = sorted(REQUIRED_IDS - parser.ids)
    if missing_ids:
        fail(errors, f"missing element ids: {', '.join(missing_ids)}")
    missing_text = sorted(item for item in REQUIRED_TEXT if item not in parser.text)
    if missing_text:
        fail(errors, f"missing required claims: {', '.join(missing_text)}")
    forbidden = sorted(item for item in FORBIDDEN_TEXT if item in parser.text)
    if forbidden:
        fail(errors, f"stale four-demo copy remains: {', '.join(forbidden)}")
    if parser.project_articles != 3:
        fail(errors, f"expected 3 flagship project cards, found {parser.project_articles}")
    if parser.details_count < 4:
        fail(errors, f"expected at least 4 interview FAQ items, found {parser.details_count}")
    if parser.scripts_count:
        fail(errors, "portfolio must remain JavaScript-free")
    if html.count("data-label=") < 12:
        fail(errors, "mobile evidence ledger must label all non-name cells")

    if len(parser.images) != 3:
        fail(errors, f"expected 3 project previews, found {len(parser.images)}")
    for index, image in enumerate(parser.images, start=1):
        if not image.get("alt"):
            fail(errors, f"image {index} has no alt text")
        if not image.get("width") or not image.get("height"):
            fail(errors, f"image {index} has no intrinsic dimensions")
        if not image.get("src"):
            fail(errors, f"image {index} has no src")

    for tag, attributes in parser.tags:
        if tag == "link":
            rel = (attributes.get("rel") or "").lower()
            href = attributes.get("href") or ""
            if "stylesheet" in rel and href != "style.css":
                fail(errors, f"unexpected stylesheet: {href}")
        if tag == "script":
            fail(errors, "script tag is not allowed")
        if tag == "a" and attributes.get("target") == "_blank":
            rel = attributes.get("rel") or ""
            if "noopener" not in rel and "noreferrer" not in rel:
                fail(errors, f"external link lacks rel protection: {attributes.get('href')}")

    for tag, raw in parser.resources:
        check_local_resource(errors, tag, raw)

    required_css = {
        "@media (max-width: 600px)",
        "@media (prefers-reduced-motion: reduce)",
        "@media print",
        "--serif:",
        "--sans:",
        "--rust:",
        "--teal:",
        "--gold:",
    }
    for token in sorted(required_css):
        if token not in css:
            fail(errors, f"style.css missing contract token: {token}")
    if "@import" in css or re.search(r"url\(\s*['\"]?https?://", css):
        fail(errors, "style.css must not load external assets")

    evidence_path = SITE / "evidence" / "llm-lab-result.json"
    try:
        result = json.loads(evidence_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(errors, f"llm-lab result is invalid JSON: {exc}")
    else:
        if result.get("steps") != 5 or len(result.get("steps_detail", [])) != 5:
            fail(errors, "llm-lab evidence must contain exactly 5 steps")
        if not result.get("all_passed"):
            fail(errors, "llm-lab evidence must have all_passed=true")
        if result.get("total_cost_usd") != 0.0:
            fail(errors, "offline llm-lab demo cost must be zero")
        verdicts = [
            step.get("verdict", {}).get("label")
            for step in result.get("steps_detail", [])
        ]
        if verdicts != ["pass"] * 5:
            fail(errors, "all llm-lab step verdicts must be pass")

    report = (SITE / "evidence" / "llm-lab-report.html").read_text(encoding="utf-8")
    if "<script" in report.lower():
        fail(errors, "llm-lab standalone report must not contain scripts")
    if report.count('class="badge badge-pass"') != 5:
        fail(errors, "llm-lab report must visibly contain 5 PASS badges")

    public_files = {
        "site/index.html": html,
        "site/style.css": css,
        "site/evidence/llm-lab-report.html": report,
    }
    for name, text in public_files.items():
        for label, pattern in FORBIDDEN_PATTERNS.items():
            if pattern.search(text):
                fail(errors, f"{name}: found {label}")

    if errors:
        print("\n".join(f"FAIL  {item}" for item in errors))
        return 1

    print("PASS  site contract: 3 flagship cards, 4 evidence rows, local assets, boundaries")
    print("PASS  zero JavaScript, zero CDN, responsive/print/reduced-motion CSS contracts")
    print("PASS  llm-lab evidence: 5/5 PASS, $0.000000, 5 visible report badges")
    return 0


if __name__ == "__main__":
    sys.exit(main())
