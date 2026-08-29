# Extended Hamming (12,7) Low-Power Encoder Research

**Researcher, thesis author, project author, and research implementation author:** Howida Gharib Saad El Din Selim

**Status:** Research Project Version 0.3 — validated working thesis draft plus a memristor/PIM research-extension layer; publication manuscript in preparation.

This public repository supports a Master's research project on transistor-level CMOS, gate-diffusion-input (GDI), full-swing GDI (FS-GDI), and selective hybrid FS-GDI/CMOS Hamming encoders. It reproduces a published Hamming (11,7) baseline, extends the Boolean architecture to extended Hamming (12,7) SEC-DED, and evaluates a speed-oriented selective-restoration candidate using LTspice 26.0.2 and a University of Minnesota 65-nm predictive technology model (PTM).

The project does **not** claim fabrication, measured silicon, foundry sign-off, peer review, acceptance, or publication. PTM is a predictive research model and is not a commercial foundry PDK.

## Motivation and objectives

Low-transistor-count XOR logic can reduce switched capacitance, but device count alone does not establish useful power, delay, energy, output swing, or operating robustness. The project therefore:

1. Audits and reproduces the published Hamming (11,7) FS-GDI baseline under a disclosed environment.
2. Implements and exhaustively verifies extended Hamming (12,7) SEC-DED behavior.
3. Compares CMOS, GDI, FS-GDI, and limited hybrid architectures using common stimuli and measurement definitions.
4. Measures power, critical-path delay, PDP, energy, output swing, and hardware complexity across voltage, temperature, frequency, and load sweeps.
5. Preserves experiment provenance and rejected results for independent review.

## Main contribution

The proposed **Hybrid-B** architecture uses FS-GDI parity networks and selectively restores only the five externally observed parity outputs with CMOS buffers. At the nominal condition (1.2 V, 27 °C, 125 MHz, 10 fF), Hybrid-B uses approximately 11.203 µW, has a D1-to-P0 delay of 215.846 ps, a PDP of 2.418 fJ, and 152 transistors. Relative to the CMOS reference, these values correspond to improvements of 58.54% in power, 37.43% in delay, 74.06% in PDP, and 42.42% in transistor count.

This is a trade-off, not a universal superiority claim: unbuffered FS-GDI retains the lowest simulated power and PDP, while Hybrid-B is the fastest nominal extended-encoder candidate in the evaluated set.

## Memristor/PIM research extension

A new scientific extension studies how the verified Hamming parity equations and validated Hybrid-B baseline can be used as the starting point for a **Memristor-Based Hamming Encoder**. The extension reframes the next research question from "which external XOR circuit is best?" to "can Hamming parity be generated inside a memristor crossbar memory using stateful logic?"

The extension now includes two LTspice behavioral memristor/PIM passes: a conservative three-memristor XOR implementation retained as a negative baseline, and an optimized two-memristor/single-pulse crossbar parity implementation retained as the positive research target. The optimized pass improves energy and delay versus Hybrid-B under stated behavioral assumptions, while the conservative pass shows why the optimization is necessary.

Key files:

- `docs/memristor-based-hamming-encoder-research-extension.md`
- `docs/memristor-implementation-results.md`
- `memristor-extension.html`
- `models/memristor/vteam_rram_research_model.json`
- `scripts/memristor_pim_hamming.py`
- `ltspice/memristor-hamming/EXP-MEM-XOR-PIM-NOM.cir`
- `ltspice/memristor-hamming/EXP-MEM-EH127-PIM-NOM.cir`
- `ltspice/memristor-hamming/EXP-MEM-XOR-PIM-OPT-NOM.cir`
- `ltspice/memristor-hamming/EXP-MEM-EH127-PIM-OPT-NOM.cir`
- `data/processed/memristor_ltspice_comparison.csv`

## Evidence status

- 121 LTspice experiments generated and executed.
- 118 measurement sets accepted by automated validation.
- Three low-load points retained but rejected because overshoot exceeded the configured supply tolerance.
- 128 data words, 1,536 single-bit-error cases, and 8,448 double-bit-error cases passed exhaustive Python SEC-DED verification.
- SystemVerilog reference encoder and testbench are included; transistor-level decoder and post-layout extraction are outside the current scope.

