"""Validate local website links, anchors, case, downloads, and selected external URLs."""
from __future__ import annotations

import html
import json
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
IGNORED_DIRS = {".git", "reports", "pdf-qa", "__pycache__"}


class Collector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(str(values["id"]))
        for attr in ("href", "src"):
            if values.get(attr):
                self.links.append((attr, str(values[attr])))


def exact_case(path: Path) -> bool:
    try:
        rel = path.resolve().relative_to(ROOT.resolve())
    except ValueError:
        return False
    cursor = ROOT
    for part in rel.parts:
        try:
            names = {entry.name for entry in cursor.iterdir()}
        except OSError:
            return False
        if part not in names:
            return False
        cursor /= part
    return True


def parse_page(path: Path) -> Collector:
    parser = Collector()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def check_external(url: str) -> dict[str, object]:
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Extended-Hamming-link-check/0.2"})
    try:
        with urllib.request.urlopen(request, timeout=15, context=ssl.create_default_context()) as response:
            return {"url": url, "status": response.status, "ok": 200 <= response.status < 400}
    except urllib.error.HTTPError as error:
        if error.code in {403, 405, 429}:
            try:
                request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(request, timeout=15) as response:
                    return {"url": url, "status": response.status, "ok": 200 <= response.status < 400}
            except Exception as fallback:
                return {"url": url, "status": error.code, "ok": error.code in {403, 429}, "note": str(fallback)}
        return {"url": url, "status": error.code, "ok": False}
    except Exception as error:
        return {"url": url, "status": None, "ok": False, "note": str(error)}


def main() -> int:
    pages = [p for p in ROOT.rglob("*.html") if not any(part in IGNORED_DIRS for part in p.parts)]
    parsed = {page: parse_page(page) for page in pages}
    internal: list[dict[str, object]] = []
    external_urls: set[str] = set()
    for page, collector in parsed.items():
        for attr, raw in collector.links:
            value = raw.strip()
            if not value or value.startswith(("mailto:", "tel:", "javascript:", "data:")):
                continue
            split = urllib.parse.urlsplit(value)
            if split.scheme in {"http", "https"}:
                external_urls.add(value)
                continue
            local_part = urllib.parse.unquote(split.path)
            if local_part.startswith("/"):
                if local_part.startswith("/Extended-Hamming/"):
                    local_part = local_part[len("/Extended-Hamming/"):]
                    target = ROOT / local_part
                else:
                    internal.append({"page": str(page.relative_to(ROOT)), "link": value, "ok": False, "reason": "root-absolute path"})
                    continue
            else:
                target = (page.parent / local_part) if local_part else page
            if target.is_dir():
                target /= "index.html"
            exists = target.exists()
            case_ok = exists and exact_case(target)
            anchor_ok = True
            if exists and split.fragment:
                if target.suffix.lower() == ".html":
                    anchor_ok = split.fragment in parse_page(target).ids
                else:
                    anchor_ok = False
            reasons = []
            if not exists: reasons.append("missing file")
            if exists and not case_ok: reasons.append("incorrect case")
            if exists and not anchor_ok: reasons.append("missing anchor")
            internal.append({"page": str(page.relative_to(ROOT)), "attribute": attr, "link": value, "target": str(target.resolve()), "ok": exists and case_ok and anchor_ok, "reason": ", ".join(reasons)})
    # Also verify URLs documented outside HTML (README, research notes, survey and BibTeX).
    for source in [ROOT / "README.md", *ROOT.glob("docs/*.md"), *ROOT.glob("literature/**/*.md"), *ROOT.glob("references/*.bib")]:
        if not source.exists():
            continue
        content = source.read_text(encoding="utf-8", errors="replace")
        for match in re.findall(r"https?://[^\s<>\)\]\}\"'`]+", content):
            cleaned = match.rstrip(".,;")
            if urllib.parse.urlsplit(cleaned).hostname in {"127.0.0.1", "localhost", "::1"}:
                continue
            external_urls.add(cleaned)
    external = [check_external(url) for url in sorted(external_urls)]
    report = {
        "base_path_tested": "/Extended-Hamming/",
        "pages_checked": len(pages),
        "internal_links_checked": len(internal),
        "internal_failures": sum(not item["ok"] for item in internal),
        "external_links_checked": len(external),
        "external_failures": sum(not item["ok"] for item in external),
        "internal": internal,
        "external": external,
    }
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "link-check-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    rows = "".join(f"<tr><td>{html.escape(str(item['page']))}</td><td>{html.escape(str(item['link']))}</td><td>{'PASS' if item['ok'] else 'FAIL'}</td><td>{html.escape(str(item.get('reason','')))}</td></tr>" for item in internal)
    document = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Link Check Report</title><style>body{{font:14px Arial;margin:2rem}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #ccc;padding:6px;text-align:left}}th{{background:#eee}}</style></head><body><h1>Website Link Check Report</h1><p>Base path: /Extended-Hamming/ · Pages: {len(pages)} · Internal failures: {report['internal_failures']} · External failures: {report['external_failures']}</p><table><thead><tr><th>Page</th><th>Link</th><th>Status</th><th>Reason</th></tr></thead><tbody>{rows}</tbody></table></body></html>"""
    (REPORTS / "link-check-report.html").write_text(document, encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("pages_checked", "internal_links_checked", "internal_failures", "external_links_checked", "external_failures")}, indent=2))
    return 1 if report["internal_failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
