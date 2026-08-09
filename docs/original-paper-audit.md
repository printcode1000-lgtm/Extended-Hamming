# Audit of the Baseline Paper

## Source

M. A. M. El-Bendary and O. El-Badry, "FS-GDI Based Area Efficient Hamming (11, 7) Encoding," *International Journal of Electronics*, vol. 111, no. 5, pp. 771-787, 2024, doi: 10.1080/00207217.2023.2192966. The supplied PDF was inspected page by page.

## Core contribution

The paper maps Hamming (7,4) and shortened Hamming (11,7) parity networks to XOR gates implemented with CMOS, GDI, and a six-transistor FS-GDI cell. Cadence Virtuoso simulations are reported for a 65-nm process at 125 MHz and nominally 1.2 V. Power, delay, PDP, and transistor count are compared.

## Verified parity equations

For data D1 through D7, the reported equations are mathematically consistent with even-parity positions 1, 2, 4, and 8:

- P1 = D1 XOR D2 XOR D4 XOR D5 XOR D7
- P2 = D1 XOR D3 XOR D4 XOR D6 XOR D7
- P4 = D2 XOR D3 XOR D4
- P8 = D5 XOR D6 XOR D7

The project independently verified these equations for all 128 possible data words.

## Published tables transcribed

| Circuit | Logic | Power (uW) | Delay (ps) | PDP (reported) | Transistors |
|---|---|---:|---:|---:|---:|
| Hamming (7,4) | CMOS | 34.4 | 72 | 2477e-18 | 72 |
| Hamming (7,4) | GDI | 30 | 80 | 2400e-18 | 40 |
| Hamming (7,4) | FS-GDI | 19 | 33.9 | 644.1e-18 | 36 |
| Hamming (11,7) | CMOS | 52 | 100 | 5200e-18 | 144 |
| Hamming (11,7) | GDI | 45 | 127 | 5715e-18 | 96 |
| Hamming (11,7) | FS-GDI | 38 | 90 | 3420e-18 | 72 |

The PDP products in these tables are arithmetically consistent with power multiplied by delay.

## Numerical inconsistencies

1. Hamming (11,7) delay changes from 100 ps to 90 ps. The improvement is `(100-90)/100 = 10%`, whereas the abstract reports 20%.
2. For Hamming (7,4), 72 ps to 33.9 ps gives 52.92% improvement. The paper uses both 50.91% and 52.91% in different locations.
3. The paper repeatedly interprets a 50% transistor-count reduction as a 50% area improvement. Without layout and extracted dimensions, transistor count is only a hardware-complexity indicator.
4. The text alternates between 0.6/0.9/1.2 V as tested supplies and 1.2 V as the simulation condition, without presenting a complete voltage-sweep table.

## Reproducibility limitations

- The foundry model deck is not supplied.
- Input vectors, transition activity, output load, timestep, measurement window, and exact delay event are insufficiently specified.
- The FS-GDI schematic is shown, but a machine-readable netlist and complete body-connection assumptions are absent.
- No process-corner or statistical setup is reported for the encoder.
- Cadence and PTM simulations should not be expected to match numerically.

## Independent reproduction result

The present LTspice/PTM reproduction uses the same 12 XOR gates implied by the original transistor counts. Under 1.2 V, 27 C, 125 MHz, and 10 fF, the reproduced Hamming (11,7) CMOS and FS-GDI results are traceable in `data/processed/results.csv`. They do not numerically match the publication because the model, simulator, load, stimulus, and reconstructed cell implementation differ. This is documented as an independent circuit-level reproduction rather than a foundry-model replication.

