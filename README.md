# Fareedkot Teeka 

> ੴ ਵਾਹਿਗੁਰੂ ਜੀ ਕੀ ਫ਼ਤਹਿ॥
> ਸ੍ਰੀ ਭਗੌਤੀ ਜੀ ਸਹਾਇ॥

Converts the 4,300-page `Fareedkot_Teeka.pdf` from the legacy SriAngad font encoding to proper Unicode Gurmukhi, producing formatted `.docx` files for review. As well as doing programatic transliteration of the Teeka to Devanagri for reach to wider audience. 

## About Fareedkot Teeka

The **Faridkot Wala Teeka** is a classical exegesis of the Sri Guru Granth Sahib in Braj Bhasha composed by a team of scholars of the Nirmala Sect. It represents the first formal, systematic attempt to interpret Gurbani in this comprehensive manner, and it became the ideal prototype for all future Teeka scholarship in this field.

### Historical Context

Teekas (commentaries) on the Guru Granth Sahib have existed since the scripture's compilation, but the first formal Teeka aligned with traditional Sikh scriptural interpretation was written by **Sant Giani Badan Singh Ji** of Dera Sekhwan at the request and encouragement of **Maharaja Bikram Singh** of Faridkot. This monumental work took six and a half years to complete and was finished in **1883**.

The Teeka was reviewed by a committee appointed by Mahant Shamer Singh of Patna. After incorporating their comments, the first edition was published (and funded) by **Maharaja Balvir Singh** of Faridkot in **1906**, printed by the **Wazir Hind Press** (established by Bhai Vir Singh) in Amritsar. A second edition was subsequently published by Maharaja Harinder Singh of Faridkot in **1928**. Due to the patronage of the Rulers of Faridkot State, it became known as the "**Faridkoti Teeka**."

### Scholarly Legacy

During the same period, **Pandit Tara Singh Narotam** — a contemporary of Giani Badan Singh — also began composing a Teeka, but passed away before completing it (finishing only up to Basant Rag). His incomplete draft was later lost when borrowed by others who never returned it. Only the Sri Rag section of his Teeka survives, possessed by very few researchers and scholars today.

The Faridkoti Teeka became the foundational reference work for Gurbani scholarship and interpretation, influencing subsequent scholarly work in Sikh scriptural studies.

### Why Digitization Matters

For generations, this work has been accessed only in its original printed form — a rare and fragile manuscript available in limited copies. The digitization and modernization of this text is critical for:

1. **Preservation** — Protect this irreplaceable scholarly work from deterioration and loss
2. **Accessibility** — Make the Teeka available to Sikhs worldwide, especially younger generations and diaspora communities
3. **Searchability** — Enable digital search, study, and reference capabilities for researchers and Kathakars (discourse leaders)
4. **Multilingual Reach** — Provide Hindi/Devanagari versions for Hindi-speaking Sikhs and scholars who can benefit from this wisdom

**Reference:** Gurmat Sahit Vivechan (Punjabi, published by Punjab Languages Department) — An authoritative compilation of 25 essays by leading scholars on the history of Gurmat literature, providing comprehensive context for understanding the Faridkoti Teeka within Sikh intellectual tradition.

---

## The Conversion Challenge

The PDF uses **SriAngad** — a legacy pre-Unicode Gurmukhi font (from pre-2000) that maps Gurmukhi glyphs to Latin character codes (WinAnsiEncoding). It has no ToUnicode map, so:
- Copy-paste from the PDF yields Latin gibberish (e.g., `manmuKh` instead of ਮਨਮੁਖ)
- The text cannot be indexed, searched, or properly displayed on modern devices
- Standard OCR and digitization tools fail completely

This project **reverse-engineers the complete SriAngad encoding** and converts the text to proper Unicode, enabling the Teeka to be used with modern software and devices.

See `ANALYSIS.md` for the full character mapping reference.

---

## ⚠️ Disclaimer

**Generated files (`output/*.docx`) are programmatically converted from PDF and may contain:**
- Spelling mistakes or clerical errors from the source document
- Character mapping errors (rare, but possible edge cases)
- Formatting inconsistencies where the PDF structure was ambiguous

**A comprehensive manual proofreading process is planned** to verify and correct all text. This conversion is a first pass to enable digital distribution and review — it is NOT a final, verified edition.

For questions about specific passages or suspected errors, please refer to the original PDF at the noted page number.

**Found an error?** Please report it:
- **Email:** sksingh2211@gmail.com (include page number and description of the error)
- **GitHub:** Open an issue at https://github.com/qascade/faridkot-teeka/issues

Your feedback helps improve the accuracy of the conversion for future readers.

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

### Transliterate Gurmukhi to Devanagari

Convert an existing Gurmukhi `.docx` file to Devanagari script (for Hindi-reading audiences):

```bash
python3 src/transliterate_docx.py input.docx [output.docx]
```

This auto-detects Gurmukhi text, transliterates to Devanagari Unicode, and changes the font to Devanagari MT. Language tag is updated from `pa-IN` to `hi-IN`.

Example:
```bash
python3 src/transliterate_docx.py output/pages_338-347.docx
# → Saves to: output/pages_338-347_devanagari.docx
```

### Run tests

```bash
python3 src/test_converter.py        # 159 character mapping tests
python3 src/test_transliterator.py   # 81 transliteration tests
```

All tests must pass before any changes to `src/converter.py` or `src/transliterator.py`.

---

## File Overview

| File | Purpose |
|------|---------|
| `src/converter.py` | Core SriAngad → Unicode conversion logic |
| `src/extractor.py` | Extracts text + color/font metadata from PDF using pdfminer |
| `src/generate.py` | CLI — main entry point for generating `.docx` files |
| `src/docx_generator.py` | Renders `Element` objects into a `.docx` |
| `src/transliterator.py` | Gurmukhi Unicode → Devanagari Unicode transliteration engine |
| `src/transliterate_docx.py` | CLI for batch Word document transliteration |
| `src/test_converter.py` | 159 unit tests covering every character mapping |
| `src/test_transliterator.py` | 81 unit tests for transliteration (all passing) |
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
