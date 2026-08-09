"""Create comparison tables and figures only from validated LTspice data."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def improvement(baseline: float, candidate: float) -> float:
    return (baseline - candidate) / baseline * 100.0


def main() -> None:
    rows = json.loads((ROOT / "thesis" / "data" / "results.json").read_text(encoding="utf-8"))
    valid = [r for r in rows if r.get("status") == "Validated"]
    nominal = [r for r in valid if r["experiment_id"].endswith("-NOM")]
    summary = {
        "source": "Validated LTspice 26.0.2 .meas results",
        "validated_experiments": len(valid),
        "rejected_experiments": len(rows) - len(valid),
        "nominal": nominal,
        "minimum_functional_vdd": {},
        "nominal_improvements_vs_cmos": [],
    }
    for level in ("XOR", "H117", "EH127"):
        architectures = sorted({r["architecture"] for r in valid if r["level"] == level})
        for arch in architectures:
            candidates = [
                r for r in valid
                if r["level"] == level and r["architecture"] == arch
                and r["temperature_c"] == 27.0 and r["frequency_hz"] == 125e6
                and r["load_ff"] == 10.0 and r.get("functional_pass")
            ]
            if candidates:
                summary["minimum_functional_vdd"][f"{level}:{arch}"] = min(r["vdd"] for r in candidates)
    for level in ("XOR", "H117", "EH127"):
        group = {r["architecture"]: r for r in nominal if r["level"] == level}
        if "CMOS" not in group:
            continue
        baseline = group["CMOS"]
        for arch, row in group.items():
            if arch == "CMOS":
                continue
            summary["nominal_improvements_vs_cmos"].append({
                "level": level,
                "architecture": arch,
                "power_improvement_pct": improvement(baseline["pavg"], row["pavg"]),
                "delay_improvement_pct": improvement(baseline["tpd"], row["tpd"]),
                "pdp_improvement_pct": improvement(baseline["pdp"], row["pdp"]),
                "transistor_reduction_pct": improvement(float(baseline["transistor_count"]), float(row["transistor_count"])),
                "functional_pass": row.get("functional_pass"),
            })
    (ROOT / "thesis" / "data" / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    csv_path = ROOT / "data" / "processed" / "nominal_comparison.csv"
    keys = ["experiment_id", "level", "architecture", "pavg", "tplh", "tphl", "tpd", "pdp", "voh", "vol", "output_swing", "transistor_count", "energy_per_operation", "energy_per_encoded_bit", "functional_pass"]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, extrasaction="ignore")
        writer.writeheader(); writer.writerows(nominal)
    print(json.dumps({k: summary[k] for k in ("validated_experiments", "rejected_experiments", "minimum_functional_vdd")}, indent=2))


if __name__ == "__main__":
    main()
