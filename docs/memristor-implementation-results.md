# Memristor/PIM LTspice Implementation Results

**Status:** Completed first conservative LTspice behavioral macromodel and second optimized LTspice behavioral macromodel.

**Simulation program:** LTspice 26.0.2 for Windows, the same simulator family used by the CMOS/FS-GDI/Hybrid-B experiments.

**Evidence boundary:** These are LTspice behavioral memristor/PIM macromodel results. They are not calibrated Verilog-A device-model results and not measured silicon.

## Implemented Items

| Requirement | Implemented artifact | Status |
|---|---|---|
| Select a memristor model | `models/memristor/vteam_rram_research_model.json` and `.md` | Complete for behavioral research layer |
| Build memristor XOR netlist | `ltspice/memristor-hamming/EXP-MEM-XOR-PIM-NOM.cir` | Complete |
| Verify XOR truth table | `data/processed/memristor_xor_truth_table.csv` | Pass |
| Build Hamming crossbar mapping | `ltspice/memristor-hamming/EXP-MEM-EH127-PIM-NOM.cir` | Complete |
| Run LTspice | `.log` files in `ltspice/memristor-hamming/` | Complete |
| Run Monte Carlo variation | `results/memristor/monte_carlo_summary.json` | Complete, not accepted by strict threshold |
| Run optimized Monte Carlo variation | `results/memristor/optimized_monte_carlo_summary.json` | Complete, accepted |
| Calculate energy, delay, and pulse count | `data/processed/memristor_results.csv` and comparison CSV | Complete |
| Calculate optimized energy, delay, and pulse count | `data/processed/memristor_optimized_results.csv` | Complete |
| Compare with Hybrid-B | `data/processed/memristor_ltspice_comparison.csv` | Complete |

## LTspice Measured Results

| Architecture | Evidence type | Power | Delay | PDP | Energy/word | Swing | Pass |
|---|---|---:|---:|---:|---:|---:|---|
| Hybrid-B | Existing LTspice transistor PTM baseline | 11.203 uW | 215.846 ps | 2.418 fJ | 89.623 fJ | 1.204 V | Yes |
| Memristor-PIM behavioral | New LTspice behavioral macromodel | 224.950 uW | 31.537 ns | 7.094 pJ | 1.800 pJ | 0.678 V | Yes |
| Memristor XOR behavioral | New LTspice behavioral primitive | 6.816 uW | 2.963 ns | 20.194 fJ | N/A | 0.980 V | Yes |
| Optimized Memristor-PIM behavioral | New LTspice optimized behavioral macromodel | 0.012 uW | 30.257 ps | 0.000369 fJ | 0.097 fJ | 1.000 V | Yes |
| Optimized Memristor XOR behavioral | New LTspice optimized behavioral primitive | 0.000417 uW | 15.255 ps | 0.000006 fJ | N/A | 1.000 V | Yes |

## Interpretation

The first executable memristor/PIM layer is functionally successful but does not beat Hybrid-B. Relative to Hybrid-B, the conservative LTspice memristor/PIM macromodel is worse by:

- Energy per encoded word: about 20.08x higher.
- Delay: about 146.11x higher.

This means the earlier 90% energy and 80% delay targets are not achieved by the conservative implementation.

The second optimized behavioral pass changes the architecture assumptions: it uses a two-memristor direct XOR abstraction, one pulse per XOR, a lower-voltage high-resistance operating point, and a wide crossbar parity schedule. Under these stated assumptions, the LTspice optimized behavioral macromodel improves over Hybrid-B by:

- Energy per encoded word: about 99.89% lower.
- Delay: about 85.98% lower.
- PDP: substantially lower because both power and measured delay decrease.

The optimized result is therefore no longer negative, but it remains a behavioral research result. It should be used as an optimization target until supported by a calibrated memristor compact model.

## Monte Carlo Reliability

Monte Carlo trials: 10,000.

Logic errors: 15.

Logic error rate: 0.15%.

Mean read-margin ratio: 52.47.

Strict acceptance criterion: error rate <= 0.1%.

Result: not accepted under the strict reliability gate.

Optimized Monte Carlo trials: 10,000.

Optimized logic errors: 0.

Optimized logic error rate: 0.00%.

Optimized mean read-margin ratio: 100.27.

Optimized result: accepted under the same strict reliability gate.

## Scientific Conclusion

The memristor/PIM path is now implemented far enough to become an evidence-bearing research extension rather than only a proposal. The first conservative model produces a negative performance result, proving that moving Hamming encoding into memory is not automatically superior. The optimized model then shows that a positive result is possible when the design uses a faster direct XOR primitive, fewer pulses, stronger read margin, and more parallel parity scheduling. The next scientific gate is calibrated device-level validation.
