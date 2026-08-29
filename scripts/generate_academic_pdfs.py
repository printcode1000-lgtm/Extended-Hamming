"""Build the public academic PDF library from verified project sources."""

from __future__ import annotations

import csv
import json
import re
from datetime import date
from html import escape
from pathlib import Path

from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, KeepTogether, LongTable, PageBreak,
    PageTemplate, Paragraph, Spacer, Table, TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parents[1]
AUTHOR = "Howida Gharib Saad El Din Selim"
VERSION = "Research Project Version 0.2 - Validated Draft"
TODAY = date.today().isoformat()

pdfmetrics.registerFont(TTFont("TimesAcademic", r"C:\Windows\Fonts\times.ttf"))
pdfmetrics.registerFont(TTFont("TimesAcademic-Bold", r"C:\Windows\Fonts\timesbd.ttf"))

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="AcademicBody", fontName="TimesAcademic", fontSize=10.5, leading=15, alignment=TA_JUSTIFY, spaceAfter=7))
styles.add(ParagraphStyle(name="AcademicH1", fontName="TimesAcademic-Bold", fontSize=17, leading=21, textColor=colors.HexColor("#183B5B"), spaceBefore=12, spaceAfter=8, keepWithNext=True))
styles.add(ParagraphStyle(name="AcademicH2", fontName="TimesAcademic-Bold", fontSize=13, leading=17, textColor=colors.HexColor("#183B5B"), spaceBefore=9, spaceAfter=5, keepWithNext=True))
styles.add(ParagraphStyle(name="AcademicTitle", fontName="TimesAcademic-Bold", fontSize=24, leading=30, alignment=TA_CENTER, textColor=colors.HexColor("#183B5B"), spaceAfter=16))
styles.add(ParagraphStyle(name="AcademicSubtitle", fontName="TimesAcademic", fontSize=13, leading=18, alignment=TA_CENTER, textColor=colors.HexColor("#4E5964"), spaceAfter=10))
styles.add(ParagraphStyle(name="AcademicCaption", fontName="TimesAcademic", fontSize=8.5, leading=11, alignment=TA_CENTER, textColor=colors.HexColor("#4E5964"), spaceBefore=4, spaceAfter=9))
styles.add(ParagraphStyle(name="AcademicEquation", fontName="TimesAcademic", fontSize=11, leading=15, alignment=TA_CENTER, borderColor=colors.HexColor("#D4D0C8"), borderWidth=.5, borderPadding=6, spaceBefore=6, spaceAfter=8))
styles.add(ParagraphStyle(name="AcademicSmall", fontName="TimesAcademic", fontSize=8, leading=10, alignment=TA_LEFT))


class AcademicDocTemplate(BaseDocTemplate):
    def __init__(self, filename: Path, title: str, pagesize=A4):
        self.document_title = title
        width, height = pagesize
        super().__init__(str(filename), pagesize=pagesize, leftMargin=22*mm, rightMargin=22*mm, topMargin=22*mm, bottomMargin=20*mm,
                         title=title, author=AUTHOR, subject="Extended Hamming (12,7), FS-GDI, CMOS, Low-Power VLSI",
                         keywords="Extended Hamming, SEC-DED, FS-GDI, CMOS, LTspice, 65 nm")
        frame = Frame(self.leftMargin, self.bottomMargin, width-self.leftMargin-self.rightMargin, height-self.topMargin-self.bottomMargin, id="body")
        self.addPageTemplates(PageTemplate(id="academic", frames=frame, onPage=self._decorate))

    def _decorate(self, canvas, doc):
        canvas.saveState()
        canvas.setFont("TimesAcademic", 8)
        canvas.setFillColor(colors.HexColor("#5D6873"))
        if doc.page > 1:
            canvas.drawString(self.leftMargin, 12*mm, AUTHOR)
            canvas.drawRightString(self.pagesize[0]-self.rightMargin, 12*mm, f"Page {doc.page}")
            canvas.setStrokeColor(colors.HexColor("#C9C3B8")); canvas.line(self.leftMargin, 16*mm, self.pagesize[0]-self.rightMargin, 16*mm)
        canvas.setAuthor(AUTHOR); canvas.setTitle(self.document_title)
        canvas.setSubject("Extended Hamming (12,7), FS-GDI, CMOS, Low-Power VLSI")
        canvas.saveState(); canvas.restoreState()
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            style = flowable.style.name
            if style in ("AcademicH1", "AcademicH2"):
                level = 0 if style == "AcademicH1" else 1
                text = flowable.getPlainText()
                key = f"h{level}-{self.seq.nextf('heading')}"
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(text, key, level=level, closed=False)
                self.notify("TOCEntry", (level, text, self.page, key))


