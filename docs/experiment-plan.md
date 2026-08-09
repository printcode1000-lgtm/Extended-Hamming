# Experiment Plan

The master manifest contains 121 experiments:

- 44 XOR experiments: CMOS, GDI, FS-GDI, and Hybrid-A.
- 33 Hamming (11,7) reproduction experiments: CMOS, GDI, and FS-GDI.
- 44 extended Hamming (12,7) experiments: CMOS, FS-GDI, Hybrid-A, and Hybrid-B.

Each architecture receives one nominal point and ten one-factor variations. All important numerical results are generated from LTspice logs. Three low-load points are retained but rejected by validation because their overshoot exceeds the configured supply tolerance; they are not silently discarded.

