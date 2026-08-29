"""Add Word download links beside academic PDF links in site pages."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPLACEMENTS = {
    "index.html": {
        '<a class="button" href="pdf/thesis/Howida_Gharib_Extended_Hamming_MSc_Thesis.pdf" download>Download PDF</a></div></article><article class="card"><h3>Literature and gap</h3>':
        '<a class="button" href="pdf/thesis/Howida_Gharib_Extended_Hamming_MSc_Thesis.pdf" download>Download PDF</a><a class="button" href="pdf/thesis/Howida_Gharib_Extended_Hamming_MSc_Thesis.docx" download>Download Word</a></div></article><article class="card"><h3>Literature and gap</h3>',
        "Open or download fifteen print-ready academic and technical PDFs.":
        "Open or download fifteen academic and technical documents as PDF or Word.",
        ">PDF library</a></div></article><article class=\"card\"><h3>Reproducibility</h3>":
        ">Document library</a></div></article><article class=\"card\"><h3>Reproducibility</h3>",
    },
    "literature.html": {
        '<a class="button" href="pdf/research/Literature_Survey.pdf" download>Download PDF</a><a class="button" href="literature/survey/survey.md">View survey source</a>':
        '<a class="button" href="pdf/research/Literature_Survey.pdf" download>Download PDF</a><a class="button" href="pdf/research/Literature_Survey.docx" download>Download Word</a><a class="button" href="literature/survey/survey.md">View survey source</a>',
    },
    "research-gap.html": {
        '<a class="button" href="pdf/research/Research_Gap_and_Contribution.pdf" download>Download PDF</a><a class="button" href="docs/research-gap.md">View source note</a>':
        '<a class="button" href="pdf/research/Research_Gap_and_Contribution.pdf" download>Download PDF</a><a class="button" href="pdf/research/Research_Gap_and_Contribution.docx" download>Download Word</a><a class="button" href="docs/research-gap.md">View source note</a>',
    },
    "results.html": {
        '<a class="button" href="pdf/simulation/Simulation_Results_and_Analysis.pdf" download>Download PDF</a><a class="button" href="data/processed/results.csv" download>Download all results CSV</a>':
        '<a class="button" href="pdf/simulation/Simulation_Results_and_Analysis.pdf" download>Download PDF</a><a class="button" href="pdf/simulation/Simulation_Results_and_Analysis.docx" download>Download Word</a><a class="button" href="data/processed/results.csv" download>Download all results CSV</a>',
    },
    "simulations.html": {
        '<a class="button" href="pdf/technical/LTspice_Simulation_Methodology.pdf" download>Download PDF</a><a class="button" href="data/experiments.json">Experiment manifest</a>':
        '<a class="button" href="pdf/technical/LTspice_Simulation_Methodology.pdf" download>Download PDF</a><a class="button" href="pdf/technical/LTspice_Simulation_Methodology.docx" download>Download Word</a><a class="button" href="data/experiments.json">Experiment manifest</a>',
    },
    "thesis/index.html": {
        '<a href="../pdf/thesis/Howida_Gharib_Extended_Hamming_MSc_Thesis.pdf">View thesis PDF</a> · <a href="../pdf-library.html">PDF library</a>':
        '<a href="../pdf/thesis/Howida_Gharib_Extended_Hamming_MSc_Thesis.pdf">View thesis PDF</a> · <a href="../pdf/thesis/Howida_Gharib_Extended_Hamming_MSc_Thesis.docx" download>Download thesis Word</a> · <a href="../pdf-library.html">PDF library</a>',
    },
    "technical-documentation.html": {
        '<a class="button primary" href="pdf/technical/LTspice_Simulation_Methodology.pdf">View</a><a class="button" href="docs/simulation-methodology.md">Source</a>':
        '<a class="button primary" href="pdf/technical/LTspice_Simulation_Methodology.pdf">View PDF</a><a class="button" href="pdf/technical/LTspice_Simulation_Methodology.docx" download>Word</a><a class="button" href="docs/simulation-methodology.md">Source</a>',
        '<a class="button primary" href="pdf/technical/Software_and_Research_Tools.pdf">View</a><a class="button" href="README.md">Workflow</a>':
        '<a class="button primary" href="pdf/technical/Software_and_Research_Tools.pdf">View PDF</a><a class="button" href="pdf/technical/Software_and_Research_Tools.docx" download>Word</a><a class="button" href="README.md">Workflow</a>',
        '<a class="button primary" href="pdf/reproducibility/GitHub_Public_Repository_Guide.pdf">View</a><a class="button" href="https://github.com/printcode1000-lgtm/Extended-Hamming">Repository</a>':
        '<a class="button primary" href="pdf/reproducibility/GitHub_Public_Repository_Guide.pdf">View PDF</a><a class="button" href="pdf/reproducibility/GitHub_Public_Repository_Guide.docx" download>Word</a><a class="button" href="https://github.com/printcode1000-lgtm/Extended-Hamming">Repository</a>',
        '<a class="button primary" href="pdf/reproducibility/Reproducibility_Guide.pdf">View</a><a class="button" href="docs/experiment-plan.md">Experiment plan</a>':
        '<a class="button primary" href="pdf/reproducibility/Reproducibility_Guide.pdf">View PDF</a><a class="button" href="pdf/reproducibility/Reproducibility_Guide.docx" download>Word</a><a class="button" href="docs/experiment-plan.md">Experiment plan</a>',
        '<a class="button primary" href="pdf/technical/65nm_Device_Model_Documentation.pdf">View</a><a class="button" href="docs/model-documentation.md">Source</a>':
        '<a class="button primary" href="pdf/technical/65nm_Device_Model_Documentation.pdf">View PDF</a><a class="button" href="pdf/technical/65nm_Device_Model_Documentation.docx" download>Word</a><a class="button" href="docs/model-documentation.md">Source</a>',
        '<a class="button primary" href="pdf/technical/Simulation_Measurement_Definitions.pdf">View</a><a class="button" href="docs/measurement-definitions.md">Source</a>':
        '<a class="button primary" href="pdf/technical/Simulation_Measurement_Definitions.pdf">View PDF</a><a class="button" href="pdf/technical/Simulation_Measurement_Definitions.docx" download>Word</a><a class="button" href="docs/measurement-definitions.md">Source</a>',
        '<a class="button primary" href="pdf/research/Original_Paper_Audit.pdf">View</a><a class="button" href="docs/original-paper-audit.md">Source</a>':
        '<a class="button primary" href="pdf/research/Original_Paper_Audit.pdf">View PDF</a><a class="button" href="pdf/research/Original_Paper_Audit.docx" download>Word</a><a class="button" href="docs/original-paper-audit.md">Source</a>',
        '<a class="button primary" href="pdf/simulation/SEC-DED_Verification_Documentation.pdf">View</a><a class="button" href="results/functional_verification.json">Results</a>':
        '<a class="button primary" href="pdf/simulation/SEC-DED_Verification_Documentation.pdf">View PDF</a><a class="button" href="pdf/simulation/SEC-DED_Verification_Documentation.docx" download>Word</a><a class="button" href="results/functional_verification.json">Results</a>',
    },
}


def main() -> None:
    for rel_path, replacements in REPLACEMENTS.items():
        path = ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        original = text
        for old, new in replacements.items():
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")
        changed = "updated" if text != original else "unchanged"
        print(f"{rel_path}: {changed}")


if __name__ == "__main__":
    main()
