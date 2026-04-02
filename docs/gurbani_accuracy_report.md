# Gurbani Accuracy Test Report

**File:** `fareedkot_teeka_0_1_0.docx`  
**Date:** 2026-04-02  
**Threshold:** 0.85  
**Reference:** GurbaniDB API (api.sikher.com) — 1430 pages, 60,403 lines

---

## Summary

| Metric | Count | % |
|--------|-------|---|
| Total tuks tested | 60726 | |
| High confidence (>= 0.95) | 57590 | 94.8% |
| Low confidence (0.85-0.95) | 2466 | 4.1% |
| Mismatched (< 0.85) | 668 | 1.1% |
| Skipped | 2 | |
| **Overall accuracy** | **60056** | **98.9%** |

---

## Per-Section Accuracy (GGS Page Ranges)

| GGS Pages | Accuracy | Visual |
|-----------|----------|--------|
| 1-100 | 99.1% | `███████████████████░` |
| 101-200 | 97.8% | `███████████████████░` |
| 201-300 | 98.3% | `███████████████████░` |
| 301-400 | 98.9% | `███████████████████░` |
| 401-500 | 98.0% | `███████████████████░` |
| 501-600 | 99.4% | `███████████████████░` |
| 601-700 | 98.9% | `███████████████████░` |
| 701-800 | 98.7% | `███████████████████░` |
| 801-900 | 98.8% | `███████████████████░` |
| 901-1000 | 99.6% | `███████████████████░` |
| 1001-1100 | 99.3% | `███████████████████░` |
| 1101-1200 | 98.8% | `███████████████████░` |
| 1201-1300 | 99.7% | `███████████████████░` |
| 1301-1400 | 99.4% | `███████████████████░` |
| 1401-1430 | 99.9% | `███████████████████░` |

---

## Known Bugs Found

### Bug 1: Å (U+00C5) not converted — 76 instances (FIXED in v0.1.1)

The SriAngad character `Å` was missing from the converter's character map. It should map to `੍ਯ` (subscript Ya).

| Extracted | Expected |
|-----------|----------|
| `ਵਖÅਾਨਾ` | `ਵਖ੍ਯਾਨਾ` |
| `ਸੁਧਾਖÅਰ` | `ਸੁਧਾਖ੍ਯਰ` |
| `ਗÅਾਨ` | `ਗ੍ਯਾਨ` |

**Status:** Fixed in converter.py. Requires docx regeneration.

### Bug 2: Missing subscript Ha (੍ਹ) — 113 instances (OPEN)

The virama (੍) appears but the following ਹ is lost during PDF extraction. The converter mapping `H → ੍ਹ` is correct — the issue is upstream in the PDF text extraction layer.

| Extracted | Expected |
|-----------|----------|
| `ਸੰਨ੍ੀ` | `ਸੰਨ੍ਹੀ` |
| `ਗਾਵਨਿ੍` | `ਗਾਵਨ੍ਹਿ` |
| `ਤਿਨ੍` | `ਤਿਨ੍ਹ` |
| `ਤੁਮ੍ਾਰੇ` | `ਤੁਮ੍ਹਾਰੇ` |

**Status:** Open — needs PDF extraction investigation.

### Bug 3: Matra ordering ੁੋ — 15 instances (OPEN)

Aunkar (ੁ) and hora (ੋ) matras appear in wrong Unicode order.

| Extracted | Expected |
|-----------|----------|
| `ਗੁੋਪਾਲ` | `ਗੋੁਪਾਲ` |
| `ਸੁੋਹੇਲਾ` | `ਸੋੁਹੇਲਾ` |

**Status:** Open — needs matra reordering fix in converter.py.

---

## Filtered Out (not counted as discrepancies)

- **Pauri/stanza numbers** (`੧॥`, `੨॥`, etc.) — structural markers, not gurbani lines
- **Standalone "ਰਹਾਉ ॥"** — refrain markers separated during PDF extraction

---

## Top Discrepancies (lowest similarity)

### GGS Page 875 (PDF Page 2655) — sim: 0.16

- **Extracted:** `ਜੋੜੁ ॥`
- **Expected:** `ਕੋਈ ਪੜਤਾ ਸਹਸਾਕਿਰਤਾ ਕੋਈ ਪੜੈ ਪੁਰਾਨਾ ॥`
- **Confidence:** mismatch

### GGS Page 594 (PDF Page 1838) — sim: 0.19

- **Extracted:** `ਸੁਧੁ`
- **Expected:** `ਜਾ ਕੀ ਨਦਰਿ ਸਦਾ ਸੁਖੁ ਹੋਇ ॥ ਰਹਾਉ ॥`
- **Confidence:** mismatch

### GGS Page 91 (PDF Page 337) — sim: 0.20

- **Extracted:** `ਸੁਧੁ`
- **Expected:** `ੴ ਸਤਿਗੁਰ ਪ੍ਰਸਾਦਿ ॥`
- **Confidence:** mismatch

### GGS Page 317 (PDF Page 1040) — sim: 0.20

- **Extracted:** `ਸੁਧੁ ॥`
- **Expected:** `ੴ ਸਤਿਗੁਰ ਪ੍ਰਸਾਦਿ ॥`
- **Confidence:** mismatch

### GGS Page 855 (PDF Page 2588) — sim: 0.20

