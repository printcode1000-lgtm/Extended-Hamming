"""Run generated LTspice experiments in batch mode and update statuses."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--level", choices=("XOR", "H117", "EH127", "ALL"), default="ALL")
    parser.add_argument("--nominal-only", action="store_true")
    args = parser.parse_args()
    manifest_path = ROOT / "data" / "experiments.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    selected = [e for e in manifest["experiments"] if args.level == "ALL" or e["level"] == args.level]
    if args.nominal_only:
        selected = [e for e in selected if e["experiment_id"].endswith("-NOM")]
    failures = 0
    for index, experiment in enumerate(selected, 1):
        circuit = ROOT / experiment["simulation_file"]
        completed = subprocess.run(
            [str(args.exe), "-b", str(circuit)], cwd=circuit.parent,
            capture_output=True, text=True, timeout=180,
        )
        log = circuit.with_suffix(".log")
        experiment["status"] = "Simulated" if completed.returncode == 0 and log.exists() else "Simulation Failed"
        if experiment["status"] != "Simulated":
            failures += 1
            experiment["runner_stderr"] = completed.stderr[-1000:]
        print(f"[{index}/{len(selected)}] {experiment['experiment_id']}: {experiment['status']}")
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()

