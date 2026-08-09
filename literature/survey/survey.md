# Literature Survey

The verified literature establishes three points. First, extended Hamming and SEC-DED are mature coding concepts. Second, GDI and FS-GDI have a long record of reducing device count and switching capacitance, but output swing, body connection, cascade depth, and drive capability remain recurring constraints. Third, recent GDI studies frequently focus on adders, approximate arithmetic, CNFETs, or longer ECC architectures rather than a reproducible short extended-Hamming encoder comparison under one 65-nm transistor model.

The survey table in `survey.csv` separates reported data from unavailable metadata. Missing values are marked for verification rather than inferred. Direct numerical comparisons across CMOS, CNTFET, foundry PDK, FPGA synthesis, and predictive PTM studies are not treated as equivalent.

The 2024 baseline paper is the closest work. It applies FS-GDI to Hamming (11,7), but does not provide an overall parity bit, machine-readable netlists, a complete operating-condition map, or sufficient detail for exact reproduction. A 2024 conference paper also studies GDI Hamming encoding/decoding, which prevents a broad novelty claim based solely on the code or logic family.

The thesis therefore contributes a narrower methodology and circuit study: selective CMOS restoration of a reconstructed FS-GDI network, explicit D1-to-P0 measurement, controlled sweeps, retained negative results, and end-to-end traceability from netlist to chart.

