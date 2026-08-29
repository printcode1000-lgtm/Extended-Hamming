# Website Quality Report

Project: **Extended Hamming (12,7) Master's Thesis Research**

Author/owner: **Howida Gharib Saad El Din Selim**

Test date: **2026-08-29**

Version: **0.3 — Validated Draft plus Memristor/PIM Research Extension**

## Pages tested

The automatic checker inspected 25 HTML pages. Browser testing covered the academic homepage, online thesis, literature survey, research gap, proposed design, the new memristor/PIM extension page, simulations, results, technical documentation, PDF library, download center, references, the private bilingual research-reference page, and all ten chapter pages. Every tested page produced a non-empty title, a visible H1, loaded its stylesheet, and had no missing image.

## Link and download validation

- Base path tested: `/Extended-Hamming/`.
- Internal links checked: 719.
- Known broken internal links: **0**.
- Unique external links checked across public HTML and research documentation: 7. GitHub, PTM, the deployed GitHub Pages site, and the Pop Lab PDF responded automatically. The Analog Devices LTspice page timed out in the local checker, arXiv failed local certificate verification, and TechRxiv returned HTTP 403 to the automated checker. These are external-checker conditions, not broken internal project links.
- PDF endpoints opened in the browser: 16 of 16.
- Explicit PDF download controls: 16 of 16.
- CSS, JavaScript, images, JSON, CSV, source-code, model, netlist, log, bibliography, and PDF targets were checked for file existence and exact case.
- Detailed machine-readable results: `reports/link-check-report.json` and `reports/link-check-report.html`.

## Responsive layouts

The homepage, results, PDF library, download center, and online thesis were tested at:

| Profile | Viewport |
|---|---:|
| Desktop | 1440 × 900 |
| Laptop | 1024 × 768 |
| Tablet | 768 × 1024 |
| Mobile | 390 × 844 |

No page-level horizontal overflow was detected. Wide result tables scroll inside their labeled containers on mobile. Images remained within the viewport and action links retained usable dimensions. A mobile viewport screenshot and DOM geometry inspection confirmed readable wrapping and an independently scrollable navigation bar.

## Print and accessibility checks

- Both the portal stylesheet and online thesis include `@media print` rules.
- Navigation and action controls are hidden for print, backgrounds are reduced, and figures/tables avoid page splitting where supported.
- Pages use semantic header, navigation, main, section/article, figure, caption, table, and footer elements.
- Navigation has an accessible label, figures have meaningful alternative text, tables use headers and captions, and keyboard focus is visibly styled.
- Text and controls use a high-contrast navy/white academic palette without animation or visual-only navigation.

## Resolved issues

- Added a repository-root GitHub Pages portal using only relative URLs.
- Added consistent author metadata and public attribution.
- Added explicit PDF view and download controls.
- Added responsive table containment and mobile button layout.
- Added `memristor-extension.html`, `docs/memristor-based-hamming-encoder-research-extension.md`, and site navigation links for the Memristor-Based Hamming Encoder research extension.
- Added first conservative LTspice behavioral memristor/PIM implementation files, logs, CSV summaries, and result documentation.
- Added optimized LTspice behavioral memristor/PIM implementation files, logs, CSV summaries, and Monte Carlo evidence with positive energy/delay results under stated behavioral assumptions.
- Updated the private bilingual research-reference page with a detailed scientific account; no public project page links to it.
- Added a Memristor-PIM current development phase report in matching PDF and editable Word formats.
- Added a custom local server that mounts the site at the repository path for realistic testing.
- Excluded large LTspice binary waveforms, caches, credential files, and local QA renders from publication.

## Known and remaining issues

- GitHub Pages is enabled with the Actions source. The deployment workflow completed successfully and the live site was opened in a browser.
- The automated external-URL report records external-only issues for Analog Devices, arXiv local certificate verification, and TechRxiv automated access. These are not internal-site defects; all internal project links pass.
- Institutional identity, university template, supervisor name, and formal submission metadata remain pending and have not been invented.
- The chapter index pages are concise navigation/abstract pages; the integrated online thesis contains the complete current chapter text.
- Browser PDF titles are displayed by the built-in viewer as URLs; document title/author metadata inside all PDFs is correct.

## Result

**PASS for public release readiness:** zero known broken internal links, all 16 PDFs accessible, repository-base routing verified, and desktop-to-mobile layouts usable. Scientific submission status remains a working draft. The memristor/PIM material now includes conservative and optimized LTspice behavioral implementations, but it is explicitly marked as a behavioral macromodel rather than calibrated device-simulation or silicon evidence.
