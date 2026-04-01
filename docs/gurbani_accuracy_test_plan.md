# Plan: Gurbani Accuracy Testing + ੴ Spacing Fix

## Context
Two tasks:
1. **Bug fix** — The `ੴ` (Ik Onkar) spacing fix was in `converter.py::convert()` before the PDF-normalization refactor. It was never carried over to `normalize_pdf_text()` and is now missing. Current docx output has `ੴਸਤਿ` (jammed together). Fix is one line.
2. **Gurbani accuracy test** — Compare every Gurbani line in the generated docx against the authoritative Unicode GGS from GurbaniDB API (`http://api.sikher.com/page/{n}`). Results flagged and stored as JSON.

---

## Phase 1: Fix ੴ spacing bug

**File:** `src/extractor.py` → `normalize_pdf_text()`

Add one line at the end (this runs on Unicode output *after* `convert()`, so it targets U+0A74 not the raw SriAngad byte):

```python
import re
text = re.sub('\u0A74(?=[^ ])', '\u0A74 ', text)
```

Wait — `normalize_pdf_text()` runs on raw SriAngad text *before* `convert()`. The ੴ fix was originally applied *after* conversion (to the Unicode output). So the fix belongs after the `convert()` call in `extract_page()`:

```python
# In extractor.py extract_page(), line ~181:
unicode_text = convert(normalize_pdf_text(raw)) if _is_sriangad(font_name) else raw
# Add after:
if _is_sriangad(font_name):
    unicode_text = re.sub('\u0A74(?=[^ ])', '\u0A74 ', unicode_text)
```

Or, cleaner: add a second pass to `normalize_pdf_text()` but document that it also accepts Unicode output. Since it's a simple regex on a Unicode codepoint this is safe either way. The cleaner option is to rename/extend `normalize_pdf_text` to also handle this, or apply it inline in `extract_page`.

**Recommended:** Apply it inline right after `convert()` in `extract_page()` since `normalize_pdf_text` is documented as operating on raw SriAngad text.

**Also:** Update `test_converter.py` — add a test that `convert(normalize_pdf_text('\xa1sat'))` produces `'ੴ ਸਤਿ'` (with space). Wait, `\xa1` is the SriAngad byte for ੴ — but the test is tricky since the fix is now in `extract_page`, not in `convert()`. Just add a quick integration note.

---

## Phase 2: One-time GGS Reference Download

**New file:** `src/download_ggs_reference.py`

Downloads all 1430 GGS pages from `http://api.sikher.com/page/{n}`, saves to `data/ggs_reference.json`.

### Format of `data/ggs_reference.json`
```json
{
  "1": ["ੴ ਸਤਿ ਨਾਮੁ ਕਰਤਾ ਪੁਰਖੁ ...", "ਸੋਚੈ ਸੋਚਿ ਨ ਹੋਵਈ ..."],
  "2": ["...", "..."],
  ...
  "1430": [...]
}
```

Each entry is a list of lines in page order. Text taken from the `text` field of API response.

### Download strategy
- Parallel fetch with `concurrent.futures.ThreadPoolExecutor(max_workers=10)`
- Progress bar via simple print (every 100 pages)
- Retry once on failure
- Skip if `data/ggs_reference.json` already exists (idempotent)
- Total: ~1430 requests × ~100ms ≈ 15 seconds with 10 workers

```bash
python3 src/download_ggs_reference.py          # downloads to data/ggs_reference.json
python3 src/download_ggs_reference.py --force  # re-download even if cached
```

---

## Phase 3: Accuracy Test Script

**New file:** `src/test_gurbani_accuracy.py`

### Docx parsing strategy
Iterate all paragraphs, track state:
```
current_pdf_page = None   # from '─── Page N ───' markers (color #999999, size 8pt)
current_ggs_page = None   # from 'ਪੰਨਾ ੧੨੩' paragraphs (color #C0006A)
```