def p(text: str, style="AcademicBody"):
    return Paragraph(text, styles[style])


def h1(text: str): return p(text, "AcademicH1")
def h2(text: str): return p(text, "AcademicH2")
def eq(text: str, number: str): return p(f"{escape(text)} &nbsp;&nbsp;&nbsp; ({number})", "AcademicEquation")


def cover(title: str, label: str, subtitle: str = ""):
    return [Spacer(1, 35*mm), p(label.upper(), "AcademicSubtitle"), p(title, "AcademicTitle"),
            p(subtitle, "AcademicSubtitle") if subtitle else Spacer(1, 1), Spacer(1, 20*mm),
            p(f"<b>Researcher and Author</b><br/>{AUTHOR}", "AcademicSubtitle"), Spacer(1, 18*mm),
            p(VERSION, "AcademicSubtitle"), p(TODAY, "AcademicSubtitle"), PageBreak()]


def table(rows, widths=None, font_size=7.5):
    data = [[p(str(cell), "AcademicSmall") for cell in row] for row in rows]
    t = LongTable(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#DDE6ED")), ("TEXTCOLOR", (0,0), (-1,0), colors.HexColor("#183B5B")),
        ("FONTNAME", (0,0), (-1,-1), "TimesAcademic"), ("FONTSIZE", (0,0), (-1,-1), font_size),
        ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#B9B5AD")), ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    return t


def md_flowables(path: Path):
    result = []
    lines = path.read_text(encoding="utf-8").splitlines()
    paragraph = []
    i = 0
    def flush():
        if paragraph:
            text = " ".join(paragraph).replace("**", "")
            result.append(p(escape(text))); paragraph.clear()
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("# "): flush(); result.append(h1(line[2:])); i += 1; continue
        if line.startswith("## "): flush(); result.append(h2(line[3:])); i += 1; continue
        if line.startswith("### "): flush(); result.append(h2(line[4:])); i += 1; continue
        if line.startswith("|") and i+1 < len(lines) and lines[i+1].strip().startswith("|---"):
            flush(); block=[line]; i+=2
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i].strip()); i+=1
            rows=[[c.strip() for c in row.strip("|").split("|")] for row in block]
            result.append(table(rows)); result.append(Spacer(1, 5*mm)); continue
        if line.startswith("- ") or re.match(r"\d+\.\s", line):
            flush(); result.append(p("• " + escape(re.sub(r"^(?:- |\d+\.\s)", "", line)))); i += 1; continue
        if not line: flush(); i += 1; continue
        paragraph.append(line); i += 1
    flush(); return result


def architecture_diagram():
    d = Drawing(470, 150)
    d.add(Rect(10,55,80,40,strokeColor=colors.HexColor("#183B5B"),fillColor=colors.HexColor("#EAF0F4")))
    d.add(String(23,72,"D1 ... D7",fontName="TimesAcademic-Bold",fontSize=10))
    d.add(Line(90,75,145,75,strokeColor=colors.HexColor("#183B5B")))
    d.add(Rect(145,35,130,80,strokeColor=colors.HexColor("#2F7D4A"),fillColor=colors.HexColor("#E8F1EB")))
    d.add(String(165,82,"FS-GDI XOR",fontName="TimesAcademic-Bold",fontSize=10))
    d.add(String(165,62,"parity network",fontName="TimesAcademic",fontSize=10))
    d.add(Line(275,75,330,75,strokeColor=colors.HexColor("#183B5B")))
    d.add(Rect(330,35,125,80,strokeColor=colors.HexColor("#8B2D2D"),fillColor=colors.HexColor("#F4EAEA")))
    d.add(String(348,82,"Selective CMOS",fontName="TimesAcademic-Bold",fontSize=10))
    d.add(String(352,62,"output restoration",fontName="TimesAcademic",fontSize=10))
    d.add(String(150,15,"Hybrid-B: restoration is applied only to externally observed parity outputs.",fontName="TimesAcademic",fontSize=8))
    return d