- **Extracted:** `ਸੁਧੁ ॥`
- **Expected:** `ਅਬਹਿ ਨ ਮਾਤਾ ਸੁ ਕਬਹੁ ਨ ਮਾਤਾ ॥`
- **Confidence:** mismatch

### GGS Page 1094 (PDF Page 3305) — sim: 0.20

- **Extracted:** `ਸੁਧੁ ॥`
- **Expected:** `ੴ ਸਤਿਗੁਰ ਪ੍ਰਸਾਦਿ ॥`
- **Confidence:** mismatch

### GGS Page 1291 (PDF Page 3884) — sim: 0.20

- **Extracted:** `ਸੁਧੁ ॥`
- **Expected:** `ੴ ਸਤਿਗੁਰ ਪ੍ਰਸਾਦਿ ॥`
- **Confidence:** mismatch

### GGS Page 1318 (PDF Page 3954) — sim: 0.20

- **Extracted:** `ਸੁਧੁ ॥`
- **Expected:** `ੴ ਸਤਿਗੁਰ ਪ੍ਰਸਾਦਿ ॥`
- **Confidence:** mismatch

### GGS Page 487 (PDF Page 1562) — sim: 0.21

- **Extracted:** `ਮਹਲਾ ੫ ॥`
- **Expected:** `ਸੀਆਲੇ ਸੋਹੰਦੀਆਂ ਪਿਰ ਗਲਿ ਬਾਹੜੀਆਂ ॥੬॥`
- **Confidence:** mismatch

### GGS Page 524 (PDF Page 1662) — sim: 0.22

- **Extracted:** `ਸੁਧੁ`
- **Expected:** `ਕਹਤ ਕਬੀਰ ਸੁਨਹੁ ਮੇਰੀ ਮਾਈ ॥`
- **Confidence:** mismatch

### GGS Page 1251 (PDF Page 3770) — sim: 0.22

- **Extracted:** `ਸੁਧੁ ॥`
- **Expected:** `ਕਾਲ ਜਾਲ ਕੀ ਸੁਧਿ ਨਹੀ ਲਹੈ ॥`
- **Confidence:** mismatch

### GGS Page 595 (PDF Page 1839) — sim: 0.24

- **Extracted:** `ਪ੍ਰਸਾਦਿ ॥`
- **Expected:** `ਜਗ ਸਿਉ ਝੂਠ ਪ੍ਰੀਤਿ ਮਨੁ ਬੇਧਿਆ ਜਨ ਸਿਉ ਵਾਦੁ ਰਚਾਈ ॥`
- **Confidence:** mismatch

### GGS Page 859 (PDF Page 2602) — sim: 0.24

- **Extracted:** `ਪ੍ਰਸਾਦਿ ॥`
- **Expected:** `ਮੇਰੇ ਮਨ ਆਸਾ ਕਰਿ ਜਗਦੀਸ ਗੁਸਾਈ ॥`
- **Confidence:** mismatch

### GGS Page 1294 (PDF Page 3892) — sim: 0.24

- **Extracted:** `ਪ੍ਰਸਾਦਿ ॥`
- **Expected:** `ਮੇਰਾ ਮਨੁ ਸਾਧ ਜਨਾਂ ਮਿਲਿ ਹਰਿਆ ॥`
- **Confidence:** mismatch

### GGS Page 1385 (PDF Page 4167) — sim: 0.24

- **Extracted:** `ਪ੍ਰਸਾਦਿ ॥`
- **Expected:** `ਬ੍ਰਹਮਾਦਿਕ ਸਨਕਾਦਿ ਸੇਖ ਗੁਣ ਅੰਤੁ ਨ ਪਾਏ ॥`
- **Confidence:** mismatch

### GGS Page 528 (PDF Page 1673) — sim: 0.24

- **Extracted:** `ਛਕਾ ੧`
- **Expected:** `ਗੁਰ ਪ੍ਰਸਾਦਿ ਕਾਹੂ ਜਾਤੇ ॥੧॥ ਰਹਾਉ ॥`
- **Confidence:** mismatch

### GGS Page 966 (PDF Page 2936) — sim: 0.24

- **Extracted:** `ਸੁਧੁ ॥`
- **Expected:** `ਜਾਂ ਸੁਧੋਸੁ ਤਾਂ ਲਹਣਾ ਟਿਕਿਓਨੁ ॥੪॥`
- **Confidence:** mismatch

### GGS Page 1106 (PDF Page 3343) — sim: 0.24

- **Extracted:** `ਮਾਰੂ ॥`
- **Expected:** `ਬਰਸੈ ਅੰਮ੍ਰਿਤ ਧਾਰ ਬੂੰਦ ਸੁਹਾਵਣੀ ॥`
- **Confidence:** mismatch

### GGS Page 1319 (PDF Page 3956) — sim: 0.24

- **Extracted:** `ਪ੍ਰਸਾਦਿ ॥`
- **Expected:** `ਹਮਰੀ ਚਿਤਵਨੀ ਹਰਿ ਪ੍ਰਭੁ ਜਾਨੈ ॥`
- **Confidence:** mismatch

### GGS Page 150 (PDF Page 521) — sim: 0.25

- **Extracted:** `ਸੁਧੁ`
- **Expected:** `ਹੰਸੁ ਹੇਤੁ ਆਸਾ ਅਸਮਾਨੁ ॥`
- **Confidence:** mismatch