**ggs_ref page number extraction:**
- Color: `RGBColor(0xC0, 0x00, 0x6A)`
- Text format: `ਪੰਨਾ ੧` (Gurmukhi numeral)
- Gurmukhi digits: `੦੧੨੩੪੫੬੭੮੯` → `0123456789`
- Parse: `int(text.replace('ਪੰਨਾ', '').strip().translate(GURMUKHI_DIGITS_TABLE))`

**Gurbani paragraph detection:**
- `run.font.color.rgb == RGBColor(0x00, 0x00, 0x7F)` and `run.font.bold == True`

### Line matching strategy

**Problem:** Docx gurbani paragraphs can span multiple API lines (multiple tuks joined together in one paragraph due to PDF text box merging).

**Solution:** Split docx gurbani text by dandas, match each tuk individually.

```python
import re
def split_into_tuks(text: str) -> list[str]:
    # Split on danda (।) or double-danda (॥), keeping the delimiter
    parts = re.split(r'(?<=[।॥])', text)
    return [p.strip() for p in parts if p.strip()]
```

### Normalization for comparison
```python
import unicodedata

def normalize_for_compare(text: str) -> str:
    text = unicodedata.normalize('NFC', text)
    text = text.replace('।', '').replace('॥', '')  # strip dandas
    text = ' '.join(text.split())                   # normalize spaces
    return text.strip()
```

### Matching
For each tuk extracted from docx:
1. If `current_ggs_page` is set: look up `ggs_reference[str(current_ggs_page)]`
2. Find best match using `difflib.SequenceMatcher`
3. If `ratio >= 0.90` → matched
4. If `ratio < 0.90` → flag as discrepancy
5. If no `current_ggs_page` set → skip (can't determine which GGS page)

### Output: `data/gurbani_discrepancies.json`
```json
{
  "tested_file": "fareedkot_teeka_final.docx",
  "tested_at": "2026-04-01T...",
  "ggs_reference": "data/ggs_reference.json",
  "total_tuks_tested": 1240,
  "matched": 1198,
  "skipped": 12,
  "accuracy": 0.967,
  "discrepancies": [
    {
      "pdf_page": 340,
      "ggs_page": 12,
      "extracted_tuk": "ਮਨਮੁਖ ਅੰਧ ਨ ਬੁਝਹਿ",
      "best_match": "ਮਨਮੁਖ ਅੰਧੁ ਨ ਬੁਝਹਿ",
      "similarity": 0.92,
      "status": "low_confidence"
    }
  ]
}
```

### CLI usage
```bash
python3 gurbani_accuracy_test/test_gurbani_accuracy.py fareedkot_teeka_final.docx
python3 gurbani_accuracy_test/test_gurbani_accuracy.py fareedkot_teeka_final.docx --output gurbani_accuracy_test/data/my_results.json
python3 gurbani_accuracy_test/test_gurbani_accuracy.py fareedkot_teeka_final.docx --threshold 0.85
```

---

## Critical files
- `src/extractor.py` — add ੴ spacing fix inline after `convert()` call (~line 181)
- `gurbani_accuracy_test/download_ggs_reference.py` — new: one-time GGS downloader
- `gurbani_accuracy_test/test_gurbani_accuracy.py` — new: accuracy test CLI
- `gurbani_accuracy_test/data/` — cached reference + results JSONs; add `gurbani_accuracy_test/data/*.json` to `.gitignore`

## Dependencies
No new pip packages needed — `difflib`, `concurrent.futures`, `urllib.request` are all stdlib. `requests` is not in requirements.txt; use `urllib.request` for the download script.

## Verification
```bash
# Fix ੴ bug first
python3 src/test_converter.py   # all 159 tests still pass

# Download GGS reference (one-time, ~15 seconds)
python3 gurbani_accuracy_test/download_ggs_reference.py

# Run accuracy test
python3 gurbani_accuracy_test/test_gurbani_accuracy.py fareedkot_teeka_final.docx

# Check results
cat gurbani_accuracy_test/data/gurbani_discrepancies.json | python3 -m json.tool | head -50
```