summary = json.loads((ROOT/"thesis/data/summary.json").read_text(encoding="utf-8"))
functional = json.loads((ROOT/"results/functional_verification.json").read_text(encoding="utf-8"))
nominal = {f"{r['level']}:{r['architecture']}": r for r in summary["nominal"]}


def nominal_table(level="EH127"):
    rows=[["Architecture","Power (uW)","Delay (ps)","PDP (fJ)","Swing (V)","Transistors","Status"]]
    for r in summary["nominal"]:
        if r["level"] != level: continue
        rows.append([r["architecture"],f"{r['pavg']*1e6:.4f}",f"{r['tpd']*1e12:.3f}",f"{r['pdp']*1e15:.4f}",f"{r['output_swing']:.4f}",r["transistor_count"],"Pass" if r["functional_pass"] else "Fail"])
    return table(rows, [30*mm,25*mm,25*mm,25*mm,24*mm,24*mm,18*mm])


REFERENCES = [
    "R. W. Hamming, 'Error Detecting and Error Correcting Codes,' Bell System Technical Journal, vol. 29, no. 2, pp. 147-160, 1950.",
    "A. Morgenshtein, A. Fish, and I. A. Wagner, 'Gate-Diffusion Input (GDI): A Power-Efficient Method for Digital Combinatorial Circuits,' IEEE TVLSI, 2002.",
    "A. Morgenshtein et al., 'Full-Swing Gate Diffusion Input Logic - Case-Study of Low-Power CLA Adder Design,' Integration, 2014.",
    "M. A. M. El-Bendary and O. El-Badry, 'FS-GDI Based Area Efficient Hamming (11,7) Encoding,' International Journal of Electronics, 2024.",
]


def build(path: Path, title: str, label: str, story, toc=False, pagesize=A4):
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = AcademicDocTemplate(path, title, pagesize=pagesize)
    content = cover(title, label)
    if toc:
        content += [h1("Table of Contents"), TableOfContents(), PageBreak()]
    content += story
    doc.multiBuild(content)


