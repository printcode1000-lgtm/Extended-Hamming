"""Generate traceable LTspice netlists and the master experiment manifest."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = "../../models/65nm_bulk.pm"

ARCH_CELLS = {
    "CMOS": "XOR_CMOS",
    "GDI": "XOR_GDI",
    "FSGDI": "XOR_FSGDI",
    "HYBRID_A": "XOR_HYBRID_A",
    "HYBRID_B": "XOR_FSGDI",
}
TRANSISTOR_COUNTS = {"CMOS": 12, "GDI": 4, "FSGDI": 6, "HYBRID_A": 10, "HYBRID_B": 6}


def pulse_sources(frequency: float, vdd: float) -> list[str]:
    period = 1.0 / frequency
    # Different binary periods exercise all 128 data words repeatedly.
    result = []
    for i in range(7):
        p = period * (2**i)
        delay = period / 4 if i == 0 else 2 * period
        result.append(f"VD{i+1} D{i+1} 0 PULSE(0 {vdd} {delay:.12g} 20p 20p {p/2:.12g} {p:.12g})")
    return result


def header(title: str, vdd: float, temp: float, frequency: float) -> list[str]:
    return [
        f"* {title}",
        f".include {MODEL}",
        ".include ../circuits.lib",
        f".param VDD={vdd}",
        f".temp {temp}",
        "VSUP VDD 0 {VDD}",
        *pulse_sources(frequency, vdd),
    ]


def xor_netlist(arch: str, vdd: float, temp: float, frequency: float, load: float, sim_time: float) -> str:
    cell = ARCH_CELLS[arch]
    period = 1.0 / frequency
    lines = [
        f"* XOR benchmark: {arch}",
        ".include ../../../models/65nm_bulk.pm",
        ".include ../../circuits.lib",
        f".param VDD={vdd}",
        f".temp {temp}",
        "VSUP VDD 0 {VDD}",
        f"VA A 0 PULSE(0 {vdd} {period/4:.12g} 20p 20p {period/2:.12g} {period:.12g})",
        "VB B 0 0",
        f"XU A B Y VDD 0 {cell}",
        f"CLOAD Y 0 {load}f",
        f".tran 2p {sim_time:.12g} 0 2p",
        f".meas tran pavg AVG (-V(VDD)*I(VSUP)) FROM={sim_time/4:.12g} TO={sim_time:.12g}",
        f".meas tran tplh TRIG V(A) VAL={vdd/2:.12g} RISE=3 TARG V(Y) VAL={vdd/2:.12g} RISE=3",
        f".meas tran tphl TRIG V(A) VAL={vdd/2:.12g} FALL=3 TARG V(Y) VAL={vdd/2:.12g} FALL=3",
        f".meas tran trise TRIG V(Y) VAL={0.1*vdd:.12g} RISE=3 TARG V(Y) VAL={0.9*vdd:.12g} RISE=3",
        f".meas tran tfall TRIG V(Y) VAL={0.9*vdd:.12g} FALL=3 TARG V(Y) VAL={0.1*vdd:.12g} FALL=3",
        f".meas tran voh MAX V(Y) FROM={sim_time/4:.12g} TO={sim_time:.12g}",
        f".meas tran vol MIN V(Y) FROM={sim_time/4:.12g} TO={sim_time:.12g}",
        ".end",
    ]
    return "\n".join(lines) + "\n"


def xor_chain(inputs: list[str], prefix: str, cell: str, lines: list[str]) -> str:
    node = inputs[0]
    for index, other in enumerate(inputs[1:], 1):
        out = f"{prefix}_{index}"
        lines.append(f"X{prefix}{index} {node} {other} {out} VDD 0 {cell}")
        node = out
    return node


def encoder_netlist(kind: str, arch: str, vdd: float, temp: float, frequency: float, load: float) -> tuple[str, int]:
    cell = ARCH_CELLS[arch]
    period = 1.0 / frequency
    sim_time = period * 16
    lines = [
        f"* {kind} encoder benchmark: {arch}",
        ".include ../../models/65nm_bulk.pm",
        ".include ../circuits.lib",
        f".param VDD={vdd}",
        f".temp {temp}",
        "VSUP VDD 0 {VDD}",
        *pulse_sources(frequency, vdd),
    ]
    raw = {}
    raw["P1"] = xor_chain(["D1", "D2", "D4", "D5", "D7"], "P1N", cell, lines)
    raw["P2"] = xor_chain(["D1", "D3", "D4", "D6", "D7"], "P2N", cell, lines)
    raw["P4"] = xor_chain(["D2", "D3", "D4"], "P4N", cell, lines)
    raw["P8"] = xor_chain(["D5", "D6", "D7"], "P8N", cell, lines)
    final = dict(raw)
    xor_count = 12
    if kind == "EH127":
        final["P0"] = xor_chain(
            ["D1", "D2", "D3", "D4", "D5", "D6", "D7", raw["P1"], raw["P2"], raw["P4"], raw["P8"]],
            "P0N", cell, lines
        )
        xor_count += 10
    if arch == "HYBRID_B":
        for name, node in list(final.items()):
            lines.append(f"XBUF{name} {node} {name} VDD 0 RESTORE_BUFFER")
            final[name] = name
    delay_node = final["P0"] if kind == "EH127" else final["P1"]
    outputs = list(final.items())
    for name, node in outputs:
        lines.append(f"CLOAD_{name} {node} 0 {load}f")
    lines.extend([
        f".tran 20p {sim_time:.12g} 0 20p",
        f".meas tran pavg AVG (-V(VDD)*I(VSUP)) FROM={period*4:.12g} TO={sim_time:.12g}",
        f".meas tran tplh TRIG V(D1) VAL={vdd/2:.12g} RISE=1 TARG V({delay_node}) VAL={vdd/2:.12g} RISE=1",
        f".meas tran tphl TRIG V(D1) VAL={vdd/2:.12g} FALL=1 TARG V({delay_node}) VAL={vdd/2:.12g} FALL=1",
        f".meas tran voh MAX V({delay_node}) FROM={period*4:.12g} TO={sim_time:.12g}",
        f".meas tran vol MIN V({delay_node}) FROM={period*4:.12g} TO={sim_time:.12g}",
        ".end",
    ])
    buffer_transistors = (len(final) * 4) if arch == "HYBRID_B" else 0
    count = xor_count * TRANSISTOR_COUNTS[arch] + buffer_transistors
    return "\n".join(lines) + "\n", count


def cases() -> list[tuple[str, float, float, float, float]]:
    nominal = ("NOM", 1.2, 27.0, 125e6, 10.0)
    result = [nominal]
    result += [(f"VDD{int(v*10):02d}", v, 27.0, 125e6, 10.0) for v in (0.6, 0.8, 1.0)]
    result += [(f"T{str(int(t)).replace('-', 'M')}", 1.2, t, 125e6, 10.0) for t in (-20.0, 85.0)]
    result += [(f"L{int(l):02d}", 1.2, 27.0, 125e6, l) for l in (1.0, 5.0, 20.0)]
    result += [(f"F{int(f/1e6):03d}", 1.2, 27.0, f, 10.0) for f in (25e6, 200e6)]
    return result


def main() -> None:
    experiments = []
    for arch in ("CMOS", "GDI", "FSGDI", "HYBRID_A"):
        folder = ROOT / "ltspice" / "xor" / arch.lower().replace("_", "-")
        folder.mkdir(parents=True, exist_ok=True)
        for label, vdd, temp, freq, load in cases():
            exp_id = f"EXP-XOR-{arch}-{label}"
            cir = folder / f"{exp_id}.cir"
            sim_time = 12 / freq
            cir.write_text(xor_netlist(arch, vdd, temp, freq, load, sim_time), encoding="ascii")
            experiments.append({
                "experiment_id": exp_id, "level": "XOR", "architecture": arch,
                "model": "PTM-65nm-beta-2006", "vdd": vdd, "temperature_c": temp,
                "frequency_hz": freq, "load_ff": load, "input_pattern": "two-input exhaustive periodic",
                "simulation_file": str(cir.relative_to(ROOT)).replace("\\", "/"),
                "raw_log": str(cir.with_suffix(".log").relative_to(ROOT)).replace("\\", "/"),
                "status": "Pending Simulation", "transistor_count": TRANSISTOR_COUNTS[arch],
            })
    for kind, archs in (("H117", ("CMOS", "GDI", "FSGDI")), ("EH127", ("CMOS", "FSGDI", "HYBRID_A", "HYBRID_B"))):
        folder = ROOT / "ltspice" / ("hamming-11-7" if kind == "H117" else "extended-hamming-12-7")
        for label, vdd, temp, freq, load in cases():
            for arch in archs:
                exp_id = f"EXP-{kind}-{arch}-{label}"
                cir = folder / f"{exp_id}.cir"
                text, count = encoder_netlist(kind, arch, vdd, temp, freq, load)
                cir.write_text(text, encoding="ascii")
                experiments.append({
                    "experiment_id": exp_id, "level": kind, "architecture": arch,
                    "model": "PTM-65nm-beta-2006", "vdd": vdd, "temperature_c": temp,
                    "frequency_hz": freq, "load_ff": load, "input_pattern": "common 16-cycle binary-count activity sample; exhaustive correctness is verified in Python",
                    "simulation_file": str(cir.relative_to(ROOT)).replace("\\", "/"),
                    "raw_log": str(cir.with_suffix(".log").relative_to(ROOT)).replace("\\", "/"),
                    "status": "Pending Simulation", "transistor_count": count,
                })
    manifest = {"schema_version": 1, "experiments": experiments}
    (ROOT / "data" / "experiments.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Generated {len(experiments)} LTspice experiments")


if __name__ == "__main__":
    main()
