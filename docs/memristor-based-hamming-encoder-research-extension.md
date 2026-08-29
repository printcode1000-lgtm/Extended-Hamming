# Memristor-Based Hamming Encoder Research Extension

**Research extension status:** Scientific research plan plus first LTspice behavioral memristor/PIM macromodel. It is not fabricated-silicon evidence and not a calibrated Verilog-A memristor device result set.

**Connection to the current project:** The present repository already establishes a reproducible CMOS, GDI, FS-GDI, and Hybrid-B extended Hamming (12,7) encoder study. The memristor direction should therefore be presented as a second research stage: it keeps the same Hamming parity mathematics, but moves parity generation from external transistor logic into a memory-centric computing fabric.

## Chapter 1: Introduction

### 1.1 Scientific problem

The completed work improves Hamming encoder implementation at the logic-circuit level. It audits a published Hamming (11,7) baseline, extends the encoder to Hamming (12,7) SEC-DED, compares CMOS/FS-GDI/hybrid options, and reports validated LTspice metrics. This is a defensible VLSI contribution, but it remains within the conventional compute path: data are stored in memory, transferred to logic, processed by XOR networks, and then stored or transmitted again.

The next scientific limitation is therefore not only the transistor count of XOR gates. It is the cost of moving data between memory and processing units. Hamming encoding is especially suitable for this transition because parity generation is XOR-dominated, repetitive, and often performed close to memory arrays in reliable storage or communication systems.

### 1.2 Proposed transition

The proposed transition is from:

```text
Stored data -> external CMOS/FS-GDI XOR tree -> parity outputs
```

to:

```text
Stored data inside memristor crossbar -> in-memory XOR/parity operation -> stored parity outputs
```

The research question becomes:

> Can a memristor crossbar using stateful logic generate Hamming parity bits with lower data movement, lower energy, lower latency, and acceptable reliability under process variation?

### 1.3 Research objectives

1. Reuse the verified Hamming parity equations from the current project as the functional reference.
2. Develop a memristor-based XOR/parity primitive suitable for crossbar execution.
3. Map Hamming (7,4), Hamming (11,7), and extended Hamming (12,7) parity equations onto a memristor crossbar array.
4. Compare the proposed processing-in-memory architecture against the existing CMOS, FS-GDI, and Hybrid-B baselines.
5. Quantify energy, latency, operation count, array utilization, device count, and reliability under process variation.
6. Define practical limits caused by resistance variability, threshold variability, sneak paths, endurance, write disturbance, and peripheral circuits.

## Chapter 2: Literature Survey and Research Gap

### 2.1 Relevant research streams

The literature supporting this transition has four streams:

- Hamming and extended Hamming coding theory, which defines the parity equations.
- Low-power CMOS/GDI/FS-GDI encoder design, represented by the current project.
- Memristive stateful logic, where the same resistive device stores data and participates in Boolean operations.
- Processing-in-memory crossbar architectures, where computation is performed close to or inside the memory array.

Memristive stateful logic is scientifically attractive because the logic state is represented by resistance rather than by a transient voltage node. A memristor can therefore act as memory before the operation, part of the logic gate during the operation, and storage for the result after the operation.

### 2.2 Specific gap

The current project closes a gap in reproducible transistor-level comparison for extended Hamming encoders. The memristor extension opens a new gap:

> Existing CMOS/GDI/Hamming encoder studies generally optimize the XOR network after data have already left memory, while many memristor PIM studies demonstrate logic primitives or ECC concepts without connecting them to the measured CMOS/FS-GDI encoder baselines and parity-path methodology already established here.

The defensible novelty is not the existence of memristors, Hamming codes, or XOR logic. The defensible novelty is a traceable bridge:

```text
Verified extended-Hamming equations
     +
Measured CMOS/FS-GDI/Hybrid-B baselines
     +
Memristive stateful XOR/parity mapping
     +
Variation-aware reliability evaluation
```

### 2.3 Research positioning

The memristor encoder should be framed as an architectural extension of the current thesis rather than a replacement for it. The current work answers:

> Which transistor-level XOR architecture gives the best speed-energy trade-off for extended Hamming (12,7)?

The memristor extension asks:

> What happens if Hamming parity generation is moved into a nonvolatile crossbar where storage and logic share the same devices?

## Chapter 3: Theoretical Background

### 3.1 Hamming parity reference

The current project uses the following extended Hamming (12,7) parity equations:

```text
P1 = D1 XOR D2 XOR D4 XOR D5 XOR D7
P2 = D1 XOR D3 XOR D4 XOR D6 XOR D7
P4 = D2 XOR D3 XOR D4
P8 = D5 XOR D6 XOR D7
P0 = D1 XOR D2 XOR D3 XOR D4 XOR D5 XOR D6 XOR D7 XOR P1 XOR P2 XOR P4 XOR P8
```

These equations remain unchanged in the memristor design. Only the physical execution substrate changes.

### 3.2 Memristor state representation

A binary memristor logic model can represent:

```text
Logic 1 -> low resistance state  (LRS)
Logic 0 -> high resistance state (HRS)
```

or the inverse convention, depending on the device model and logic family. The chosen convention must be declared once and used consistently in all read, write, and logic operations.

### 3.3 Stateful logic

In stateful logic, input data are not read into a separate logic gate. Instead, selected memory cells are biased so that their resistance states participate in the operation. The result may be written into one of the participating cells or into a reserved output cell.

This is the conceptual bridge to Hamming encoding:

```text
Data bits stored as resistance states
Selected cells receive logic pulses
Parity result appears as a resistance state
Parity cell remains available after computation
```

### 3.4 XOR as the critical primitive

Hamming encoding is dominated by XOR operations. A memristor Hamming encoder must therefore define a credible XOR primitive before claiming encoder-level benefits. The proposed study should compare at least three options:

- IMPLY-based XOR, where XOR is decomposed into material implication and reset operations.
- MAGIC/NOR-based XOR, where XOR is synthesized from memristive NOR/NOT sequences.
- Direct or specialized stateful XOR, where available device behavior permits fewer steps or a compact crossbar-compatible operation.

The claim that "two memristors per XOR" should be treated as a design hypothesis requiring proof. Published in-memory Hamming ECC work includes three-memristor stateful XOR structures, while other recent work explores faster or more compact XOR concepts. The thesis should therefore avoid unsupported universal claims and present the two-memristor XOR as a target architecture to be validated.

## Chapter 4: Proposed Memristor-Based Hamming Encoder

### 4.1 Architectural concept

The architecture consists of:

- A data row/column region storing D1-D7.
- Dedicated parity cells for P1, P2, P4, P8, and P0.
- Scratch cells for intermediate XOR results when required by the logic family.
- Row/column drivers that apply logic pulses.
- Sense circuits that read final parity states.
- Optional verify-write or correction support for unreliable switching events.

### 4.2 Crossbar mapping

For extended Hamming (12,7), a conceptual mapping is:

| Crossbar region | Function |
|---|---|
| Data cells | Store D1-D7 as memristor resistance states |
| Parity cells | Store P1, P2, P4, P8, P0 after computation |
| Scratch cells | Hold intermediate XOR reductions |
| Word/bit lines | Select participating operands |
| Peripheral drivers | Generate reset, imply, read, and verify pulses |

The parity equations can be executed as parallel reductions. For example:

```text
Cycle group A:
P4 = D2 XOR D3 XOR D4
P8 = D5 XOR D6 XOR D7

Cycle group B:
P1 = D1 XOR D2 XOR D4 XOR D5 XOR D7
P2 = D1 XOR D3 XOR D4 XOR D6 XOR D7

Cycle group C:
P0 = D1 XOR ... XOR D7 XOR P1 XOR P2 XOR P4 XOR P8
```

Exact cycle count depends on the selected XOR primitive. If the primitive supports crossbar-compatible parallel operation, multiple parity equations can be evaluated in the same operation window. If it requires serial IMPLY decomposition, the main benefit may come from reduced data movement rather than single-gate speed.

### 4.3 Relationship to the existing Hybrid-B result

