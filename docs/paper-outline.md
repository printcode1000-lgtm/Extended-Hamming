# Publication Manuscript Outline

1. Introduction and verified research gap.
2. Audited baseline and extended-code equations.
3. CMOS, FS-GDI, Hybrid-A, and selective-output Hybrid-B circuits.
4. PTM 65-nm LTspice methodology and traceability.
5. XOR-level results.
6. Hamming (11,7) reproduction.
7. Extended Hamming nominal and robustness results.
8. Speed-energy-restoration trade-off.
9. Limitations and conclusion.

Provisional central result: Hybrid-B is the fastest tested extended encoder at the nominal condition and improves all reported metrics relative to CMOS, but unbuffered FS-GDI remains more energy efficient. The final title should emphasize selective restoration and trade-off rather than generic superiority.

## Optional second manuscript: Memristor/PIM extension

The memristor-based Hamming encoder should be treated as a second manuscript or future-work article unless device-level simulations are completed.

1. Introduction: data-movement cost in Hamming parity generation.
2. Related work: Hamming ECC, FS-GDI/Hybrid-B baseline, memristive stateful logic, crossbar PIM, and in-memory ECC.
3. Proposed architecture: memristor crossbar parity mapping and XOR primitive selection.
4. Methodology: memristor compact model, CMOS peripheral assumptions, pulse schedule, and comparison baselines.
5. Reliability: process variation, read margin, sneak paths, write disturbance, and Monte Carlo protocol.
6. Results: XOR truth table, encoder energy, latency, operation count, and variation-aware error rate.
7. Discussion and conclusion: whether improvement comes from device physics, crossbar parallelism, or reduced data transfer.

Provisional contribution statement: a variation-aware memristor processing-in-memory mapping for Hamming parity generation, evaluated against the repository's validated CMOS, FS-GDI, and Hybrid-B extended-Hamming baselines.

Current evidence update: the first LTspice behavioral memristor/PIM macromodel has been executed. It validates the workflow but gives a negative first result relative to Hybrid-B. A publishable second manuscript should therefore focus either on the negative finding as an architectural caution or on a later optimized XOR/pulse schedule that demonstrably improves the result.
