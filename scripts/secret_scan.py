"""Conservative pre-publication scan for credential files and common secret patterns."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "pdf-qa", "__pycache__"}
SKIP_SUFFIXES = {".pdf", ".png", ".jpg", ".jpeg", ".raw", ".db", ".pyc"}
FORBIDDEN_NAMES = {".env", "id_rsa", "id_ed25519", "credentials.json", "service-account.json"}
PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github_token": re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "generic_assignment": re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*['\"][^'\"\s]{12,}['\"]"),
}


def main() -> int:
    findings: list[dict[str, object]] = []
    scanned = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        relative = path.relative_to(ROOT)
        if path.name.lower() in FORBIDDEN_NAMES or path.name.lower().startswith(".env."):
            findings.append({"file": str(relative), "line": None, "type": "credential filename"})
            continue
        if path.suffix.lower() in SKIP_SUFFIXES or path.stat().st_size > 5_000_000:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        scanned += 1
        for line_number, line in enumerate(content.splitlines(), 1):
            for label, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings.append({"file": str(relative), "line": line_number, "type": label})
    report = {"files_scanned": scanned, "findings": findings, "status": "PASS" if not findings else "FAIL"}
    reports = ROOT / "reports"; reports.mkdir(exist_ok=True)
    (reports / "secret-scan-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