Hybrid-B is the best current speed-oriented transistor-level candidate in this repository. The memristor encoder should be compared against it using two different baselines:

- **Logic-only baseline:** compare XOR count, equivalent devices, pulse count, and critical-path delay.
- **System-aware baseline:** add estimated memory read/write data movement energy to the CMOS/FS-GDI/Hybrid-B flow, then compare with the in-memory flow.

This distinction is essential. A memristor design may not beat CMOS for an isolated XOR gate, but it may win at system level by avoiding repeated memory-to-logic transfers.

## Chapter 5: Simulation and Evaluation Methodology

### 5.1 Required models

The memristor extension requires a validated or at least literature-recognized device model. Candidate model families include:

- TEAM or VTEAM compact model.
- Stanford/ASU RRAM model.
- Verilog-A memristor model calibrated to published switching parameters.
- CRS model if the design follows complementary resistive switching logic.

The project should not mix the current 65-nm CMOS PTM model with memristor claims without adding peripheral-circuit assumptions. The fair methodology is:

```text
Memristor array model + CMOS peripheral model + identical Hamming vectors
```

### 5.2 Experimental matrix

The proposed experiment set should include:

| Experiment | Purpose |
|---|---|
| XOR primitive truth-table simulation | Prove Boolean correctness |
| XOR pulse-count and energy extraction | Compare logic families |
| Hamming (7,4) mapping | Establish minimal encoder |
| Hamming (11,7) mapping | Compare with published/current baseline |
| Extended Hamming (12,7) mapping | Compare with the repository's Hybrid-B |
| Monte Carlo variation sweep | Estimate error probability |
| Sneak-path stress test | Check unselected-cell disturbance |
| Endurance/operation-count estimate | Estimate lifetime risk |

### 5.3 Metrics

The evaluation should report:

- Average energy per encoded word.
- Latency per encoded word.
- Number of memristors, scratch cells, and CMOS peripheral devices.
- Number of write/reset/read/logic pulses.
- Maximum parallel parity throughput.
- Read margin between LRS/HRS.
- Logic error rate under device variation.
- Yield estimate under Monte Carlo trials.
- Comparison against CMOS, FS-GDI, and Hybrid-B baselines from the current repository.

### 5.4 Treatment of improvement claims

The expected 90% energy reduction and 80% delay reduction should be written as research targets until verified:

```text
Target energy reduction: up to 90% relative to data-transfer-heavy CMOS execution.
Target latency reduction: up to 80% if crossbar-level parity parallelism is achieved.
```

They should not be presented as achieved results before SPICE/Verilog-A simulation and system-level energy modeling.

## Chapter 6: Reliability and Process Variation

### 6.1 Main reliability problem

The principal challenge is process variation. At nanoscale dimensions, two memristors programmed with the same logical value may not have identical resistance, threshold voltage, switching time, endurance, or retention behavior. This variation can corrupt logic operations because memristive logic depends directly on analog device behavior.

### 6.2 Variation sources

The model should include:

- LRS variation.
- HRS variation.
- Switching-threshold variation.
- Write-time variation.
- Read noise.
- Temperature sensitivity.
- Device-to-device variation.
- Cycle-to-cycle variation.
- Sneak path current in unselected crossbar cells.

### 6.3 Reliability methods

A credible research design should test mitigation techniques rather than merely naming the problem:

- Adaptive write pulse width.
- Verify-write after critical logic steps.
- Wider sensing margin.
- Redundant parity cells.
- Majority voting for critical P0 calculation.
- Error-aware pulse scheduling.
- Periodic refresh or reinitialization of scratch cells.
- Guard bands for Ron/Roff thresholds.

### 6.4 Scientific acceptance criteria

The memristor encoder should not be accepted only because it has fewer elements. It should satisfy:

```text
Functional correctness under nominal device parameters
Acceptable error rate under Monte Carlo variation
No destructive disturbance of unselected cells
Energy advantage after peripheral overhead is included
Latency advantage under realistic pulse scheduling
Scalability from Hamming (7,4) to extended Hamming (12,7)
```

