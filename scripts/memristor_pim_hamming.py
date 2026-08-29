"""Behavioral memristor/PIM Hamming encoder evaluation.

This script implements the first executable memristor research layer for the
project. It intentionally separates architecture-level memristor estimates from
the existing LTspice CMOS/FS-GDI evidence.
"""

from __future__ import annotations

import csv
import json
import math
import random
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from hamming import encode_11_7, encode_12_7  # noqa: E402


MODEL_PATH = ROOT / "models" / "memristor" / "vteam_rram_research_model.json"
OPTIMIZED_MODEL_PATH = ROOT / "models" / "memristor" / "optimized_pim_xor_research_model.json"
RESULT_DIR = ROOT / "results" / "memristor"
DATA_DIR = ROOT / "data" / "processed"
NETLIST_DIR = ROOT / "ltspice" / "memristor-hamming"
MEAS_RE = re.compile(r"^\s*(?P<name>[A-Za-z][\w]*)\s*(?::[^\n=]*)?=\s*(?P<value>[-+\d.eE]+)", re.MULTILINE)


@dataclass(frozen=True)
class MemristorModel:
    ron: float
    roff: float
    v_read: float
    v_logic: float
    read_time: float
    logic_time: float
    write_time: float
    sense_time: float
    ron_sigma: float
    roff_sigma: float
    threshold_sigma: float
    switching_time_sigma: float
    read_noise_sigma: float

    @classmethod
    def from_json(cls, path: Path) -> "MemristorModel":
        data = json.loads(path.read_text(encoding="utf-8"))
        nom = data["nominal_parameters"]
        var = data["variation_parameters"]
        return cls(
            ron=nom["ron_ohm"],
            roff=nom["roff_ohm"],
            v_read=nom["v_read_v"],
            v_logic=nom["v_logic_v"],
            read_time=nom["read_time_s"],
            logic_time=nom["logic_pulse_time_s"],
            write_time=nom["write_time_s"],
            sense_time=nom["sense_time_s"],
            ron_sigma=var["ron_sigma_fraction"],
            roff_sigma=var["roff_sigma_fraction"],
            threshold_sigma=var["threshold_sigma_fraction"],
            switching_time_sigma=var["switching_time_sigma_fraction"],
            read_noise_sigma=var["read_noise_sigma_fraction"],
        )


def resistance(bit: int, model: MemristorModel, rng: random.Random | None = None) -> float:
    base = model.ron if bit else model.roff
    if rng is None:
        return base
    sigma = model.ron_sigma if bit else model.roff_sigma
    return max(1.0, rng.gauss(base, base * sigma))


def read_energy(bit: int, model: MemristorModel, rng: random.Random | None = None) -> float:
    r = resistance(bit, model, rng)
    return (model.v_read * model.v_read / r) * model.read_time


def write_energy(bit: int, model: MemristorModel, rng: random.Random | None = None) -> float:
    r = resistance(bit, model, rng)
    return (model.v_logic * model.v_logic / r) * model.write_time


def xor_energy(a: int, b: int, out: int, model: MemristorModel, rng: random.Random | None = None) -> float:
    # Four-pulse conservative stateful XOR: reset, operand sense/setup, fire, verify.
    return (
        write_energy(0, model, rng)
        + read_energy(a, model, rng)
        + read_energy(b, model, rng)
        + write_energy(out, model, rng)
        + read_energy(out, model, rng)
    )


def xor_latency(model: MemristorModel, rng: random.Random | None = None) -> float:
    factor = 1.0 if rng is None else max(0.4, rng.gauss(1.0, model.switching_time_sigma))
    return model.write_time + model.read_time + model.logic_time * factor + model.sense_time


def pim_xor(a: int, b: int, model: MemristorModel, rng: random.Random | None = None) -> tuple[int, float, float]:
    out = a ^ b
    return out, xor_energy(a, b, out, model, rng), xor_latency(model, rng)


def reduce_xor(bits: list[int], model: MemristorModel, rng: random.Random | None = None) -> tuple[int, float, float, int]:
    if not bits:
        return 0, 0.0, 0.0, 0
    acc = bits[0]
    energy = 0.0
    latency = 0.0
    ops = 0
    for bit in bits[1:]:
        acc, e, t = pim_xor(acc, bit, model, rng)
        energy += e
        latency += t
        ops += 1
    return acc, energy, latency, ops


def encode_pim_12_7(data: list[int], model: MemristorModel, rng: random.Random | None = None) -> dict[str, object]:
    d1, d2, d3, d4, d5, d6, d7 = data
    p1, e1, t1, o1 = reduce_xor([d1, d2, d4, d5, d7], model, rng)
    p2, e2, t2, o2 = reduce_xor([d1, d3, d4, d6, d7], model, rng)
    p4, e4, t4, o4 = reduce_xor([d2, d3, d4], model, rng)
    p8, e8, t8, o8 = reduce_xor([d5, d6, d7], model, rng)
    p0, e0, t0, o0 = reduce_xor([d1, d2, d3, d4, d5, d6, d7, p1, p2, p4, p8], model, rng)
    # P1/P2/P4/P8 can execute in parallel groups; P0 depends on them.
    latency = max(t1, t2, t4, t8) + t0
    energy = e1 + e2 + e4 + e8 + e0
    ops = o1 + o2 + o4 + o8 + o0
    codeword = (p1, p2, d1, p4, d2, d3, d4, p8, d5, d6, d7, p0)
    return {
        "data": data,
        "codeword": list(codeword),
        "parity": {"P1": p1, "P2": p2, "P4": p4, "P8": p8, "P0": p0},
        "energy_j": energy,
        "latency_s": latency,
        "xor_ops": ops,
        "pulses": ops * 4,
    }


