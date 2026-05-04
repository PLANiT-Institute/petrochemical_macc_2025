#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parent.parent
MANUSCRIPT_DIR = ROOT / "01_manuscript"
SRC_MD = MANUSCRIPT_DIR / "manuscript_draft.md"
CLEAN_MD = MANUSCRIPT_DIR / "manuscript_final_clean.md"
OUT_TEX = MANUSCRIPT_DIR / "manuscript_final.tex"
OUT_PDF = MANUSCRIPT_DIR / "manuscript_final.pdf"


def clean_markdown(text: str) -> str:
    # Remove internal traceability tags like [C01] or `[C01]`
    text = re.sub(r"(?:\s*`?\[C\d+\]`?)+", "", text)
    # Remove internal traceability note line
    text = re.sub(r"^\*\*Traceability Note:\*\*.*$", "", text, flags=re.MULTILINE)
    # Remove internal claim-tag appendix from final output
    text = re.sub(r"^## Claim Tags Used in This Manuscript[\s\S]*$", "", text, flags=re.MULTILINE)
    # Cleanup artifacts after tag stripping
    text = re.sub(r"\s*``\s*", " ", text)
    text = re.sub(r"\s+([,.;:])", r"\1", text)
    # Normalize excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def md_inline_to_html(text: str) -> str:
    # Minimal markdown inline handling for reportlab Paragraph
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r"<font face='Courier'>\1</font>", text)
    return text


def build_pdf(md_text: str) -> None:
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        fontSize=18,
        leading=22,
        spaceAfter=12,
    )
    h1_style = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=14, leading=18, spaceBefore=10, spaceAfter=6)
    h2_style = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=12, leading=15, spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=10.5, leading=15)
    bullet_style = ParagraphStyle("Bullet", parent=styles["BodyText"], leftIndent=12, bulletIndent=0, fontSize=10.5, leading=14)
    caption_style = ParagraphStyle("Caption", parent=styles["Italic"], fontSize=9, leading=12, alignment=1)

    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=A4,
        leftMargin=2.2 * cm,
        rightMargin=2.2 * cm,
        topMargin=2.2 * cm,
        bottomMargin=2.2 * cm,
        title="Infrastructure Bottlenecks in Petrochemical Decarbonization",
        author="Jinsu Park",
    )

    story = []
    lines = md_text.splitlines()
    paragraph_buf = []

    def flush_paragraph() -> None:
        nonlocal paragraph_buf
        if paragraph_buf:
            text = " ".join(s.strip() for s in paragraph_buf).strip()
            if text:
                story.append(Paragraph(md_inline_to_html(text), body_style))
                story.append(Spacer(1, 0.12 * cm))
            paragraph_buf = []

    img_pat = re.compile(r"!\[(.*?)\]\((.*?)\)")

    for raw in lines:
        line = raw.rstrip()

        if not line.strip():
            flush_paragraph()
            continue

        if line.startswith("# "):
            flush_paragraph()
            story.append(Paragraph(md_inline_to_html(line[2:].strip()), title_style))
            story.append(Spacer(1, 0.2 * cm))
            continue

        if line.startswith("## "):
            flush_paragraph()
            heading = line[3:].strip()
            if heading.lower().startswith("claim tags used"):
                # skip internal appendix in final PDF
                break
            story.append(Paragraph(md_inline_to_html(heading), h1_style))
            continue

        if line.startswith("### "):
            flush_paragraph()
            story.append(Paragraph(md_inline_to_html(line[4:].strip()), h2_style))
            continue

        m = img_pat.match(line.strip())
        if m:
            flush_paragraph()
            alt = m.group(1).strip()
            img_rel = m.group(2).strip()
            img_path = (SRC_MD.parent / img_rel).resolve()
            if img_path.exists():
                img = Image(str(img_path))
                img._restrictSize(16.5 * cm, 10.5 * cm)
                story.append(img)
                story.append(Spacer(1, 0.1 * cm))
                if alt:
                    story.append(Paragraph(md_inline_to_html(alt), caption_style))
                    story.append(Spacer(1, 0.2 * cm))
            continue

        if line.startswith("- "):
            flush_paragraph()
            story.append(Paragraph(md_inline_to_html("• " + line[2:].strip()), bullet_style))
            story.append(Spacer(1, 0.05 * cm))
            continue

        # Skip horizontal rule markers
        if line.strip() == "---":
            flush_paragraph()
            story.append(Spacer(1, 0.2 * cm))
            continue

        paragraph_buf.append(line)

    flush_paragraph()
    doc.build(story)


def main() -> None:
    md_text = SRC_MD.read_text(encoding="utf-8")
    clean = clean_markdown(md_text)
    CLEAN_MD.write_text(clean, encoding="utf-8")

    # Build TeX from cleaned markdown
    import subprocess

    subprocess.run(
        [
            "pandoc",
            str(CLEAN_MD),
            "-f",
            "gfm",
            "-t",
            "latex",
            "-s",
            "-o",
            str(OUT_TEX),
        ],
        check=True,
    )

    # Prefer TeX->PDF with tectonic; fallback to reportlab if TeX build is unavailable.
    try:
        subprocess.run(
            [
                "tectonic",
                "--keep-logs",
                "--keep-intermediates",
                OUT_TEX.name,
            ],
            cwd=str(MANUSCRIPT_DIR),
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        build_pdf(clean)


if __name__ == "__main__":
    main()