def thesis_story():
    body=[h1("Abstract"),p("This working thesis draft evaluates CMOS, GDI, FS-GDI, and hybrid FS-GDI/CMOS implementations of Hamming (11,7) and extended Hamming (12,7). The baseline paper is independently audited, SEC-DED logic is exhaustively verified, and 121 LTspice experiments are executed with a predictive 65-nm PTM model. Of these, 118 measurement sets pass automated validation and three low-load cases are rejected for excessive overshoot. Hybrid-B provides the lowest measured D1-to-P0 delay at the nominal condition, whereas FS-GDI retains the lowest simulated power and PDP."),
          h1("List of Figures"),p("Figure 6.1 Hybrid-B architecture. Figure 8.1 Nominal power. Figure 8.2 D1-to-P0 delay. Figure 8.3 PDP. Figure 8.4 PDP versus VDD."),
          h1("List of Tables"),p("Table 4.1 Hamming reproduction. Table 7.1 Simulation setup. Table 8.1 Extended Hamming comparison. Table 9.1 Contribution evidence."),
          h1("Abbreviations"),table([["Abbreviation","Meaning"],["CMOS","Complementary metal-oxide-semiconductor"],["GDI","Gate diffusion input"],["FS-GDI","Full-swing gate diffusion input"],["PDP","Power-delay product"],["PTM","Predictive technology model"],["SEC-DED","Single-error correction, double-error detection"]],[38*mm,120*mm]),
          h1("Chapter 1 - Introduction"),p("Low-power error-control hardware is dominated by XOR networks. Device count alone does not establish useful operation because pass-transistor degradation, output load, restoration overhead, and cascade depth can change the power-delay trade-off. The objective is to reproduce the baseline Hamming network and test whether selective CMOS restoration produces a defensible extended-Hamming implementation."),
          h2("Research objectives"),p("The work audits the published equations and percentages, verifies extended Hamming logic, compares cells and complete encoders under common conditions, measures energy and signal swing, and maps controlled voltage, temperature, frequency, and load variation."),
          h1("Chapter 2 - Literature Survey"),p("Hamming established the coding theory; Morgenshtein and co-authors established GDI and later FS-GDI. Recent GDI work emphasizes adders, approximate arithmetic, and emerging devices, while recent ECC work addresses SEC-DED and stronger adjacent-error codes. Extended Hamming and GDI are therefore not new by themselves."),
          h2("Research gap and motivation"),p("The closest published Hamming study does not provide extended parity, machine-readable netlists, or a complete robustness map. The gap addressed here is a traceable one-model comparison with explicit P0 timing, common activity, selective restoration, and retained negative results."),
          h1("Chapter 3 - Theoretical Background"),p("Parity bits occupy positions 1, 2, 4, and 8; data occupy positions 3, 5, 6, 7, 9, 10, and 11; P0 is appended at position 12."),
          eq("P1 = D1 XOR D2 XOR D4 XOR D5 XOR D7","3.1"),eq("P2 = D1 XOR D3 XOR D4 XOR D6 XOR D7","3.2"),eq("P4 = D2 XOR D3 XOR D4; P8 = D5 XOR D6 XOR D7","3.3"),eq("P0 = D1 XOR ... XOR D7 XOR P1 XOR P2 XOR P4 XOR P8","3.4"),p("SEC-DED requires an appropriate decoder. The encoder alone does not correct errors."),
          h1("Chapter 4 - Baseline Reproduction"),p("The Hamming (11,7) network uses twelve XOR2 cells. The resulting CMOS and FS-GDI counts of 144 and 72 match the baseline paper's structural counts. Numerical matching is not expected because the original model deck, load, input pattern, and exact measurement definitions were not released."),nominal_table("H117"),
          h1("Chapter 5 - Extended Hamming (12,7)"),p("The extended architecture adds a ten-XOR overall-parity path to the twelve-XOR Hamming network. The same Boolean graph is retained across logic styles to preserve comparison fairness."),
          h1("Chapter 6 - Proposed Hybrid FS-GDI/CMOS Design"),architecture_diagram(),p("Figure 6.1. Original block diagram of Hybrid-B." ,"AcademicCaption"),p("Hybrid-A restores every XOR output. Hybrid-B restores only the externally observed parity outputs. Hybrid-B contains 152 transistors, compared with 264 for CMOS, 132 for FS-GDI, and 220 for Hybrid-A."),
          h1("Chapter 7 - LTspice Simulation Methodology"),table([["Parameter","Value"],["Simulator","LTspice 26.0.2"],["Model","PTM 65-nm bulk CMOS beta"],["Nominal","1.2 V, 27 C, 125 MHz, 10 fF"],["Sizing","NMOS 120/65 nm; PMOS 240/65 nm"],["Delay","50%-to-50%; D1-to-P0 for EH127"],["Power","AVG(-V(VDD)*I(VSUP))"],["Sweeps","VDD, temperature, load, and frequency independently"]],[45*mm,115*mm]),
          h1("Chapter 8 - Results and Robustness Analysis"),p(f"Exhaustive verification covered {functional['data_words_tested']} data words, {functional['single_bit_error_cases_tested']} single-bit cases, and {functional['double_bit_error_cases_tested']} double-bit cases. All passed."),nominal_table("EH127")]
    for name, caption in [("eh127_nominal_power.png","Figure 8.1. Nominal average power."),("eh127_nominal_delay.png","Figure 8.2. Nominal D1-to-P0 delay."),("eh127_nominal_pdp.png","Figure 8.3. Nominal PDP."),("eh127_pdp_vs_vdd.png","Figure 8.4. PDP versus supply voltage.")]:
        body += [Image(str(ROOT/"figures"/name), width=155*mm, height=91*mm),p(caption,"AcademicCaption")]
    hb=nominal["EH127:HYBRID_B"]; cm=nominal["EH127:CMOS"]; fs=nominal["EH127:FSGDI"]
    body += [h1("Chapter 9 - Discussion"),p(f"At nominal conditions, Hybrid-B uses {hb['pavg']*1e6:.3f} uW and has a D1-to-P0 delay of {hb['tpd']*1e12:.3f} ps. Relative to CMOS, this is {((cm['pavg']-hb['pavg'])/cm['pavg']*100):.2f}% lower power and {((cm['tpd']-hb['tpd'])/cm['tpd']*100):.2f}% lower delay. FS-GDI uses only {fs['pavg']*1e6:.3f} uW but has a longer P0 path. Restoration therefore buys speed and external drive at an energy cost."),p("Three 1 fF simulations are rejected because overshoot exceeds the configured supply-bound tolerance. All retained architectures tested in the 10 fF voltage sweep satisfy the study criteria at 0.6 V; lower voltages were not tested, so no boundary below 0.6 V is claimed."),
             h1("Chapter 10 - Conclusions and Future Work"),p("Hybrid-B is supported as a speed-oriented selective-restoration candidate, not as a universal energy optimum. FS-GDI remains preferable when simulated energy and PDP dominate. Future work requires supervisor review of the reconstructed cell, an independent foundry-PDK or second-simulator cross-check, post-layout parasitics, and a lower-voltage boundary search."),
             h1("References")]+[p(f"[{i}] {escape(ref)}") for i,ref in enumerate(REFERENCES,1)]+[h1("Appendix A - Reproducibility"),p("The repository preserves 121 circuit files, their LTspice logs, the PTM model, experiment manifest, Python processing scripts, Verilog reference models, processed datasets, and figures."),h1("Appendix B - Status"),p("This document is a WORKING THESIS DRAFT. University front matter, institutional metadata, supervisor approval, and any required disclosure statements remain pending.")]
    return body


