# Public Release Report

Project: **Extended Hamming (12,7) Low-Power Encoder Research**

Researcher and author: **Howida Gharib Saad El Din Selim**

Release date: **2026-08-09**

Release version: **0.2 — Validated Working Draft**

## GitHub repository status

- Public repository: <https://github.com/printcode1000-lgtm/Extended-Hamming>
- Target/default branch: `main`.
- Remote name: `origin`; no duplicate remote was created.
- Initial validated research-package commit: `67f99a6`. The current `main` tip shown in the public Git history is the authoritative final release identifier because this deployment-status report follows that package commit.
- Secret scan: **PASS**, 316 text/source files inspected before staging; no credential pattern or forbidden credential file detected.
- Publication exclusions: LTspice `.raw`, `.op.raw`, and `.db` artifacts; Python caches; environment/credential files; editor/OS caches; local PDF render QA; and a locally retained published-paper page image.
- Retained for reproducibility: 121 `.cir` source netlists, 121 textual `.log` files, device model, experiment manifest, processed datasets, verification sources, figures, documentation, and PDFs.

## Website and GitHub Pages

- Website status: **deployed, live, and browser-validated**.
- Publishing source: repository root.
- GitHub Pages workflow: `.github/workflows/pages.yml`.
- Repository path tested: `/Extended-Hamming/`.
- Live URL: <https://printcode1000-lgtm.github.io/Extended-Hamming/>
- Website pages: 23 HTML pages, including the research portal, integrated thesis, ten chapter pages, research pages, PDF library, technical index, download center, references, and 404 page.
- Responsive profiles: desktop 1440×900, laptop 1024×768, tablet 768×1024, and mobile 390×844.
- Print styles: available for the public portal and integrated online thesis.
- Accessibility: semantic landmarks, labeled navigation, heading hierarchy, alt text, table captions/headers, visible focus, and scroll-contained mobile tables.

GitHub Pages was configured with the Actions build source. Workflow run `31319051965` completed successfully, and the live homepage, results page, figures, PDF library, and thesis PDF returned HTTP 200 and were opened in the browser.

## PDF status

- PDFs generated: **15**.
- Total rendered pages inspected: **53**.
- Metadata: all PDFs identify Howida Gharib Saad El Din Selim as author and use a document-specific title.
- Browser access: 15 of 15 opened under the repository base path.
- Download controls: 15 of 15 present in the PDF library.

Documents available:

1. Working Master's Thesis Draft.
2. Literature Survey.
3. Research Gap and Contribution.
4. Original Paper Audit.
5. Proposed Hybrid Extended Hamming Encoder.
6. LTspice Simulation Methodology.
7. 65-nm Device Model Documentation.
8. Simulation Measurement Definitions.
9. Software and Research Tools.
10. GitHub Public Repository Guide.
11. Reproducibility Guide.
12. Simulation Results and Analysis.
13. SEC-DED Verification Documentation.
14. Project Technical Architecture.
15. Publication Plan and Manuscript Outline.

The detailed inventory is in `docs/pdf-inventory.md`.

## Scientific and simulation evidence

- 121 LTspice experiments executed.
- 118 measurement sets validated.
- Three low-load measurements transparently rejected for supply-bound overshoot.
- Nominal, VDD, temperature, frequency, and load comparisons are available.
- Python SEC-DED verification passed 128 data words, 1,536 single-bit errors, and 8,448 double-bit errors.
- SystemVerilog encoder and testbench sources are available.
- Machine-readable experiment IDs link circuit, model, input condition, netlist, log, processed result, and figure/table output.

## Link validation

- HTML pages checked: 23.
- Internal links checked: 289.
- Known broken internal links: **0**.
- Unique external links checked across public HTML and documentation: 4. GitHub, PTM, and GitHub Pages passed automatically; the official Analog Devices LTspice page was manually verified after an automated timeout.
- Missing PDFs or downloads: **0**.
- Incorrect-case paths: **0**.
- Broken anchors: **0**.

See `reports/link-check-report.json`, `reports/link-check-report.html`, and `docs/website-quality-report.md`.

## Publication and completion status

The repository is suitable for public scholarly inspection and reproducibility review. It is **not** a final university submission and does not claim publication, acceptance, peer review, fabrication, or measured silicon.

Pending scientific or supervisor actions:

- Supervisor approval of the reconstructed FS-GDI cell and the selected contribution framing.
- University-format title/front-matter data, affiliation, supervisor, and candidate metadata.
- Optional cross-check using an authorized foundry PDK or a second simulator.
- Post-layout parasitics, lower-voltage boundary search, and statistical variation if required by the publication target.
- Final venue selection, manuscript preparation, and formal novelty review.
- Selection of an explicit public reuse license after institutional/supervisor review.

No pending LTspice run exists in the current 121-experiment manifest. The optional checks above are future evidence expansions rather than missing data silently represented as complete.