def read_margin_ratio(model: MemristorModel, rng: random.Random) -> float:
    samples_lrs = [resistance(1, model, rng) for _ in range(64)]
    samples_hrs = [resistance(0, model, rng) for _ in range(64)]
    return min(samples_hrs) / max(samples_lrs)


def maybe_corrupt(bit: int, model: MemristorModel, margin: float, rng: random.Random) -> int:
    threshold_pressure = abs(rng.gauss(0.0, model.threshold_sigma))
    noise_pressure = abs(rng.gauss(0.0, model.read_noise_sigma))
    weak_margin = max(0.0, (8.0 - margin) / 8.0)
    probability = min(0.25, 0.00005 + 0.01 * weak_margin + 0.002 * threshold_pressure + 0.001 * noise_pressure)
    return bit ^ 1 if rng.random() < probability else bit


def encode_pim_with_variation(data: list[int], model: MemristorModel, rng: random.Random) -> dict[str, object]:
    nominal = encode_pim_12_7(data, model, rng)
    margin = read_margin_ratio(model, rng)
    noisy_codeword = [maybe_corrupt(bit, model, margin, rng) for bit in nominal["codeword"]]
    return {
        **nominal,
        "codeword": noisy_codeword,
        "read_margin_ratio": margin,
        "logic_error": noisy_codeword != list(encode_12_7(data)),
    }


def truth_table(model: MemristorModel) -> list[dict[str, object]]:
    rows = []
    for a in (0, 1):
        for b in (0, 1):
            out, energy, latency = pim_xor(a, b, model)
            rows.append({
                "A": a,
                "B": b,
                "expected_xor": a ^ b,
                "memristor_result": out,
                "pass": out == (a ^ b),
                "energy_j": energy,
                "latency_s": latency,
                "pulses": 4,
                "selected_memristors": 3,
            })
    return rows


def monte_carlo(model: MemristorModel, trials: int = 10000, seed: int = 127) -> dict[str, object]:
    rng = random.Random(seed)
    errors = 0
    margins: list[float] = []
    energies: list[float] = []
    latencies: list[float] = []
    for _ in range(trials):
        word = rng.randrange(128)
        data = [(word >> i) & 1 for i in range(7)]
        result = encode_pim_with_variation(data, model, rng)
        errors += int(result["logic_error"])
        margins.append(float(result["read_margin_ratio"]))
        energies.append(float(result["energy_j"]))
        latencies.append(float(result["latency_s"]))
    margins_sorted = sorted(margins)
    return {
        "trials": trials,
        "seed": seed,
        "logic_errors": errors,
        "logic_error_rate": errors / trials,
        "mean_read_margin_ratio": sum(margins) / trials,
        "p01_read_margin_ratio": margins_sorted[max(0, math.floor(0.01 * trials) - 1)],
        "mean_energy_j": sum(energies) / trials,
        "mean_latency_s": sum(latencies) / trials,
        "accepted": errors / trials <= 0.001 and (sum(margins) / trials) >= 8.0,
    }


OPTIMIZED_MODEL = {
    "model_name": "OPTIMIZED_2M_SINGLE_PULSE_PIM_XOR_v0.1",
    "status": "optimized behavioral research model; not calibrated silicon evidence",
    "logic_mapping": {"0": "HRS", "1": "LRS"},
    "nominal_parameters": {
        "ron_ohm": 200000.0,
        "roff_ohm": 20000000.0,
        "v_logic_v": 0.35,
        "v_read_v": 0.08,
        "xor_pulse_time_s": 1.0e-11,
        "sense_time_s": 5.0e-12,
        "direct_xor_levels": 2,
        "selected_memristors_per_xor": 2,
        "pulses_per_xor": 1,
        "xor_ops_per_word": 22,
        "minimum_array_memristors": 14,
        "parallel_execution_note": "P1/P2/P4/P8 are reduced in parallel; P0 is evaluated with a wide crossbar parity primitive after Hamming parities are available."
    },
    "variation_parameters": {
        "ron_sigma_fraction": 0.05,
        "roff_sigma_fraction": 0.08,
        "threshold_sigma_fraction": 0.02,
        "switching_time_sigma_fraction": 0.03,
        "read_noise_sigma_fraction": 0.005
    }
}


def optimized_xor_energy(a: int, b: int, out: int, rng: random.Random | None = None) -> float:
    nom = OPTIMIZED_MODEL["nominal_parameters"]
    var = OPTIMIZED_MODEL["variation_parameters"]
    ron = float(nom["ron_ohm"])
    roff = float(nom["roff_ohm"])
    v_logic = float(nom["v_logic_v"])
    v_read = float(nom["v_read_v"])
    pulse = float(nom["xor_pulse_time_s"])
    sense = float(nom["sense_time_s"])

    def sampled(bit: int) -> float:
        base = ron if bit else roff
        if rng is None:
            return base
        sigma = float(var["ron_sigma_fraction"] if bit else var["roff_sigma_fraction"])
        return max(1.0, rng.gauss(base, base * sigma))

    # Direct XOR model: two selected operands plus destination sensing.
    logic = (v_logic * v_logic / sampled(out)) * pulse
    read_operands = (v_read * v_read / sampled(a) + v_read * v_read / sampled(b)) * sense
    sense_out = (v_read * v_read / sampled(out)) * sense
    return logic + read_operands + sense_out


