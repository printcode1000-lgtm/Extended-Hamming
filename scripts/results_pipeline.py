"""Parse LTspice .log measurements and validate derived metrics."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path

MEASUREMENT = re.compile(
    r"^\s*(?P<name>[A-Za-z][\w]*)\s*(?::[^\n=]*)?=\s*(?P<value>[-+\d.eE]+)",
    re.MULTILINE,
)


def parse_log(path: Path) -> dict[str, float]:
    text = path.read_text(encoding="utf-8", errors="replace")
    parsed: dict[str, float] = {}
    for match in MEASUREMENT.finditer(text):
        try:
            parsed[match.group("name").lower()] = float(match.group("value"))
        except ValueError:
            continue
    return parsed


def validate(row: dict[str, object]) -> list[str]:
    errors: list[str] = []
    required = ("pavg", "tplh", "tphl", "voh", "vol")
    for key in required:
        value = row.get(key)
        if not isinstance(value, (float, int)) or not math.isfinite(float(value)):
            errors.append(f"missing_or_invalid:{key}")
    if isinstance(row.get("pavg"), (float, int)) and float(row["pavg"]) < 0:
        errors.append("negative_power")
    for key in ("tplh", "tphl"):
        if isinstance(row.get(key), (float, int)) and float(row[key]) <= 0:
            errors.append(f"nonpositive_delay:{key}")
    if all(isinstance(row.get(k), (float, int)) for k in ("voh", "vol", "vdd")):
        vdd = float(row["vdd"])
        if float(row["voh"]) > vdd * 1.05 or float(row["vol"]) < -vdd * 0.05:
            errors.append("output_outside_supply")
    if all(isinstance(row.get(k), (float, int)) for k in ("pavg", "tpd", "pdp")):
        expected = float(row["pavg"]) * float(row["tpd"])
        if not math.isclose(float(row["pdp"]), expected, rel_tol=1e-9, abs_tol=1e-30):
            errors.append("pdp_mismatch")
    return errors


def process(manifest_path: Path, output_csv: Path, output_json: Path) -> list[dict[str, object]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    for experiment in manifest["experiments"]:
        row = dict(experiment)
        exp_id = str(row["experiment_id"])
        if exp_id in seen:
            row["validation_errors"] = ["duplicate_experiment_id"]
            rows.append(row)
            continue
        seen.add(exp_id)
        log_path = manifest_path.parent.parent / str(row["raw_log"])
        if not log_path.exists():
            row.update({"status": "Pending Simulation", "validation_errors": ["missing_log"]})
            rows.append(row)
            continue
        row.update(parse_log(log_path))
        if isinstance(row.get("tplh"), float) and isinstance(row.get("tphl"), float):
            row["tpd"] = (row["tplh"] + row["tphl"]) / 2
        if isinstance(row.get("pavg"), float) and isinstance(row.get("tpd"), float):
            row["pdp"] = row["pavg"] * row["tpd"]
        if isinstance(row.get("voh"), float) and isinstance(row.get("vol"), float):
            row["output_swing"] = row["voh"] - row["vol"]
        if row.get("level") in {"H117", "EH127"} and isinstance(row.get("pavg"), float):
            frequency = float(row["frequency_hz"])
            bits = 11 if row["level"] == "H117" else 12
            row["energy_per_operation"] = row["pavg"] / frequency
            row["energy_per_encoded_bit"] = row["energy_per_operation"] / bits
        functional_reasons: list[str] = []
        if all(isinstance(row.get(k), (float, int)) for k in ("voh", "vol", "vdd")):
            if float(row["voh"]) < 0.8 * float(row["vdd"]):
                functional_reasons.append("VOH_below_0.8VDD")
            if float(row["vol"]) > 0.2 * float(row["vdd"]):
                functional_reasons.append("VOL_above_0.2VDD")
        if all(isinstance(row.get(k), (float, int)) for k in ("tpd", "frequency_hz")):
            if float(row["tpd"]) >= 0.5 / float(row["frequency_hz"]):
                functional_reasons.append("delay_exceeds_half_period")
        row["functional_pass"] = not functional_reasons
        row["functional_failure_reasons"] = functional_reasons
        errors = validate(row)
        row["validation_errors"] = errors
        row["status"] = "Validated" if not errors else "Rejected"
        rows.append(row)
    output_json.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    keys = sorted({key for row in rows for key in row})
    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            serial = {k: json.dumps(v) if isinstance(v, (list, dict)) else v for k, v in row.items()}
            writer.writerow(serial)
    status_by_id = {str(row["experiment_id"]): str(row["status"]) for row in rows}
    for experiment in manifest["experiments"]:
        experiment["status"] = status_by_id[str(experiment["experiment_id"])]
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("data/experiments.json"))
    parser.add_argument("--csv", type=Path, default=Path("data/processed/results.csv"))
    parser.add_argument("--json", type=Path, default=Path("thesis/data/results.json"))
    args = parser.parse_args()
    rows = process(args.manifest, args.csv, args.json)
    print(json.dumps({"experiments": len(rows), "validated": sum(r["status"] == "Validated" for r in rows)}, indent=2))


if __name__ == "__main__":
    main()
