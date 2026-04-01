"""
extractor.py — Extract structured text elements from Fareedkot_Teeka.pdf.

Text type classification is driven primarily by color (from graphicstate),
with font size as a tiebreaker for black SriAngad text.

Color legend (ICCBased RGB, confirmed from PDF probe):
  (0.0,   0.0,   ~0.5) deep blue  → gurbani
  (~0.5,  0.0,   0.0)  red        → braj
  (0.0,   0.0,   ~1.0) bright blue→ braj_sub  (sub-commentary / Braj notes)
  DeviceGray 0.0       black      → header / annotation / footnote (by size)
  other ICCBased                  → ggs_ref  (GGS page-ref markers, pink)
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTChar, LTTextBox, LTTextLine

from converter import convert


@dataclass
class Element:
    raw_text: str       # SriAngad Latin bytes as extracted from PDF
    unicode_text: str   # After convert()
    text_type: str      # see classify() below
    font_size: float
    page_num: int       # 1-based


# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------

def _is_sriangad(font_name: str) -> bool:
    return 'SriAngad' in font_name or 'EAKGKK' in font_name


def _color_label(ncs, fc) -> str:
    """Return a coarse color label from a graphicstate color space + value."""
    if ncs.ncomponents == 1:
        # DeviceGray: 0.0 = black, 1.0 = white
        return 'black'

    if ncs.ncomponents == 3:
        r, g, b = fc
        if b >= 0.4 and r < 0.15 and g < 0.15:
            return 'blue_deep' if b < 0.8 else 'blue_bright'
        if r >= 0.4 and g < 0.15 and b < 0.15:
            return 'red'
        if r >= 0.4 and b >= 0.4 and g < 0.15:
            return 'magenta'  # (1.0, 0.0, 1.0) — GGS page-ref markers (pMnw NNN)
        return 'other'

    return 'unknown'


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def classify(font_name: str, size: float, color: str) -> str:
    """Map (font, size, color) → text type string."""
    if not _is_sriangad(font_name):
        return 'latin'

    if color == 'blue_deep':
        return 'gurbani'
    if color == 'red':
        return 'braj'
    if color == 'blue_bright':
        return 'braj_sub'
    if color in ('magenta', 'other'):
        return 'ggs_ref'

    # Black SriAngad — use size to distinguish
    if size >= 10:
        return 'braj'        # black braj/commentary text
    return 'annotation'      # footnotes, small labels


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

def _extract_footnote_number(text: str) -> tuple[str | None, str]:
    """Extract leading footnote number from text.

    Returns (footnote_number_or_None, remaining_text).
    Examples:
      "1 some text" → ("1", "some text")
      "123 text" → ("123", "text")
      "no number here" → (None, "no number here")
    """
    match = re.match(r'^(\d+)\s+(.*)$', text.strip())
    if match:
        return match.group(1), match.group(2)
    return None, text


def _dominant_color(line: LTTextLine) -> tuple[str, object, float]:
    """Return (color_label, ncs, size) from the first LTChar in the line."""
    for ch in line:
        if not isinstance(ch, LTChar):
            continue
        gs = ch.graphicstate
        return _color_label(gs.ncs, gs.ncolor), gs.ncs, ch.size
    return 'unknown', None, 0.0


# Known header/footer strings to strip (Unicode, after conversion)
_STRIP_TEXTS: frozenset[str] = frozenset([
    'ਫਰੀਦਕੋਟ ਵਾਲਾ ਟੀਕਾ',
    'ਗੁਰੂ ਅੰਗਦ ਦੇਵ ਜੀ ਦੇ ੫੦੦ ਸਾਲਾ ਅਵਤਾਰ ਪੁਰਬ ਨੂੰ ਸਮਰਪਿਤ',
])


def postprocess(elements: list[Element]) -> list[Element]:
    """Strip header/footer and merge consecutive same-type/same-size elements across boxes."""
    filtered = [el for el in elements if el.unicode_text.strip() not in _STRIP_TEXTS]

    merged: list[Element] = []
    for el in filtered:
        same = (
            merged
            and merged[-1].text_type == el.text_type
            and abs(merged[-1].font_size - el.font_size) < 0.5
            # Don't merge across gurbani type — each Gurbani section is intentional
            and el.text_type != 'gurbani'
        )
        if same:
            prev = merged[-1]
            merged[-1] = Element(
                raw_text=prev.raw_text + ' ' + el.raw_text,
                unicode_text=(prev.unicode_text.rstrip() + ' ' + el.unicode_text.strip()).strip(),
                text_type=prev.text_type,
                font_size=prev.font_size,
                page_num=prev.page_num,
            )
        else:
            merged.append(el)
    return merged


def extract_page(pdf_path: str, page_num: int) -> list[Element]:
    """Extract all text elements from a single page (1-based page_num).

    Lines within the same LTTextBox and of the same text_type are merged into
    one Element — this correctly handles both paragraph wrapping and multi-tuk
    Gurbani blocks, while keeping logically separate boxes as separate elements.
    """
    elements: list[Element] = []
    page_index = page_num - 1  # pdfminer uses 0-based page_numbers

    for page_layout in extract_pages(pdf_path, page_numbers=[page_index]):
        for block in page_layout:
            if not isinstance(block, LTTextBox):
                continue

            # Collect lines from this box, merging consecutive same-type runs
            box_elements: list[Element] = []
            for line in block:
                if not isinstance(line, LTTextLine):
                    continue

                raw = line.get_text().strip()
                if not raw:
                    continue

                color, _ncs, size = _dominant_color(line)

                # font_name from first LTChar
                font_name = next(
                    (ch.fontname for ch in line if isinstance(ch, LTChar)),
                    ''
                )

                # Check if this line starts with a footnote number
                footnote_num, rest_text = _extract_footnote_number(raw)

                # Process footnote number (if present) as a separate element
                if footnote_num:
                    # Footnote numbers are always annotation (gray), regardless of size
                    fn_unicode = footnote_num  # numbers don't need conversion
                    box_elements.append(Element(
                        raw_text=footnote_num,
                        unicode_text=fn_unicode,
                        text_type='annotation',
                        font_size=size,
                        page_num=page_num,
                    ))
                    # Continue with the rest of the text
                    raw = rest_text

                # Classify and process the remaining text (or full line if no footnote number)
                text_type = classify(font_name, size, color)
                unicode_text = convert(raw) if _is_sriangad(font_name) else raw

                if not raw.strip():
                    # Just a footnote number, already added
                    continue

                # Merge with previous line in this box if same type AND same font size
                prev_same = (
                    box_elements
                    and box_elements[-1].text_type == text_type
                    and abs(box_elements[-1].font_size - size) < 0.5
                )
                if prev_same:
                    prev = box_elements[-1]
                    box_elements[-1] = Element(
                        raw_text=prev.raw_text + ' ' + raw,
                        unicode_text=(prev.unicode_text.rstrip() + ' ' + unicode_text.strip()).strip(),
                        text_type=text_type,
                        font_size=prev.font_size,
                        page_num=page_num,
                    )
                else:
                    box_elements.append(Element(
                        raw_text=raw,
                        unicode_text=unicode_text,
                        text_type=text_type,
                        font_size=size,
                        page_num=page_num,
                    ))

            elements.extend(box_elements)

    return elements


# ---------------------------------------------------------------------------
# CLI: python3 extractor.py  →  print page 8 elements
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    import sys

    pdf_path = 'Fareedkot_Teeka.pdf'
    page = int(sys.argv[1]) if len(sys.argv) > 1 else 8

    elements = extract_page(pdf_path, page)
    for el in elements:
        print(f"[{el.text_type:<12}] {el.font_size:4.1f}pt | {el.unicode_text}")
