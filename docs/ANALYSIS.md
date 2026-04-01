# Fareedkot Teeka PDF - Font & Encoding Analysis

## Document Overview

| Property | Value |
|----------|-------|
| **Title** | Faridkot Wala Teeka (ਫਰੀਦਕੋਟ ਵਾਲਾ ਟੀਕਾ) |
| **Created** | July 11, 2006 |
| **Author** | Baljinder Singh |
| **Pages** | 4,300 |
| **Source Tool** | Acrobat PDFMaker 6.0 for Word → Distiller 6.0 |

---

## Root Cause: The "Gibberish" Problem

**The SriAngad font is a legacy pre-Unicode Gurmukhi font** (Kulbir S. Thind, 1997). It assigns Gurmukhi glyphs to Latin character codes using WinAnsiEncoding (8-bit Extended ASCII). The PDF **lacks a ToUnicode mapping table**, so copy-paste yields raw Latin bytes instead of Gurmukhi.

With the complete mapping table below, extracted text can be post-processed into proper Unicode.

---

## Fonts Used

| Font Name | Type | Encoding | Embedded | Use |
|-----------|------|----------|----------|-----|
| **EAKGKK+SriAngad** | TrueType | WinAnsiEncoding | Yes | Gurmukhi/Punjabi text |
| TimesNewRomanPSMT | TrueType | WinAnsiEncoding | No | Roman/Latin text |
| TimesNewRomanPS-ItalicMT | TrueType | WinAnsiEncoding | No | Italic text |

---

## Complete SriAngad → Unicode Mapping Table

### Vowel Matras (diacritical marks)

| SriAngad | Unicode | Gurmukhi | Name | Notes |
|----------|---------|----------|------|-------|
| `w` | U+0A3E | ਾ | aa matra | |
| `W` | U+0A3E+U+0A02 | ਾਂ | aa matra + bindi | nasalized — `iqRSnW`→ਤ੍ਰਿਸ਼ਨਾਂ, `ijnHW`→ਜਿਨ੍ਹਾਂ |
| `i` | U+0A3F | ਿ | sihari | **Pre-base encoding**: coded BEFORE its consonant in SriAngad, must be reordered AFTER in Unicode |
| `I` | U+0A40 | ੀ | ii matra (long) | |
| `u` | U+0A41 | ੁ | u matra (short) | |
| `U` | U+0A42 | ੂ | uu matra (long) | |
| `y` | U+0A47 | ੇ | e matra | |
| `Y` | U+0A48 | ੈ | ai matra | |
| `o` | U+0A4B | ੋ | o matra | |
| `O` | U+0A4C | ੌ | au matra | e.g. `aOr`→ਔਰ |
| `M` | U+0A70 | ੰ | Tippi | nasal |
| `x` | U+0A02 | ਂ | Anusvaar | light nasal |
| `z` | U+0A71 | ੱ | Addak | consonant doubling |

### Independent Vowels (carriers)

| SriAngad | Unicode | Gurmukhi | Name | Notes |
|----------|---------|----------|------|-------|
| `a` | U+0A05 | ਅ | Mukta | inherent vowel carrier |
| `A` | U+0A73 | ੳ | Ura carrier | combines with matra: A+u=ੳੁ=ਉ, A+U=ੳੂ=ਊ — `Auir`→ਉਰਿ |
| `e` | U+0A72 | ੲ | Iri carrier | combines with matra: e+y=ੲੇ=ਏ, e+I=ੲੀ=ਈ; also i+e→ਇ — `eynI`→ਏਨੀ |
| `E` | U+0A13 | ਓ | O-kara | standalone long-O vowel — `EaMkwru`→ਓਅੰਕਾਰ, `Ehu`→ਓਹੁ |

### Consonants