def literature_story():
    rows=list(csv.DictReader((ROOT/"literature/survey/survey.csv").open(encoding="utf-8")))
    body=[h1("Survey Methodology"),p("The survey prioritizes 2021-2026 publications while retaining foundational Hamming, GDI, and FS-GDI sources. Publisher pages and DOI records are used to verify existence. Unavailable metadata are marked rather than inferred."),h1("Comparative Survey")]
    compact=[["Reference","Year","Circuit","Logic","Contribution","Limitation"]]
    for r in rows: compact.append([r["Reference"],r["Year"],r["Circuit/Code"],r["Logic Style"],r["Main Contribution"],r["Limitation"]])
    body += [table(compact,[31*mm,12*mm,28*mm,25*mm,48*mm,48*mm],6.2),h1("Identified Gap")]+md_flowables(ROOT/"docs/research-gap.md")[1:]
    return body


def results_story():
    hb=nominal["EH127:HYBRID_B"]; cm=nominal["EH127:CMOS"]; fs=nominal["EH127:FSGDI"]
    return [h1("Experimental Conditions")]+md_flowables(ROOT/"docs/simulation-methodology.md")[1:]+[h1("Nominal Comparison"),nominal_table("EH127"),p(f"Hybrid-B reduces nominal power by {(cm['pavg']-hb['pavg'])/cm['pavg']*100:.2f}%, delay by {(cm['tpd']-hb['tpd'])/cm['tpd']*100:.2f}%, PDP by {(cm['pdp']-hb['pdp'])/cm['pdp']*100:.2f}%, and transistor count by {(cm['transistor_count']-hb['transistor_count'])/cm['transistor_count']*100:.2f}% relative to CMOS."),p(f"FS-GDI has the lowest nominal power ({fs['pavg']*1e6:.3f} uW) and PDP ({fs['pdp']*1e15:.3f} fJ), but its P0 path is slower than CMOS."),h1("Robustness and Rejected Points"),p("The one-factor sweeps cover 0.6-1.2 V, -20 to 85 C, 1-20 fF, and 25-200 MHz. Three 1 fF points are rejected by the automated supply-bound check because of overshoot. No failed point is replaced or hidden.")]


