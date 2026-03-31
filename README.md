# Fareedkot Teeka — SriAngad → Unicode Converter

Converts the 4,300-page `Fareedkot_Teeka.pdf` from the legacy SriAngad font encoding to proper Unicode Gurmukhi, producing formatted `.docx` files for review.

## Background

The PDF uses **SriAngad** — a legacy pre-Unicode Gurmukhi font that maps Gurmukhi glyphs to Latin character codes (WinAnsiEncoding). It has no ToUnicode map, so copy-paste yields Latin gibberish. This tool reverse-engineers the complete encoding and converts the text.

See `ANALYSIS.md` for the full character mapping reference.

---

## Setup

```bash
pip install -r requirements.txt
```

**Requirements:** `pdfminer.six`, `python-docx`

**Font:** Uses `Gurmukhi MN` (macOS system font). On other systems, edit `_GURMUKHI_FONT` in `src/generate.py`.

---

## Usage

### Generate pages to `.docx`

Run from the project root (so the PDF and `output/` folder are found correctly):

```bash
# 10 pages starting at page 338
python3 src/generate.py -s 338 -e 347

# Custom output path
python3 src/generate.py -s 1 -e 50 --output output/first_50.docx

# With page breaks between pages
python3 src/generate.py -s 338 -e 347 --page-break

# Only Gurbani and Braj (skip refs/annotations)
python3 src/generate.py -s 338 -e 347 --types gurbani braj

# No page number separators
python3 src/generate.py -s 338 -e 347 --no-page-markers

# Quiet (no per-page progress)
python3 src/generate.py -s 338 -e 347 -q
```

Output goes to `output/pages_{start}-{end}.docx` by default.

### Run tests

```bash
python3 src/test_converter.py
```

All 159 tests must pass before any changes to `src/converter.py`.

---

## File Overview

| File | Purpose |
|------|---------|
| `src/converter.py` | Core SriAngad → Unicode conversion logic |
| `src/extractor.py` | Extracts text + color/font metadata from PDF using pdfminer |
| `src/generate.py` | CLI — main entry point for generating `.docx` files |
| `src/docx_generator.py` | Renders `Element` objects into a `.docx` |
| `src/test_converter.py` | 159 unit tests covering every character mapping |
| `requirements.txt` | Python dependencies |
| `docs/ANALYSIS.md` | Complete SriAngad → Unicode character mapping reference |
| `docs/doc_generation_instructions.md` | Page structure rules + known common errors |
| `docs/sample_mappings.md` | Ground-truth Gurbani lines used to verify mappings |
| `docs/` | Reference PDFs (font key maps) |

---

## Text Type Classification

Text is classified by color (from PDF graphicstate) and font size:

| Type | Color in PDF | Style in output |
|------|-------------|-----------------|
| `gurbani` | Deep blue `(0, 0, 0.502)` | Blue bold centered, 16pt |
| `braj` | Red `(0.502, 0, 0)` or black ≥10pt | Dark red justified, 12pt |
| `braj_sub` | Bright blue `(0, 0, 1.0)` | Blue justified, 11pt |
| `ggs_ref` | Magenta `(1, 0, 1)` | Pink, 11pt |
| `annotation` | Black < 10pt | Gray, 9pt |
| `latin` | Times New Roman font | Black, 10pt |

---

## Key Encoding Rules

1. **Sihari reordering** — `i` is coded BEFORE its consonant in SriAngad; must be placed AFTER in Unicode. With subscript clusters: `i` + base + subscript → base + subscript + ਿ
2. **Carrier + matra look-ahead** — `a`/`e`/`A` followed by a matra produce precomposed independent vowels (e.g. `aw`→ਆ, `ey`→ਏ, `Au`→ਉ)
3. **Ø+z sequence** — together produce ੱ (addak); Ø alone has no output
4. **Matra ordering** — tippi/bindi typed before dulainkar/aunkar in source are swapped to correct Unicode order

---

## Known Issues / Manual Fixes Needed

- Shabad header lines (ੴ, ਸਿਰੀਰਾਗੁ, ਘਰਿ marker, first tuk) come from a single PDF text box and merge into one paragraph — split manually
- Page markers (`─── Page N ───`) are included for reference; remove after verification
- `ਅਗ੍ਯਾਨ` vs `ਅਯਾਨ` — some words have variant spellings across pages; verify against original
