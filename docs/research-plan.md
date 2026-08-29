# Research Plan

The project follows a reproduce-extend-test sequence. The baseline Hamming equations were audited, reference models were exhaustively verified, a predictive model and common sizing rule were fixed, XOR cells were compared, Hamming (11,7) was reproduced, extended Hamming (12,7) and two hybrid candidates were implemented, and controlled sweeps were executed. The web thesis is generated from validated results and remains traceable to raw logs.

## Stage 1: Completed transistor-level foundation

The current validated foundation remains CMOS/FS-GDI/Hybrid-B extended Hamming (12,7). Its role is to provide a measured baseline for any later architecture.

1. Audit Hamming (11,7) baseline equations and reported claims.
2. Reconstruct CMOS, GDI, FS-GDI, Hybrid-A, and Hybrid-B netlists.
3. Verify Hamming/SEC-DED behavior in Python and SystemVerilog.
4. Execute LTspice sweeps using one predictive 65-nm model and common measurement definitions.
5. Retain rejected measurements and document the trade-off: Hybrid-B is fastest at nominal conditions, while FS-GDI is lowest in simulated energy/PDP.

## Stage 2: Memristor/PIM research extension

The memristor extension keeps the same parity equations but changes the computation site. Instead of moving data from memory to external XOR trees, the proposed direction computes parity inside a memristor crossbar array using stateful logic.

Seven-chapter implementation plan:

1. Define the memory-wall problem for Hamming parity generation.
2. Survey Hamming encoders, CMOS/GDI baselines, memristive stateful logic, and crossbar PIM.
3. Formalize Hamming parity equations, LRS/HRS bit representation, and XOR primitive options.
4. Map Hamming (7,4), Hamming (11,7), and extended Hamming (12,7) onto a crossbar.
5. Build a simulation methodology using a documented memristor model plus CMOS peripheral assumptions.
6. Evaluate process variation, sneak paths, write/read disturbance, and reliability mitigation.
7. Compare memristor-PIM results against the repository's CMOS, FS-GDI, and Hybrid-B baselines.

The implemented research-extension document is `docs/memristor-based-hamming-encoder-research-extension.md`; the public portal page is `memristor-extension.html`.

## Stage 3: First memristor LTspice behavioral implementation

The first executable memristor/PIM pass is complete using the same LTspice simulator family as the current project. It adds a behavioral VTEAM/RRAM model, a three-memristor conservative XOR primitive, an extended Hamming (12,7) crossbar mapping, LTspice logs, Monte Carlo variation, and comparison against Hybrid-B.

This pass produced a useful negative result: the conservative memristor/PIM macromodel passes nominal logic checks but does not meet the 90% energy or 80% delay targets. The next research step is therefore optimization, not publication of superiority claims.
