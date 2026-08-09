"""Export validated JSON as a JavaScript global for file:// operation."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
summary = json.loads((ROOT / "thesis" / "data" / "summary.json").read_text(encoding="utf-8"))
results = json.loads((ROOT / "thesis" / "data" / "results.json").read_text(encoding="utf-8"))
payload = "window.THESIS_DATA = " + json.dumps({"summary": summary, "results": results}) + ";\n"
(ROOT / "thesis" / "data" / "thesis-data.js").write_text(payload, encoding="utf-8")
print("Exported thesis/data/thesis-data.js")

