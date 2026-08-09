"""Remove machine-specific absolute prefixes from LTspice text logs before publication."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WINDOWS_ROOT = str(ROOT).replace("/", "\\") + "\\"


def main() -> None:
    changed = 0
    for path in (ROOT / "ltspice").rglob("*.log"):
        text = path.read_text(encoding="utf-8", errors="replace")
        sanitized = text.replace(WINDOWS_ROOT, "")
        # Historical logs may have been produced from the same project under another user.
        sanitized = re.sub(r"(?i)[A-Z]:\\Users\\[^\\\r\n]+\\(?:Desktop\\)?Encoders\\", "", sanitized)
        if sanitized != text:
            path.write_text(sanitized, encoding="utf-8", newline="")
            changed += 1
    print(f"Sanitized {changed} LTspice text logs")


if __name__ == "__main__":
    main()