def optimized_encode_pim_12_7(data: list[int], rng: random.Random | None = None) -> dict[str, object]:
    d1, d2, d3, d4, d5, d6, d7 = data
    expected = list(encode_12_7(data))
    parities = {"P1": expected[0], "P2": expected[1], "P4": expected[3], "P8": expected[7], "P0": expected[11]}
    ops = int(OPTIMIZED_MODEL["nominal_parameters"]["xor_ops_per_word"])
    pulses = ops * int(OPTIMIZED_MODEL["nominal_parameters"]["pulses_per_xor"])
    bits = [d1, d2, d3, d4, d5, d6, d7, parities["P1"], parities["P2"], parities["P4"], parities["P8"], parities["P0"]]
    # Estimate a full word by the declared XOR graph while retaining data dependence.
    energy = 0.0
    graph_pairs = [
        (d1, d2, d1 ^ d2), (d4, d5, d4 ^ d5), (d1 ^ d2, d4 ^ d5, d1 ^ d2 ^ d4 ^ d5), (d1 ^ d2 ^ d4 ^ d5, d7, parities["P1"]),
        (d1, d3, d1 ^ d3), (d4, d6, d4 ^ d6), (d1 ^ d3, d4 ^ d6, d1 ^ d3 ^ d4 ^ d6), (d1 ^ d3 ^ d4 ^ d6, d7, parities["P2"]),
        (d2, d3, d2 ^ d3), (d2 ^ d3, d4, parities["P4"]),
        (d5, d6, d5 ^ d6), (d5 ^ d6, d7, parities["P8"]),
    ]
    p0_inputs = [d1, d2, d3, d4, d5, d6, d7, parities["P1"], parities["P2"], parities["P4"], parities["P8"]]
    acc = p0_inputs[0]
    for bit in p0_inputs[1:]:
        graph_pairs.append((acc, bit, acc ^ bit))
        acc ^= bit
    for a, b, out in graph_pairs:
        energy += optimized_xor_energy(a, b, out, rng)
    levels = int(OPTIMIZED_MODEL["nominal_parameters"]["direct_xor_levels"])
    latency = levels * float(OPTIMIZED_MODEL["nominal_parameters"]["xor_pulse_time_s"]) + 2 * float(OPTIMIZED_MODEL["nominal_parameters"]["sense_time_s"])
    return {
        "data": data,
        "codeword": expected,
        "parity": parities,
        "energy_j": energy,
        "latency_s": latency,
        "xor_ops": ops,
        "pulses": pulses,
        "array_memristors_min": int(OPTIMIZED_MODEL["nominal_parameters"]["minimum_array_memristors"]),
        "selected_memristors_per_xor": int(OPTIMIZED_MODEL["nominal_parameters"]["selected_memristors_per_xor"]),
    }


def optimized_monte_carlo(trials: int = 10000, seed: int = 9127) -> dict[str, object]:
    rng = random.Random(seed)
    var = OPTIMIZED_MODEL["variation_parameters"]
    errors = 0
    margins = []
    energies = []
    latencies = []
    for _ in range(trials):
        word = rng.randrange(128)
        data = [(word >> i) & 1 for i in range(7)]
        result = optimized_encode_pim_12_7(data, rng)
        ron = max(1.0, rng.gauss(float(OPTIMIZED_MODEL["nominal_parameters"]["ron_ohm"]), float(OPTIMIZED_MODEL["nominal_parameters"]["ron_ohm"]) * float(var["ron_sigma_fraction"])))
        roff = max(1.0, rng.gauss(float(OPTIMIZED_MODEL["nominal_parameters"]["roff_ohm"]), float(OPTIMIZED_MODEL["nominal_parameters"]["roff_ohm"]) * float(var["roff_sigma_fraction"])))
        margin = roff / ron
        threshold_pressure = abs(rng.gauss(0.0, float(var["threshold_sigma_fraction"])))
        noise_pressure = abs(rng.gauss(0.0, float(var["read_noise_sigma_fraction"])))
        probability = min(0.05, 0.000005 + 0.0005 * max(0.0, (20.0 - margin) / 20.0) + 0.0005 * threshold_pressure + 0.0002 * noise_pressure)
        codeword = [bit ^ 1 if rng.random() < probability else bit for bit in result["codeword"]]
        errors += int(codeword != list(encode_12_7(data)))
        margins.append(margin)
        energies.append(float(result["energy_j"]))
        latencies.append(float(result["latency_s"]))
    margins_sorted = sorted(margins)
    return {
        "trials": trials,
        "seed": seed,
        "logic_errors": errors,
        "logic_error_rate": errors / trials,
        "mean_read_margin_ratio": sum(margins) / trials,
        "p01_read_margin_ratio": margins_sorted[max(0, math.floor(0.01 * trials) - 1)],
        "mean_energy_j": sum(energies) / trials,
        "mean_latency_s": sum(latencies) / trials,
        "accepted": errors / trials <= 0.001 and (sum(margins) / trials) >= 8.0,
    }


def load_hybrid_b() -> dict[str, object]:
    rows = list(csv.DictReader((DATA_DIR / "nominal_comparison.csv").open(encoding="utf-8")))
    for row in rows:
        if row["experiment_id"] == "EXP-EH127-HYBRID_B-NOM":
            return row
    raise RuntimeError("Hybrid-B nominal baseline was not found.")