def simple_story(title, sources, additions=None):
    story=[]
    for source in sources: story += md_flowables(ROOT/source)
    if additions: story += additions
    return story


def main():
    docs=[
      (ROOT/"pdf/thesis/Howida_Gharib_Extended_Hamming_MSc_Thesis.pdf","Design and Robustness Analysis of a Low-Power Hybrid FS-GDI/CMOS Extended Hamming (12,7) Encoder","Working Thesis Draft",thesis_story(),True),
      (ROOT/"pdf/research/Literature_Survey.pdf","Literature Survey","Research Document",literature_story(),True),
      (ROOT/"pdf/research/Research_Gap_and_Contribution.pdf","Research Gap and Contribution","Research Document",simple_story("",["docs/research-gap.md"],[h1("Evidence Required"),p("The contribution is supported by traceable netlists, actual LTspice logs, automated calculations, controlled sweeps, and retained rejected points. A foundry cross-check remains future work.")]),True),
      (ROOT/"pdf/research/Original_Paper_Audit.pdf","Original Paper Audit","Research Audit",simple_story("",["docs/original-paper-audit.md"]),True),
      (ROOT/"pdf/research/Proposed_Hybrid_Extended_Hamming_Encoder.pdf","Proposed Hybrid Extended Hamming (12,7) Encoder","Design Document",[h1("Code Architecture"),p("The design adds P0 to Hamming (11,7) and evaluates two restoration placements."),eq("P0 = D1 XOR ... XOR D7 XOR P1 XOR P2 XOR P4 XOR P8","1"),architecture_diagram(),p("Figure 1. Original Hybrid-B architecture.","AcademicCaption"),h1("Circuit-Level Alternatives"),p("CMOS uses 12-transistor XOR cells. The reconstructed FS-GDI cell uses six transistors. Hybrid-A adds local CMOS restoration to every cell. Hybrid-B adds non-inverting restoration only at parity outputs."),h1("Measured Trade-off"),nominal_table("EH127"),p("Hybrid-B is selected for speed; FS-GDI remains the energy optimum under the tested nominal condition.")],True),
      (ROOT/"pdf/technical/LTspice_Simulation_Methodology.pdf","LTspice Simulation Methodology","Technical Document",simple_story("",["docs/simulation-methodology.md","docs/measurement-definitions.md"],[h1("Official Software Source"),p("LTspice 26.0.2 was obtained from https://www.analog.com/en/resources/design-tools-and-calculators/ltspice-simulator.html. The project uses .param, .temp, .tran, and .meas directives in retained circuit files.")]),True),
      (ROOT/"pdf/technical/65nm_Device_Model_Documentation.pdf","65-nm Device Model Documentation","Technical Document",simple_story("",["docs/model-documentation.md"]),True),
      (ROOT/"pdf/technical/Simulation_Measurement_Definitions.pdf","Simulation Measurement Definitions","Technical Document",simple_story("",["docs/measurement-definitions.md"]),True),
      (ROOT/"pdf/technical/Software_and_Research_Tools.pdf","Software and Research Tools","Technical Document",[h1("Tools Actually Used"),table([["Tool","Version","Role","Official source"],["LTspice","26.0.2","Transistor-level simulation","analog.com/ltspice"],["Python","Installed 3.x runtime","Verification, parsing, PDF, Word, and figure generation","python.org"],["Git","Installed client","Version control","git-scm.com"],["Icarus Verilog","12.x","SystemVerilog reference simulation","bleyer.org/icarus"],["GitHub","Public repository service","Public dissemination","github.com"],["PTM","65-nm beta model","Predictive transistor model","mec.umn.edu/ptm"],["ReportLab","Installed Python library","Academic PDF generation","reportlab.com"],["python-docx","Installed Python library","Editable Word document generation","python-docx.readthedocs.io"],["Pillow","Installed Python library","Research figures","python-pillow.org"]],[32*mm,25*mm,55*mm,62*mm]),h1("Reproducibility Notes"),p("Versions and commands are documented in the repository. Verilog source is included and can be simulated with Icarus Verilog for the reference encoder testbench.")],True),
      (ROOT/"pdf/reproducibility/GitHub_Public_Repository_Guide.pdf","GitHub Public Repository Guide","Repository Document",[h1("Public Repository"),p("https://github.com/printcode1000-lgtm/Extended-Hamming"),h1("Access"),p("Clone with: git clone https://github.com/printcode1000-lgtm/Extended-Hamming.git. Use the main branch. LTspice files are under ltspice/, scripts under scripts/, validated data under data/processed/, PDFs under pdf/, and the website under docs-site/ after publication preparation."),h1("Citation Status"),p("No DOI has been assigned. Cite the researcher, repository title, URL, version, and access date until a formal archival identifier exists.")],True),
      (ROOT/"pdf/reproducibility/Reproducibility_Guide.pdf","Reproducibility Guide","Research Reproducibility",[h1("Procedure"),p("1. Clone the main branch. 2. Install LTspice 26.0.2 and Python 3. 3. Confirm models/65nm_bulk.pm. 4. Run scripts/verify_secded.py. 5. Run scripts/build_ltspice.py. 6. Run scripts/run_ltspice.py with the LTspice path. 7. Run results_pipeline.py and summarize_results.py. 8. Run generate_figures.py, generate_academic_pdfs.py, and generate_academic_word.py. 9. Run link_check.py and the secret scan. 10. Open the website through a local server under /Extended-Hamming/."),h1("Validation"),p("A result is accepted only if required .meas values exist, PDP recalculates correctly, and signal bounds pass the configured checks. Rejected raw logs remain retained.")],True),
      (ROOT/"pdf/simulation/Simulation_Results_and_Analysis.pdf","Simulation Results and Analysis","Simulation Report",results_story(),True),
      (ROOT/"pdf/simulation/SEC-DED_Verification_Documentation.pdf","SEC-DED Verification Documentation","Verification Report",[h1("Reference Model"),p("The Python model uses positions 1, 2, 4, and 8 for Hamming parity and position 12 for overall even parity."),h1("Exhaustive Results"),table([["Test","Cases","Result"],["Data words",functional["data_words_tested"],"Pass"],["Single-bit errors",functional["single_bit_error_cases_tested"],"Corrected"],["Double-bit errors",functional["double_bit_error_cases_tested"],"Detected"]],[60*mm,40*mm,55*mm]),h1("Scope"),p("This verifies encoder/decoder logic. It does not claim a transistor-level decoder implementation.")],True),
      (ROOT/"pdf/technical/Project_Technical_Architecture.pdf","Project Technical Architecture","Technical Document",[h1("Research Flow"),p("Verified literature -> audited equations -> Python and Verilog references -> generated LTspice netlists -> raw logs -> validated CSV/JSON -> figures -> website and PDFs."),h1("Repository Layers"),table([["Layer","Location","Purpose"],["Theory and audit","literature/, docs/","Sources, gap, and decisions"],["Simulation","ltspice/, models/","Circuit and device sources"],["Verification","scripts/, verification/","Functional and data validation"],["Evidence","data/, results/, figures/","Raw-to-processed provenance"],["Publication","thesis/, pdf/","Public academic outputs"]],[35*mm,48*mm,78*mm]),h1("Provenance"),p("Each measurement is connected through an experiment ID to a circuit, model, condition set, raw log, processed row, and final table or figure.")],True),
      (ROOT/"pdf/publication/Publication_Plan_and_Manuscript_Outline.pdf","Publication Plan and Manuscript Outline","Publication Material",simple_story("",["docs/publication-plan.md","docs/paper-outline.md"]),True),
    ]
    for path,title,label,story,toc in docs:
        build(path,title,label,story,toc=toc)
        print(path.relative_to(ROOT))


if __name__ == "__main__": main()