| SriAngad | Unicode | Gurmukhi | Name | SriAngad | Unicode | Gurmukhi | Name |
|----------|---------|----------|------|----------|---------|----------|------|
| `k` | U+0A15 | ਕ | Ka | `n` | U+0A28 | ਨ | Na |
| `K` | U+0A16 | ਖ | Kha | `N` | U+0A23 | ਣ | Nnna |
| `g` | U+0A17 | ਗ | Ga | `p` | U+0A2A | ਪ | Pa |
| `G` | U+0A18 | ਘ | Gha | `P` | U+0A2B | ਫ | Pha |
| `c` | U+0A1A | ਚ | Cha | `b` | U+0A2C | ਬ | Ba |
| `C` | U+0A1B | ਛ | Chha | `B` | U+0A2D | ਭ | Bha |
| `j` | U+0A1C | ਜ | Ja | `m` | U+0A2E | ਮ | Ma |
| `J` | U+0A1D | ਝ | Jha | `r` | U+0A30 | ਰ | Ra |
| `t` | U+0A1F | ਟ | Tainka | `l` | U+0A32 | ਲ | La |
| `T` | U+0A20 | ਠ | Ttha | `v` | U+0A35 | ਵ | Va |
| `f` | U+0A21 | ਡ | Dda | `V` | U+0A5C | ੜ | Rra |
| `d` | U+0A26 | ਦ | Da | `h` | U+0A39 | ਹ | Ha |
| `D` | U+0A27 | ਧ | Dha | `s` | U+0A38 | ਸ | Sa |
| `F` | U+0A22 | ਢ | Ddha | `S` | U+0A38+U+0A3C | ਸ਼ | Sha |
| `q` | U+0A24 | ਤ | Ta | `X` | U+0A2F | ਯ | Ya |
| `Q` | U+0A25 | ਥ | Tha | `Z` | U+0A1C+U+0A3C | ਜ਼ | Za |
| `ø` | U+0A1E | ਞ | Nya (rare) | `ß` | U+0A17+U+0A3C | ਗ਼ | Gha+Nukta |
| `ù` | U+0A19 | ਙ | Nga (rare) | | | | |

### Subscript / Cluster Forms

| SriAngad | Unicode | Gurmukhi | Notes |
|----------|---------|----------|-------|
| `R` | U+0A4D+U+0A30 | ੍ਰ | Subscript Ra |
| `H` | U+0A4D+U+0A39 | ੍ਹ | Subscript Ha — `ijnHW`→ਜਿਨ੍ਹਾਂ, `qrHW`→ਤਰ੍ਹਾਂ |
| `Ã` | U+0A4D+U+0A1F | ੍ਟ | Subscript Tainka — `aiDsÃwn`→ਅਧਿਸ੍ਟਾਨ |
| `Í` | U+0A4D+U+0A35 | ੍ਵ | Subscript Va — `sÍwmI`→ਸ੍ਵਾਮੀ, `eIsÍr`→ਈਸ੍ਵਰ |
| `Î` | U+0A4D+U+0A2F | ੍ਯ | Subscript Ya — `awgÎw`→ਆਗ੍ਯਾ, `XogÎ`→ਯੋਗ੍ਯ |
| `Ä` | U+0A4D | ੍ | Trailing virama — `TginÄ`→ਠਗਿਨ੍ |

### Cluster-Context Matra Variants

| SriAngad | Unicode | Gurmukhi | Notes |
|----------|---------|----------|-------|
| `ü` | U+0A41 | ੁ | u matra after subscript Ra — `sRüqI`→ਸ੍ਰੁਤੀ |
| `Á` | U+0A42 | ੂ | uu matra after subscript Ra — `DRÁ`→ਧ੍ਰੂ |
| `û` | U+0A70 | ੰ | Tippi variant — `anûdu`→ਅਨੰਦੁ, `iqlûg`→ਤਿਲੰਗ |
| `À` | U+0A02 | ਂ | Anusvaar variant — same as `x` |

### Special / Compound Characters

