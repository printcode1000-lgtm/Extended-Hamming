# Research Gap and Motivation

Foundational work established Hamming codes, GDI, and FS-GDI. Later work repeatedly demonstrated reduced transistor count or energy in arithmetic cells, and the baseline 2024 paper applied a six-transistor FS-GDI XOR to Hamming (7,4) and (11,7). Recent ECC research also covers SEC-DED and stronger adjacent-error codes. Therefore, neither extended Hamming nor GDI alone is novel.

The defensible gap is narrower: the accessible literature does not provide a reproducible, fair, transistor-level comparison of CMOS, reconstructed FS-GDI, and selectively restored FS-GDI/CMOS extended Hamming (12,7) encoders using one predictive model, one activity pattern, explicit D1-to-P0 delay measurement, automated `.meas` extraction, and controlled VDD, temperature, load, and frequency sweeps.

The baseline paper stops at Hamming (11,7), reports no overall parity output, does not publish its netlists, and contains inconsistent delay-improvement percentages. It also treats transistor count as area. This thesis addresses those methodological weaknesses and tests two limited hybrid candidates rather than assuming that buffering improves every metric.

The resulting evidence shows a real trade-off. Hybrid-B is faster than CMOS and FS-GDI on the measured D1-to-P0 path, while FS-GDI retains the lowest simulated power and PDP. The scientific contribution is therefore a traceable characterization and a speed-oriented selective-restoration architecture, not a claim of universal superiority.

