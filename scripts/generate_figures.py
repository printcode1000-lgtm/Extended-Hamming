"""Generate simple publication figures from validated data using Pillow."""

from __future__ import annotations

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
COLORS = {"CMOS": "#1f4e79", "GDI": "#a65f00", "FSGDI": "#2f7d4a", "HYBRID_A": "#7d4e9e", "HYBRID_B": "#b33c3c"}
FONT = ImageFont.load_default()


def bar_chart(rows, metric, scale, ylabel, filename):
    width, height = 1400, 820
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    left, top, right, bottom = 150, 100, 1340, 680
    draw.line((left, top, left, bottom), fill="#333333", width=3)
    draw.line((left, bottom, right, bottom), fill="#333333", width=3)
    values = [r[metric] * scale for r in rows]
    maximum = max(values) * 1.12
    bar_width = 180
    gap = (right - left - len(rows) * bar_width) / (len(rows) + 1)
    for i, (row, value) in enumerate(zip(rows, values)):
        x0 = left + gap * (i + 1) + bar_width * i
        y0 = bottom - (value / maximum) * (bottom - top)
        draw.rectangle((x0, y0, x0 + bar_width, bottom), fill=COLORS[row["architecture"]])
        draw.text((x0 + 15, y0 - 28), f"{value:.3g}", fill="#111111", font=FONT)
        draw.text((x0 + 20, bottom + 20), row["architecture"], fill="#111111", font=FONT)
    draw.text((left, 35), "Extended Hamming (12,7): nominal LTspice comparison", fill="#111111", font=FONT)
    draw.text((25, top), ylabel, fill="#111111", font=FONT)
    draw.text((left, 760), "Conditions: PTM 65 nm, 1.2 V, 27 C, 125 MHz, 10 fF. Source: validated .meas logs.", fill="#444444", font=FONT)
    image.save(ROOT / "figures" / filename)


def line_chart(rows, filename):
    width, height = 1400, 820
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    left, top, right, bottom = 150, 100, 1340, 680
    draw.line((left, top, left, bottom), fill="#333333", width=3)
    draw.line((left, bottom, right, bottom), fill="#333333", width=3)
    values = [r["pdp"] * 1e15 for r in rows]
    max_v = max(values) * 1.08
    for arch in ("CMOS", "FSGDI", "HYBRID_A", "HYBRID_B"):
        points = sorted((r for r in rows if r["architecture"] == arch), key=lambda r: r["vdd"])
        coords = []
        for row in points:
            x = left + (row["vdd"] - 0.6) / 0.6 * (right - left)
            y = bottom - (row["pdp"] * 1e15 / max_v) * (bottom - top)
            coords.append((x, y))
            draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=COLORS[arch])
        if len(coords) > 1:
            draw.line(coords, fill=COLORS[arch], width=4)
    for i, arch in enumerate(("CMOS", "FSGDI", "HYBRID_A", "HYBRID_B")):
        draw.rectangle((850 + i * 125, 45, 870 + i * 125, 65), fill=COLORS[arch])
        draw.text((875 + i * 125, 43), arch, fill="#111111", font=FONT)
    draw.text((left, 35), "Extended Hamming (12,7): PDP versus VDD", fill="#111111", font=FONT)
    draw.text((30, top), "PDP (fJ)", fill="#111111", font=FONT)
    for vdd in (0.6, 0.8, 1.0, 1.2):
        x = left + (vdd - 0.6) / 0.6 * (right - left)
        draw.text((x - 10, bottom + 20), f"{vdd:.1f}", fill="#111111", font=FONT)
    draw.text((680, bottom + 55), "VDD (V)", fill="#111111", font=FONT)
    image.save(ROOT / "figures" / filename)


def main() -> None:
    rows = json.loads((ROOT / "thesis" / "data" / "results.json").read_text(encoding="utf-8"))
    valid = [r for r in rows if r.get("status") == "Validated"]
    nominal = [r for r in valid if r["level"] == "EH127" and r["experiment_id"].endswith("-NOM")]
    bar_chart(nominal, "pavg", 1e6, "Average power (uW)", "eh127_nominal_power.png")
    bar_chart(nominal, "tpd", 1e12, "D1-to-P0 delay (ps)", "eh127_nominal_delay.png")
    bar_chart(nominal, "pdp", 1e15, "PDP (fJ)", "eh127_nominal_pdp.png")
    sweep = [r for r in valid if r["level"] == "EH127" and r["temperature_c"] == 27.0 and r["frequency_hz"] == 125e6 and r["load_ff"] == 10.0]
    line_chart(sweep, "eh127_pdp_vs_vdd.png")
    print("Generated 4 figures from validated LTspice data")


if __name__ == "__main__":
    main()