| SriAngad | Unicode | Gurmukhi | Notes |
|----------|---------|----------|-------|
| `L` | U+0A28+U+0A42+U+0A70 | ਨੂੰ | Dative postposition as single byte — `mYL`→ਮੈਨੂੰ, `qYL`→ਤੈਨੂੰ |
| `¡` | U+0A74 | ੴ | Ik Onkar — `¡siqgur`→ੴ ਸਤਿਗੁਰ |
| `Ú` | U+0A03 | ਃ | Visarga — `mÚ`→ਮਃ |
| `Øz` | U+0A71 | ੱ | Two-byte Addak — `AuØzqr`→ਉੱਤਰ (Ø is silent prefix, z gives ੱ) |
| `æ` | — | — | Visual artifact, no Gurmukhi equivalent |

---

## Multi-Byte Encoding Rules

1. **`Øz` pair**: When `Ø` (ANSI 216) precedes `z`, together they = ੱ. `Ø` has no output of its own.
2. **`L`**: Single byte encoding for the full postposition ਨੂੰ (3 Unicode chars).
3. **`¡`**: Single byte for ੴ (Ik Onkar symbol).
4. **`S`**: Sa (U+0A38) + Nukta (U+0A3C) = ਸ਼.
5. **`Z`**: Ja (U+0A1C) + Nukta (U+0A3C) = ਜ਼.
6. **`ß`**: Ga (U+0A17) + Nukta (U+0A3C) = ਗ਼.
7. **Subscript forms** (`R`, `H`, `Ã`, `Í`, `Î`): Each encodes virama (U+0A4D) + consonant as a single byte.
8. **`Ä`**: Standalone trailing virama — appears at word/syllable boundary.

---

## Common Output Errors (Known Fixes)

These patterns appear in the source due to SriAngad typing conventions and are corrected automatically in `converter.py`:

| Wrong output | Correct | Cause | Fix |
|---|---|---|---|
| ਬੰੂਦ | ਬੂੰਦ | Tippi typed before dulainkar in source (`bMUd`) | Swap nasal after vowel matra |
| ਹੰੂ | ਹੂੰ | Same pattern (`hMU`) | Same fix |

**Rule**: Nasalization marks (ੰ tippi, ਂ bindi) must always follow vowel matras (ੂ dulainkar, ੁ aunkar). Converter swaps them if they arrive in wrong order.

---

## Page Structure

Every page follows this structure (header/footer stripped automatically):

```
[Header]  ਫਰੀਦਕੋਟ ਵਾਲਾ ਟੀਕਾ           ← stripped
[Latin]   page number                    ← kept as reference marker
[Gurbani] ੴ / shabad lines              ← deep blue, bold, centered
[Braj]    commentary paragraphs         ← dark red, justified
[ggs_ref] ਪੰਨਾ ੯੨ style markers         ← pink
[Footer]  ਗੁਰੂ ਅੰਗਦ ਦੇਵ ਜੀ...           ← stripped
```

---

## Research Notes

Confirmed character mappings from corpus investigation:

- `Î` — subscript Ya, produces half-form in `lzKNÎu`→ਲੱਖਣ੍ਯੁ, `XogÎ`→ਯੋਗ੍ਯ
- `À` — same output as `x` (ਂ bindi); variant used in specific contexts
- `Øz` — equivalent to ੱ (addak); `Ø` has no independent output
- `Q` → ਥ (confirmed), `C` → ਛ (confirmed)
- `f` → ਡ (e.g. `ipMfu`→ਪਿੰਡੂ), `d` → ਦ (e.g. `dosqI`→ਦੋਸਤੀ) — distinct, do not confuse
- `D` → ਧ (e.g. `ihrdy`→ਹਿਰਦੇ), `F` → ਢ (e.g. `gMFu`→ਗੰਢੁ) — distinct, do not confuse
- `ù` → ਙ Nga (rare): `isMiùaw`→ਸਿੰਙਿਆ, `ùaw`→ਙਆ (pages 341+)
- `ø` → ਞ Nya (rare): `suMøI`→ਸੁੰਞੀ (page 86), `vMøw`→ਵੰਞਾ (page 103)
- `æ` → stripped (visual artifact, no Gurmukhi meaning): `CUæt`→ਛੂਟ, `kuætl`
- `Ã` → ੍ਟ subscript Tainka: appears as subscript at foot of consonant, like ੍ਹ in ਜਿਨ੍ਹਾਂ