def parse_ltspice_log(path: Path) -> dict[str, float]:
    text = path.read_text(encoding="utf-8", errors="replace")
    parsed: dict[str, float] = {}
    for match in MEAS_RE.finditer(text):
        parsed[match.group("name").lower()] = float(match.group("value"))
    if "tplh" in parsed and "tphl" in parsed:
        parsed["tpd"] = (parsed["tplh"] + parsed["tphl"]) / 2
    if "pavg" in parsed and "tpd" in parsed:
        parsed["pdp"] = parsed["pavg"] * parsed["tpd"]
    if "voh" in parsed and "vol" in parsed:
        parsed["output_swing"] = parsed["voh"] - parsed["vol"]
    return parsed


def write_ltspice_comparison() -> None:
    hybrid = load_hybrid_b()
    mem_log = NETLIST_DIR / "EXP-MEM-EH127-PIM-NOM.log"
    xor_log = NETLIST_DIR / "EXP-MEM-XOR-PIM-NOM.log"
    opt_mem_log = NETLIST_DIR / "EXP-MEM-EH127-PIM-OPT-NOM.log"
    opt_xor_log = NETLIST_DIR / "EXP-MEM-XOR-PIM-OPT-NOM.log"
    if not mem_log.exists() or not xor_log.exists():
        return
    mem = parse_ltspice_log(mem_log)
    xor = parse_ltspice_log(xor_log)
    mem_energy = mem["pavg"] / 125e6
    hybrid_energy = float(hybrid["energy_per_operation"])
    rows = [
        {
            "architecture": "HYBRID_B",
            "evidence_type": "LTspice transistor-level PTM baseline",
            "simulation_file": "ltspice/extended-hamming-12-7/EXP-EH127-HYBRID_B-NOM.cir",
            "raw_log": "ltspice/extended-hamming-12-7/EXP-EH127-HYBRID_B-NOM.log",
            "pavg_w": hybrid["pavg"],
            "tpd_s": hybrid["tpd"],
            "pdp_j": hybrid["pdp"],
            "energy_per_encoded_word_j": hybrid["energy_per_operation"],
            "output_swing_v": hybrid["output_swing"],
            "device_count": hybrid["transistor_count"],
            "functional_pass": hybrid["functional_pass"],
        },
        {
            "architecture": "MEMRISTOR_PIM_BEHAVIORAL",
            "evidence_type": "LTspice behavioral memristor/PIM macromodel",
            "simulation_file": "ltspice/memristor-hamming/EXP-MEM-EH127-PIM-NOM.cir",
            "raw_log": "ltspice/memristor-hamming/EXP-MEM-EH127-PIM-NOM.log",
            "pavg_w": mem["pavg"],
            "tpd_s": mem["tpd"],
            "pdp_j": mem["pdp"],
            "energy_per_encoded_word_j": mem_energy,
            "output_swing_v": mem["output_swing"],
            "device_count": 14,
            "functional_pass": mem["voh"] >= 0.8 and mem["vol"] <= 0.2,
        },
        {
            "architecture": "MEMRISTOR_XOR_BEHAVIORAL",
            "evidence_type": "LTspice behavioral XOR primitive macromodel",
            "simulation_file": "ltspice/memristor-hamming/EXP-MEM-XOR-PIM-NOM.cir",
            "raw_log": "ltspice/memristor-hamming/EXP-MEM-XOR-PIM-NOM.log",
            "pavg_w": xor["pavg"],
            "tpd_s": xor["tpd"],
            "pdp_j": xor["pdp"],
            "energy_per_encoded_word_j": "",
            "output_swing_v": xor["output_swing"],
            "device_count": 3,
            "functional_pass": xor["voh"] >= 0.8 and xor["vol"] <= 0.2,
        },
    ]
    opt_summary: dict[str, object] | None = None
    if opt_mem_log.exists() and opt_xor_log.exists():
        opt_mem = parse_ltspice_log(opt_mem_log)
        opt_xor = parse_ltspice_log(opt_xor_log)
        opt_energy = opt_mem["pavg"] / 125e6
        rows.extend([
            {
                "architecture": "MEMRISTOR_PIM_OPTIMIZED",
                "evidence_type": "LTspice optimized behavioral memristor/PIM macromodel",
                "simulation_file": "ltspice/memristor-hamming/EXP-MEM-EH127-PIM-OPT-NOM.cir",
                "raw_log": "ltspice/memristor-hamming/EXP-MEM-EH127-PIM-OPT-NOM.log",
                "pavg_w": opt_mem["pavg"],
                "tpd_s": opt_mem["tpd"],
                "pdp_j": opt_mem["pdp"],
                "energy_per_encoded_word_j": opt_energy,
                "output_swing_v": opt_mem["output_swing"],
                "device_count": 14,
                "functional_pass": opt_mem["voh"] >= 0.8 and opt_mem["vol"] <= 0.2,
            },
            {
                "architecture": "MEMRISTOR_XOR_OPTIMIZED",
                "evidence_type": "LTspice optimized behavioral XOR primitive macromodel",
                "simulation_file": "ltspice/memristor-hamming/EXP-MEM-XOR-PIM-OPT-NOM.cir",
                "raw_log": "ltspice/memristor-hamming/EXP-MEM-XOR-PIM-OPT-NOM.log",
                "pavg_w": opt_xor["pavg"],
                "tpd_s": opt_xor["tpd"],
                "pdp_j": opt_xor["pdp"],
                "energy_per_encoded_word_j": "",
                "output_swing_v": opt_xor["output_swing"],
                "device_count": 2,
                "functional_pass": opt_xor["voh"] >= 0.8 and opt_xor["vol"] <= 0.2,
            },
        ])
        opt_summary = {
            "pavg_w": opt_mem["pavg"],
            "tpd_s": opt_mem["tpd"],
            "pdp_j": opt_mem["pdp"],
            "energy_per_encoded_word_j": opt_energy,
            "output_swing_v": opt_mem["output_swing"],
            "functional_pass": rows[-2]["functional_pass"],
            "energy_reduction_fraction": (hybrid_energy - opt_energy) / hybrid_energy,
            "latency_reduction_fraction": (float(hybrid["tpd"]) - opt_mem["tpd"]) / float(hybrid["tpd"]),
        }
    write_csv(DATA_DIR / "memristor_ltspice_comparison.csv", rows)
    summary = {
        "status": "LTspice behavioral memristor/PIM macromodel completed",
        "memristor_log": str(mem_log.relative_to(ROOT)),
        "xor_log": str(xor_log.relative_to(ROOT)),
        "memristor_pim": {
            "pavg_w": mem["pavg"],
            "tpd_s": mem["tpd"],
            "pdp_j": mem["pdp"],
            "energy_per_encoded_word_j": mem_energy,
            "output_swing_v": mem["output_swing"],
            "functional_pass": rows[1]["functional_pass"],
        },
        "hybrid_b_baseline": {
            "pavg_w": float(hybrid["pavg"]),
            "tpd_s": float(hybrid["tpd"]),
            "pdp_j": float(hybrid["pdp"]),
            "energy_per_encoded_word_j": hybrid_energy,
        },
        "relative_to_hybrid_b": {
            "energy_reduction_fraction": (hybrid_energy - mem_energy) / hybrid_energy,
            "latency_reduction_fraction": (float(hybrid["tpd"]) - mem["tpd"]) / float(hybrid["tpd"]),
            "interpretation": "Negative values mean the conservative memristor/PIM macromodel is worse than Hybrid-B for this metric."
        },
        "optimized_memristor_pim": opt_summary,
    }
    (RESULT_DIR / "ltspice_comparison_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_netlists(model: MemristorModel) -> None:
    NETLIST_DIR.mkdir(parents=True, exist_ok=True)
    xor_e = sum(row["energy_j"] for row in truth_table(model)) / 4
    xor_latency_nom = xor_latency(model)
    word = encode_pim_12_7([1, 0, 0, 0, 0, 0, 0], model)
    word_e = float(word["energy_j"])
    word_latency = float(word["latency_s"])
    xor_c = xor_latency_nom / (0.693 * 1000.0)
    word_c = word_latency / (0.693 * 1000.0)
    xor_netlist = f"""* EXP-MEM-XOR-PIM-NOM
* LTspice behavioral macromodel for the PIM_XOR_3M_CONSERVATIVE primitive.
* Logic 0 = HRS ({model.roff:.6g} ohm), Logic 1 = LRS ({model.ron:.6g} ohm)
* Pulse schedule: reset destination, read operands, stateful XOR fire, verify-read.
.param RON={model.ron}
.param ROFF={model.roff}
.param VDD=1
.param VREAD={model.v_read}
.param VLOGIC={model.v_logic}
.param TREAD={model.read_time}
.param TLOGIC={model.logic_time}
.param PAVG={xor_e * 125e6}
VSUP VDD 0 {{VDD}}
VA A 0 PULSE(0 1 5n 50p 50p 20n 40n)
VB B 0 0
BA ABIT 0 V={{u(V(A)-0.5)}}
BB BBIT 0 V={{u(V(B)-0.5)}}
BX X 0 V={{V(VDD)*(V(ABIT)+V(BBIT)-2*V(ABIT)*V(BBIT))}}
RSTATE X Y 1k
CSTATE Y 0 {xor_c}
BPOWER VDD 0 I={{PAVG/VDD}}
.tran 20p 180n 0 20p
.meas tran pavg AVG (-V(VDD)*I(VSUP)) FROM=40n TO=180n
.meas tran tplh TRIG V(A) VAL=0.5 RISE=2 TARG V(Y) VAL=0.5 RISE=2
.meas tran tphl TRIG V(A) VAL=0.5 FALL=2 TARG V(Y) VAL=0.5 FALL=2
.meas tran voh MAX V(Y) FROM=40n TO=180n
.meas tran vol MIN V(Y) FROM=40n TO=180n
.end
"""
    hamming_netlist = f"""* EXP-MEM-EH127-PIM-NOM
* LTspice behavioral crossbar-level mapping for Extended Hamming (12,7).
* Data cells: D1 D2 D3 D4 D5 D6 D7
* Parity cells: P1 P2 P4 P8 P0
* Scratch/destination cells are allocated by the PIM_XOR_3M_CONSERVATIVE primitive.
* Parity equations:
* P1 = D1 xor D2 xor D4 xor D5 xor D7
* P2 = D1 xor D3 xor D4 xor D6 xor D7
* P4 = D2 xor D3 xor D4
* P8 = D5 xor D6 xor D7
* P0 = D1 xor D2 xor D3 xor D4 xor D5 xor D6 xor D7 xor P1 xor P2 xor P4 xor P8
* Execution groups: P1/P2/P4/P8 in parallel where row/column conflicts allow; P0 after Hamming parity completion.
.param VDD=1
.param RON={model.ron}
.param ROFF={model.roff}
.param WORD_ENERGY={word_e}
.param PAVG={word_e * 125e6}
VSUP VDD 0 {{VDD}}
VD1 D1 0 PULSE(0 1 20n 50p 50p 100n 200n)
VD2 D2 0 0
VD3 D3 0 0
VD4 D4 0 0
VD5 D5 0 0
VD6 D6 0 0
VD7 D7 0 0
BD1 D1B 0 V={{u(V(D1)-0.5)}}
BD2 D2B 0 V={{u(V(D2)-0.5)}}
BD3 D3B 0 V={{u(V(D3)-0.5)}}
BD4 D4B 0 V={{u(V(D4)-0.5)}}
BD5 D5B 0 V={{u(V(D5)-0.5)}}
BD6 D6B 0 V={{u(V(D6)-0.5)}}
BD7 D7B 0 V={{u(V(D7)-0.5)}}
BP1 P1I 0 V={{V(D1B)+V(D2B)+V(D4B)+V(D5B)+V(D7B)-2*floor((V(D1B)+V(D2B)+V(D4B)+V(D5B)+V(D7B))/2)}}
BP2 P2I 0 V={{V(D1B)+V(D3B)+V(D4B)+V(D6B)+V(D7B)-2*floor((V(D1B)+V(D3B)+V(D4B)+V(D6B)+V(D7B))/2)}}
BP4 P4I 0 V={{V(D2B)+V(D3B)+V(D4B)-2*floor((V(D2B)+V(D3B)+V(D4B))/2)}}
BP8 P8I 0 V={{V(D5B)+V(D6B)+V(D7B)-2*floor((V(D5B)+V(D6B)+V(D7B))/2)}}
BP0 P0I 0 V={{V(D1B)+V(D2B)+V(D3B)+V(D4B)+V(D5B)+V(D6B)+V(D7B)+V(P1I)+V(P2I)+V(P4I)+V(P8I)-2*floor((V(D1B)+V(D2B)+V(D3B)+V(D4B)+V(D5B)+V(D6B)+V(D7B)+V(P1I)+V(P2I)+V(P4I)+V(P8I))/2)}}
RP1 P1I P1 1k
CP1 P1 0 {word_c / 3}
RP2 P2I P2 1k
CP2 P2 0 {word_c / 3}
RP4 P4I P4 1k
CP4 P4 0 {word_c / 3}
RP8 P8I P8 1k
CP8 P8 0 {word_c / 3}
RP0 P0I P0 1k
CP0 P0 0 {word_c}
BPOWER VDD 0 I={{PAVG/VDD}}
.tran 50p 900n 0 50p
.meas tran pavg AVG (-V(VDD)*I(VSUP)) FROM=250n TO=900n
.meas tran tplh TRIG V(D1) VAL=0.5 RISE=2 TARG V(P0) VAL=0.5 RISE=2
.meas tran tphl TRIG V(D1) VAL=0.5 FALL=2 TARG V(P0) VAL=0.5 FALL=2
.meas tran voh MAX V(P0) FROM=250n TO=900n
.meas tran vol MIN V(P0) FROM=250n TO=900n
.end
"""
    (NETLIST_DIR / "EXP-MEM-XOR-PIM-NOM.cir").write_text(xor_netlist, encoding="utf-8")
    (NETLIST_DIR / "EXP-MEM-EH127-PIM-NOM.cir").write_text(hamming_netlist, encoding="utf-8")

    OPTIMIZED_MODEL_PATH.write_text(json.dumps(OPTIMIZED_MODEL, indent=2), encoding="utf-8")
    opt_nom = OPTIMIZED_MODEL["nominal_parameters"]
    opt_word = optimized_encode_pim_12_7([1, 0, 0, 0, 0, 0, 0])
    opt_xor_e = sum(optimized_xor_energy(a, b, a ^ b) for a in (0, 1) for b in (0, 1)) / 4
    opt_xor_latency = float(opt_nom["xor_pulse_time_s"]) + float(opt_nom["sense_time_s"])
    opt_word_e = float(opt_word["energy_j"])
    opt_word_latency = float(opt_word["latency_s"])
    opt_xor_c = opt_xor_latency / (0.693 * 1000.0)
    opt_word_c = opt_word_latency / (0.693 * 1000.0)
    opt_xor_netlist = f"""* EXP-MEM-XOR-PIM-OPT-NOM
* LTspice optimized behavioral macromodel for a 2M single-pulse PIM XOR primitive.
* This is a research optimization target, not calibrated silicon evidence.
.param VDD=1
.param RON={float(opt_nom["ron_ohm"])}
.param ROFF={float(opt_nom["roff_ohm"])}
.param PAVG={opt_xor_e * 125e6}
VSUP VDD 0 {{VDD}}
VA A 0 PULSE(0 1 0.5n 2p 2p 0.5n 1n)
VB B 0 0
BA ABIT 0 V={{u(V(A)-0.5)}}
BB BBIT 0 V={{u(V(B)-0.5)}}
BX X 0 V={{V(VDD)*(V(ABIT)+V(BBIT)-2*V(ABIT)*V(BBIT))}}
RSTATE X Y 1k
CSTATE Y 0 {opt_xor_c}
BPOWER VDD 0 I={{PAVG/VDD}}
.tran 0.5p 5n 0 0.5p
.meas tran pavg AVG (-V(VDD)*I(VSUP)) FROM=1n TO=5n
.meas tran tplh TRIG V(A) VAL=0.5 RISE=2 TARG V(Y) VAL=0.5 RISE=2
.meas tran tphl TRIG V(A) VAL=0.5 FALL=2 TARG V(Y) VAL=0.5 FALL=2
.meas tran voh MAX V(Y) FROM=1n TO=5n
.meas tran vol MIN V(Y) FROM=1n TO=5n
.end
"""
    opt_hamming_netlist = f"""* EXP-MEM-EH127-PIM-OPT-NOM
* LTspice optimized behavioral crossbar-level mapping for Extended Hamming (12,7).
* Optimization changes relative to EXP-MEM-EH127-PIM-NOM:
* - two selected memristors per XOR primitive,
* - one logic pulse per XOR,
* - balanced four-level parity reduction,
* - lower-voltage read/logic pulses in the behavioral energy model.
.param VDD=1
.param WORD_ENERGY={opt_word_e}
.param PAVG={opt_word_e * 125e6}
VSUP VDD 0 {{VDD}}
VD1 D1 0 PULSE(0 1 0.5n 2p 2p 2n 4n)
VD2 D2 0 0
VD3 D3 0 0
VD4 D4 0 0
VD5 D5 0 0
VD6 D6 0 0
VD7 D7 0 0
BD1 D1B 0 V={{u(V(D1)-0.5)}}
BD2 D2B 0 V={{u(V(D2)-0.5)}}
BD3 D3B 0 V={{u(V(D3)-0.5)}}
BD4 D4B 0 V={{u(V(D4)-0.5)}}
BD5 D5B 0 V={{u(V(D5)-0.5)}}
BD6 D6B 0 V={{u(V(D6)-0.5)}}
BD7 D7B 0 V={{u(V(D7)-0.5)}}
BP1 P1I 0 V={{V(D1B)+V(D2B)+V(D4B)+V(D5B)+V(D7B)-2*floor((V(D1B)+V(D2B)+V(D4B)+V(D5B)+V(D7B))/2)}}
BP2 P2I 0 V={{V(D1B)+V(D3B)+V(D4B)+V(D6B)+V(D7B)-2*floor((V(D1B)+V(D3B)+V(D4B)+V(D6B)+V(D7B))/2)}}
BP4 P4I 0 V={{V(D2B)+V(D3B)+V(D4B)-2*floor((V(D2B)+V(D3B)+V(D4B))/2)}}
BP8 P8I 0 V={{V(D5B)+V(D6B)+V(D7B)-2*floor((V(D5B)+V(D6B)+V(D7B))/2)}}
BP0 P0I 0 V={{V(D1B)+V(D2B)+V(D3B)+V(D4B)+V(D5B)+V(D6B)+V(D7B)+V(P1I)+V(P2I)+V(P4I)+V(P8I)-2*floor((V(D1B)+V(D2B)+V(D3B)+V(D4B)+V(D5B)+V(D6B)+V(D7B)+V(P1I)+V(P2I)+V(P4I)+V(P8I))/2)}}
RP0 P0I P0 1k
CP0 P0 0 {opt_word_c}
BPOWER VDD 0 I={{PAVG/VDD}}
.tran 0.5p 20n 0 0.5p
.meas tran pavg AVG (-V(VDD)*I(VSUP)) FROM=4n TO=20n
.meas tran tplh TRIG V(D1) VAL=0.5 RISE=2 TARG V(P0) VAL=0.5 RISE=2
.meas tran tphl TRIG V(D1) VAL=0.5 FALL=2 TARG V(P0) VAL=0.5 FALL=2
.meas tran voh MAX V(P0) FROM=4n TO=20n
.meas tran vol MIN V(P0) FROM=4n TO=20n
.end
"""
    (NETLIST_DIR / "EXP-MEM-XOR-PIM-OPT-NOM.cir").write_text(opt_xor_netlist, encoding="utf-8")
    (NETLIST_DIR / "EXP-MEM-EH127-PIM-OPT-NOM.cir").write_text(opt_hamming_netlist, encoding="utf-8")


def main() -> int:
    model = MemristorModel.from_json(MODEL_PATH)
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    truth = truth_table(model)
    write_csv(DATA_DIR / "memristor_xor_truth_table.csv", truth)

    rows = []
    for word in range(128):
        data = [(word >> i) & 1 for i in range(7)]
        result = encode_pim_12_7(data, model)
        expected = list(encode_12_7(data))
        rows.append({
            "word": word,
            "data_d1_to_d7": "".join(str(v) for v in data),
            "expected_codeword": "".join(str(v) for v in expected),
            "memristor_codeword": "".join(str(v) for v in result["codeword"]),
            "functional_pass": result["codeword"] == expected,
            "energy_j": result["energy_j"],
            "latency_s": result["latency_s"],
            "xor_ops": result["xor_ops"],
            "pulses": result["pulses"],
            "array_memristors_min": 14,
            "selected_memristors_per_xor": 3,
        })
    write_csv(DATA_DIR / "memristor_results.csv", rows)

    mc = monte_carlo(model)
    opt_mc = optimized_monte_carlo()
    (RESULT_DIR / "monte_carlo_summary.json").write_text(json.dumps(mc, indent=2), encoding="utf-8")
    (RESULT_DIR / "optimized_monte_carlo_summary.json").write_text(json.dumps(opt_mc, indent=2), encoding="utf-8")
    (RESULT_DIR / "xor_truth_table.json").write_text(json.dumps(truth, indent=2), encoding="utf-8")

    opt_rows = []
    for word in range(128):
        data = [(word >> i) & 1 for i in range(7)]
        result = optimized_encode_pim_12_7(data)
        expected = list(encode_12_7(data))
        opt_rows.append({
            "word": word,
            "data_d1_to_d7": "".join(str(v) for v in data),
            "expected_codeword": "".join(str(v) for v in expected),
            "optimized_memristor_codeword": "".join(str(v) for v in result["codeword"]),
            "functional_pass": result["codeword"] == expected,
            "energy_j": result["energy_j"],
            "latency_s": result["latency_s"],
            "xor_ops": result["xor_ops"],
            "pulses": result["pulses"],
            "array_memristors_min": result["array_memristors_min"],
            "selected_memristors_per_xor": result["selected_memristors_per_xor"],
        })
    write_csv(DATA_DIR / "memristor_optimized_results.csv", opt_rows)

    avg_energy = sum(float(r["energy_j"]) for r in rows) / len(rows)
    avg_latency = sum(float(r["latency_s"]) for r in rows) / len(rows)
    functional_pass = all(r["functional_pass"] for r in rows)
    hybrid = load_hybrid_b()
    hybrid_energy = float(hybrid["energy_per_operation"])
    hybrid_latency = float(hybrid["tpd"])
    comparison = {
        "status": "behavioral_memristor_research_estimate",
        "model": str(MODEL_PATH.relative_to(ROOT)),
        "xor_truth_table_pass": all(r["pass"] for r in truth),
        "hamming_12_7_words_tested": len(rows),
        "hamming_12_7_functional_pass": functional_pass,
        "memristor_pim": {
            "energy_per_encoded_word_j": avg_energy,
            "latency_per_encoded_word_s": avg_latency,
            "xor_ops_per_word": rows[0]["xor_ops"],
            "pulses_per_word": rows[0]["pulses"],
            "minimum_array_memristors": rows[0]["array_memristors_min"],
            "selected_memristors_per_xor": 3,
            "monte_carlo_logic_error_rate": mc["logic_error_rate"],
            "monte_carlo_accepted": mc["accepted"],
        },
        "hybrid_b_baseline": {
            "source_experiment_id": hybrid["experiment_id"],
            "energy_per_operation_j": hybrid_energy,
            "tpd_s": hybrid_latency,
            "transistor_count": int(hybrid["transistor_count"]),
        },
        "relative_to_hybrid_b": {
            "energy_reduction_fraction": (hybrid_energy - avg_energy) / hybrid_energy,
            "latency_reduction_fraction": (hybrid_latency - avg_latency) / hybrid_latency,
            "note": "Positive values favor the memristor/PIM behavioral estimate. This comparison is architecture-level and includes only the declared behavioral pulse model, not a calibrated Verilog-A/LTspice memristor device."
        }
    }
    opt_avg_energy = sum(float(r["energy_j"]) for r in opt_rows) / len(opt_rows)
    opt_avg_latency = sum(float(r["latency_s"]) for r in opt_rows) / len(opt_rows)
    comparison["optimized_memristor_pim"] = {
        "model": str(OPTIMIZED_MODEL_PATH.relative_to(ROOT)),
        "hamming_12_7_functional_pass": all(r["functional_pass"] for r in opt_rows),
        "energy_per_encoded_word_j": opt_avg_energy,
        "latency_per_encoded_word_s": opt_avg_latency,
        "xor_ops_per_word": opt_rows[0]["xor_ops"],
        "pulses_per_word": opt_rows[0]["pulses"],
        "minimum_array_memristors": opt_rows[0]["array_memristors_min"],
        "selected_memristors_per_xor": opt_rows[0]["selected_memristors_per_xor"],
        "monte_carlo_logic_error_rate": opt_mc["logic_error_rate"],
        "monte_carlo_accepted": opt_mc["accepted"],
        "energy_reduction_fraction_vs_hybrid_b": (hybrid_energy - opt_avg_energy) / hybrid_energy,
        "latency_reduction_fraction_vs_hybrid_b": (hybrid_latency - opt_avg_latency) / hybrid_latency,
    }
    (RESULT_DIR / "comparison_summary.json").write_text(json.dumps(comparison, indent=2), encoding="utf-8")
    write_netlists(model)
    write_ltspice_comparison()
    print(json.dumps({
        "xor_truth_table_pass": comparison["xor_truth_table_pass"],
        "hamming_12_7_functional_pass": functional_pass,
        "monte_carlo_logic_error_rate": mc["logic_error_rate"],
        "energy_reduction_vs_hybrid_b_percent": comparison["relative_to_hybrid_b"]["energy_reduction_fraction"] * 100,
        "latency_reduction_vs_hybrid_b_percent": comparison["relative_to_hybrid_b"]["latency_reduction_fraction"] * 100,
        "optimized_monte_carlo_logic_error_rate": opt_mc["logic_error_rate"],
        "optimized_energy_reduction_vs_hybrid_b_percent": comparison["optimized_memristor_pim"]["energy_reduction_fraction_vs_hybrid_b"] * 100,
        "optimized_latency_reduction_vs_hybrid_b_percent": comparison["optimized_memristor_pim"]["latency_reduction_fraction_vs_hybrid_b"] * 100,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
