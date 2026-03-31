#!/usr/bin/env python3
"""
transliterate_docx.py — Convert Gurmukhi text in Word documents to Devanagari.

Usage:
    python3 src/transliterate_docx.py input.docx [output.docx]

If output.docx is not specified, the output filename will be
input_devanagari.docx (in the same directory as input.docx).
"""

import sys
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from transliterator import transliterate


def has_gurmukhi_codepoints(text: str) -> bool:
    """Check if text contains Gurmukhi codepoints (U+0A00–U+0A7F)."""
    return any('\u0A00' <= c <= '\u0A7F' for c in text)


def set_run_font(run, font_name: str) -> None:
    """Set font on a run to the specified font name."""
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    rFonts.set(qn('w:ascii'), font_name)
    rFonts.set(qn('w:hAnsi'), font_name)
    rFonts.set(qn('w:cs'), font_name)


def set_run_language(run, lang_code: str) -> None:
    """Set language on a run (w:lang attribute)."""
    rPr = run._element.get_or_add_rPr()
    lang = rPr.find(qn('w:lang'))
    if lang is None:
        lang = OxmlElement('w:lang')
        rPr.append(lang)
    lang.set(qn('w:val'), lang_code)


def transliterate_docx(input_path: str, output_path: str = None) -> None:
    """
    Transliterate Gurmukhi text to Devanagari in a Word document.

    Args:
        input_path: Path to input .docx file
        output_path: Path to output .docx file (default: input_devanagari.docx)
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if output_path is None:
        stem = input_path.stem
        output_path = input_path.parent / f"{stem}_devanagari.docx"
    else:
        output_path = Path(output_path)

    # Load document
    doc = Document(str(input_path))

    # Process every paragraph and run
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            if not run.text:
                continue

            # Check if font is 'Gurmukhi MN' or contains Gurmukhi codepoints
            is_gurmukhi_font = False
            rPr = run._element.rPr
            if rPr is not None:
                rFonts = rPr.find(qn('w:rFonts'))
                if rFonts is not None:
                    ascii_font = rFonts.get(qn('w:ascii'), '')
                    h_ansi = rFonts.get(qn('w:hAnsi'), '')
                    cs = rFonts.get(qn('w:cs'), '')
                    if any(f == 'Gurmukhi MN' for f in [ascii_font, h_ansi, cs]):
                        is_gurmukhi_font = True

            has_gurmukhi = has_gurmukhi_codepoints(run.text)

            if is_gurmukhi_font or has_gurmukhi:
                # Transliterate
                run.text = transliterate(run.text)
                # Change font to Devanagari MT
                set_run_font(run, 'Devanagari MT')
                # Change language from pa-IN to hi-IN
                set_run_language(run, 'hi-IN')

    # Save document
    doc.save(str(output_path))
    print(f"✓ Transliterated document saved to: {output_path}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 transliterate_docx.py input.docx [output.docx]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        transliterate_docx(input_path, output_path)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
