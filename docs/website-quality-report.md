# Website Quality Report

Project: **Extended Hamming (12,7) Master's Thesis Research**

Author/owner: **Howida Gharib Saad El Din Selim**

Test date: **2026-08-09**

Version: **0.2 — Validated Draft**

## Pages tested

The automatic checker inspected 23 HTML pages. Browser testing opened the academic homepage, online thesis, literature survey, research gap, proposed design, simulations, results, technical documentation, PDF library, download center, references, and all ten chapter pages. Every tested page produced a non-empty title, a visible H1, loaded its stylesheet, and had no missing image.

## Link and download validation

- Base path tested: `/Extended-Hamming/`.
- Internal links checked: 289.
- Known broken internal links: **0**.
- Unique external links checked across public HTML and research documentation: 4. GitHub, PTM, and the deployed GitHub Pages site responded automatically; the Analog Devices LTspice page timed out in the local checker but was independently opened and verified from the official page.
- PDF endpoints opened in the browser: 15 of 15.
- Explicit PDF download controls: 15 of 15.
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
- Added a custom local server that mounts the site at the repository path for realistic testing.
- Excluded large LTspice binary waveforms, caches, credential files, and local QA renders from publication.

## Known and remaining issues

- GitHub Pages is enabled with the Actions source. The deployment workflow completed successfully and the live site was opened in a browser.
- The automated external-URL report records one Analog Devices timeout. This is not an internal-site defect; the official LTspice page was independently opened and verified.
- Institutional identity, university template, supervisor name, and formal submission metadata remain pending and have not been invented.
- The chapter index pages are concise navigation/abstract pages; the integrated online thesis contains the complete current chapter text.
- Browser PDF titles are displayed by the built-in viewer as URLs; document title/author metadata inside all PDFs is correct.

## Result

**PASS for public release readiness:** zero known broken internal links, all 15 PDFs accessible, repository-base routing verified, and desktop-to-mobile layouts usable. Scientific submission status remains a working draft.
