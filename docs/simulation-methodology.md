# LTspice Simulation Methodology

## Common setup

- Simulator: LTspice 26.0.2 for Windows.
- Device model: PTM 65-nm bulk CMOS beta model released 22 February 2006.
- Nominal condition: 1.2 V, 27 C, 125 MHz, 10 fF per observed output.
- NMOS: L=65 nm, W=120 nm.
- PMOS: L=65 nm, W=240 nm.
- Input edge time: 20 ps.
- XOR transient maximum timestep: 2 ps.
- Encoder transient maximum timestep: 20 ps.
- Power: average of `-V(VDD)*I(VSUP)` over the documented steady-state window.
- Delay: 50%-to-50%; `tpd=(tpLH+tpHL)/2`.
- Extended encoder delay endpoint: overall parity P0.

## Sweeps

The experiment set uses independent one-factor sweeps around the nominal condition: VDD = 0.6, 0.8, 1.0, 1.2 V; temperature = -20, 27, 85 C; load = 1, 5, 10, 20 fF; frequency = 25, 125, 200 MHz. A redundant full Cartesian product is intentionally avoided.

## Functional criteria

For the automated operating map, a measured point is considered functionally acceptable when VOH is at least 0.8 VDD, VOL is at most 0.2 VDD, and propagation delay is less than half the input period. This is an explicit study criterion, not a claim that it is a foundry-qualified noise-margin specification.

## Traceability

Every generated netlist and log has an experiment ID. The manifest is `data/experiments.json`; raw LTspice logs stay next to their circuits; parsed results are in `data/processed/results.csv`; web data are in `thesis/data/results.json`.