### Result classes

- **Published baseline results:** values and claims reported by the audited source paper; recorded in the literature and audit documents.
- **Reproduced results:** new LTspice Hamming (11,7) runs using the disclosed predictive model, not numerical duplicates of an undisclosed Cadence/foundry setup.
- **New thesis simulation results:** extended Hamming (12,7) CMOS, FS-GDI, Hybrid-A, and Hybrid-B comparisons and sweeps in `data/processed/`.
- **Pending work:** supervisor review, institutional front matter, and optional foundry-PDK or second-simulator cross-check.

## Repository structure

| Path | Purpose |
|---|---|
| `ltspice/` | Reproducible `.cir` source netlists, textual `.log` measurements, and shared circuit library |
| `models/` | University of Minnesota 65-nm predictive bulk-CMOS model |
| `scripts/` | SEC-DED verification, netlist generation, LTspice execution, result validation, figures, PDFs, and QA |
| `verification/verilog/` | SystemVerilog encoder reference and testbench |
| `data/` | Experiment manifest, input vectors, processed CSV/JSON results |
| `figures/` | Original plots generated from processed measurements |
| `literature/` and `references/` | Survey synthesis, comparison data, and BibTeX records |
| `docs/` | Research decisions, definitions, plans, quality reports, and release documentation |
| `pdf/` | Fifteen print-ready academic and technical documents |
| `thesis/` | Printable chaptered web thesis and its data assets |
| root HTML files | GitHub Pages academic portal, PDF library, technical index, and download center |

Large LTspice binary waveform/cache files (`.raw`, `.op.raw`, `.db`) are intentionally ignored because they are generated from the retained netlists and can be reproduced.

## Requirements

- Windows with [LTspice](https://www.analog.com/en/resources/design-tools-and-calculators/ltspice-simulator.html) 26.0.2 or a compatible current version.
- Python 3.11 or later. Plot, PDF, and Word regeneration additionally use Matplotlib, ReportLab, Pillow, pypdf, pypdfium2, and python-docx.
- Git for cloning and version control.
- The included PTM model, used subject to its source terms and research limitations.

## Reproducible workflow

From the repository root:

```powershell
python scripts/verify_secded.py
python scripts/build_ltspice.py
python scripts/run_ltspice.py --exe "C:\Path\To\LTspice.exe" --level ALL
python scripts/sanitize_logs.py
python scripts/results_pipeline.py
python scripts/summarize_results.py
python scripts/generate_figures.py
python scripts/export_web_data.py
python scripts/generate_academic_pdfs.py
python scripts/generate_academic_word.py
python scripts/link_check.py
python scripts/secret_scan.py
```

The exact experiment parameters are in `data/experiments.json`; common definitions are in `docs/measurement-definitions.md`. Rebuilding netlists overwrites generated `.cir` files by design, so review local scientific changes first.

## Website and documents

- Academic website: [GitHub Pages project site](https://printcode1000-lgtm.github.io/Extended-Hamming/)
- [Working thesis PDF](pdf/thesis/Howida_Gharib_Extended_Hamming_MSc_Thesis.pdf)
- [Academic PDF and Word inventory](docs/pdf-inventory.md)
- [Reproducibility guide](pdf/reproducibility/Reproducibility_Guide.pdf)
- [Simulation results](pdf/simulation/Simulation_Results_and_Analysis.pdf)
- [Memristor/PIM research extension](memristor-extension.html)
- [Memristor implementation results](docs/memristor-implementation-results.md)

To preview under the same repository base path used by GitHub Pages:

```powershell
python scripts/serve_pages.py --port 8765
```

Then open `http://127.0.0.1:8765/Extended-Hamming/`.

## Citation and publication status

No DOI or accepted manuscript exists yet. Until formal citation metadata is assigned, cite the researcher, repository title, repository URL, version, and access date. A manuscript outline is available in `docs/paper-outline.md`; submission remains pending.

## License and model status

No blanket project license has yet been selected. Copyright remains with Howida Gharib Saad El Din Selim unless an individual source file states otherwise. External references, LTspice, and the predictive model retain their respective owners' terms. A supervisor or institutional repository should approve the final licensing choice before reuse beyond ordinary scholarly inspection.