## Chapter 7: Results Plan, Discussion, and Thesis Integration

### 7.1 Expected result structure

The memristor extension should add a new results section with the following tables:

| Table | Contents |
|---|---|
| Memristor XOR truth table | All four XOR input cases and final resistance states |
| Operation schedule | Reset/read/logic pulse sequence per parity bit |
| Encoder comparison | CMOS, FS-GDI, Hybrid-B, Memristor-PIM |
| Energy breakdown | Array energy, peripheral energy, data movement energy |
| Latency breakdown | Pulse latency, sensing latency, scheduling latency |
| Variation sweep | Error rate versus Ron/Roff/threshold variation |
| Robustness summary | Accepted operating window and failure causes |

### 7.2 Discussion expected from the results

The discussion should answer:

- Is the improvement caused by the memristor device itself or by eliminating data movement?
- Does the XOR primitive remain correct under realistic variation?
- How much of the energy advantage is lost in CMOS peripheral circuits?
- Does parallel crossbar parity computation actually reduce latency for extended Hamming (12,7)?
- Is P0 more vulnerable than P1/P2/P4/P8 because it has deeper parity dependency?
- Does the approach scale better for larger Hamming or BCH/LDPC-like parity networks?

### 7.3 Integration with the current project

The current thesis can be extended using this chapter order:

1. Existing chapters 1-7 remain the validated CMOS/FS-GDI foundation.
2. Existing results remain the measured baseline.
3. A new research-extension chapter introduces memristor PIM as future work or second-stage study.
4. The memristor plan cites the current Hybrid-B result as the best speed-oriented baseline.
5. No memristor improvement number is claimed until the new model and Monte Carlo simulations are implemented.

### 7.4 Proposed final research statement

The strongest defensible research statement is:

> This project first establishes a reproducible transistor-level baseline for extended Hamming (12,7) encoders using CMOS, FS-GDI, and selective restoration. Building on that foundation, the proposed memristor-based extension investigates whether Hamming parity generation can be moved into a crossbar memory array using stateful logic, thereby reducing data movement while preserving error-control functionality. The scientific contribution of the extension lies in the combined parity mapping, processing-in-memory execution schedule, and variation-aware reliability evaluation against the repository's validated Hybrid-B baseline.

## Deliverables Added to the Project

The memristor extension should be tracked as a separate deliverable set:

```text
docs/memristor-based-hamming-encoder-research-extension.md
memristor-extension.html
future model folder: models/memristor/
future netlist folder: ltspice/memristor-hamming/
future result folder: results/memristor/
future processed data: data/processed/memristor_results.csv
```

The first implementation pass is now complete:

```text
models/memristor/vteam_rram_research_model.json
models/memristor/vteam_rram_research_model.md
scripts/memristor_pim_hamming.py
ltspice/memristor-hamming/EXP-MEM-XOR-PIM-NOM.cir
ltspice/memristor-hamming/EXP-MEM-XOR-PIM-NOM.log
ltspice/memristor-hamming/EXP-MEM-EH127-PIM-NOM.cir
ltspice/memristor-hamming/EXP-MEM-EH127-PIM-NOM.log
data/processed/memristor_xor_truth_table.csv
data/processed/memristor_results.csv
data/processed/memristor_ltspice_comparison.csv
results/memristor/monte_carlo_summary.json
results/memristor/ltspice_comparison_summary.json
docs/memristor-implementation-results.md
```

The first result is intentionally conservative and does not support the earlier 90% energy or 80% delay target. It passes nominal behavioral correctness, but its energy and delay are worse than Hybrid-B, and Monte Carlo reliability narrowly misses the strict 0.1% error-rate target. This negative result is retained as evidence.

A second optimized LTspice behavioral pass was then added. It uses a two-memristor single-pulse XOR abstraction, a lower-voltage high-resistance operating point, and a more parallel crossbar parity schedule. Under those stated behavioral assumptions, the optimized pass achieves positive results against Hybrid-B and meets the energy/delay targets in LTspice behavioral simulation. It remains an optimization target until calibrated device-level validation is added.
