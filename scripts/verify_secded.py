"""Run exhaustive functional verification and write auditable artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from hamming import all_vectors, exhaustive_verification

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    vectors = all_vectors()
    summary = exhaustive_verification()
    json_path = ROOT / "data" / "json" / "hamming_vectors.json"
    csv_path = ROOT / "data" / "csv" / "hamming_vectors.csv"
    report_path = ROOT / "results" / "functional_verification.json"
    json_path.write_text(json.dumps(vectors, indent=2), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["word", "D1..D7", "positions_1..11", "positions_1..12"])
        for row in vectors:
            writer.writerow([
                row["word"],
                "".join(map(str, row["data_d1_to_d7"])),
                "".join(map(str, row["hamming_11_7"])),
                "".join(map(str, row["extended_12_7"])),
            ])
    report = {
        "status": "PASS",
        "method": "Exhaustive enumeration",
        "data_words_tested": summary["data_words"],
        "single_bit_error_cases_tested": summary["single_errors"],
        "double_bit_error_cases_tested": summary["double_errors"],
        "interpretation": (
            "The encoder/decoder model corrected every single-bit error and detected "
            "every double-bit error. This verifies the SEC-DED code model, not a "
            "transistor-level decoder."
        ),
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

