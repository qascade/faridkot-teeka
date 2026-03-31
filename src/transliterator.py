"""
transliterator.py — Gurmukhi Unicode → Devanagari Unicode transliteration
"""

import re

# ---------------------------------------------------------------------------
# Step 1 preprocessing: addak before nukta-consonants
# ੱ + C + ਼ → C + ਼ + ੍ + C + ਼  (double the full nukta-consonant)
# ---------------------------------------------------------------------------
_ADDAK_NUKTA = [
    ('\u0A71\u0A38\u0A3C', '\u0A38\u0A3C\u0A4D\u0A38\u0A3C'),  # ੱਸ਼ → ਸ਼੍ਸ਼
    ('\u0A71\u0A1C\u0A3C', '\u0A1C\u0A3C\u0A4D\u0A1C\u0A3C'),  # ੱਜ਼ → ਜ਼੍ਜ਼
    ('\u0A71\u0A17\u0A3C', '\u0A17\u0A3C\u0A4D\u0A17\u0A3C'),  # ੱਗ਼ → ਗ਼੍ਗ਼
]

# ---------------------------------------------------------------------------
# Step 2: addak + plain Gurmukhi consonant → consonant + ੍ + consonant
# ---------------------------------------------------------------------------
_GK_CONS = r'[\u0A15-\u0A28\u0A2A-\u0A30\u0A32\u0A35\u0A38\u0A39\u0A5C]'
_ADDAK_RE = re.compile(r'\u0A71(' + _GK_CONS + r')')

# ---------------------------------------------------------------------------
# Step 3: multi-codepoint substitutions
# ---------------------------------------------------------------------------
_MULTI_SUBS = [
    ('\u0A38\u0A3C', '\u0936'),          # ਸ਼ → श
    ('\u0A5C', '\u0921\u093C'),          # ੜ  → ड़
]

# ---------------------------------------------------------------------------
# Step 4: single-codepoint translation table
# ---------------------------------------------------------------------------
_TABLE = str.maketrans({
    # Independent vowels (offset 0x100)
    0x0A05: 0x0905,  # ਅ → अ
    0x0A06: 0x0906,  # ਆ → आ
    0x0A07: 0x0907,  # ਇ → इ
    0x0A08: 0x0908,  # ਈ → ई
    0x0A09: 0x0909,  # ਉ → उ
    0x0A0A: 0x090A,  # ਊ → ऊ
    0x0A0F: 0x090F,  # ਏ → ए
    0x0A10: 0x0910,  # ਐ → ऐ
    0x0A13: 0x0913,  # ਓ → ओ
    0x0A14: 0x0914,  # ਔ → औ
    # Vowel matras (offset 0x100)
    0x0A3E: 0x093E,  0x0A3F: 0x093F,  0x0A40: 0x0940,
    0x0A41: 0x0941,  0x0A42: 0x0942,  0x0A47: 0x0947,
    0x0A48: 0x0948,  0x0A4B: 0x094B,  0x0A4C: 0x094C,
    # Diacritics
    0x0A02: 0x0902,  # ਂ bindi → anusvara
    0x0A03: 0x0903,  # ਃ visarga
    0x0A3C: 0x093C,  # ਼ nukta
    0x0A4D: 0x094D,  # ੍ virama
    0x0A70: 0x0902,  # ੰ tippi → anusvara (Devanagari has no tippi)
    0x0A71: None,    # ੱ addak → delete (already expanded above)
    # Consonants (offset 0x100)
    0x0A15: 0x0915,  0x0A16: 0x0916,  0x0A17: 0x0917,  0x0A18: 0x0918,
    0x0A19: 0x0919,  0x0A1A: 0x091A,  0x0A1B: 0x091B,  0x0A1C: 0x091C,
    0x0A1D: 0x091D,  0x0A1E: 0x091E,  0x0A1F: 0x091F,  0x0A20: 0x0920,
    0x0A21: 0x0921,  0x0A22: 0x0922,  0x0A23: 0x0923,  0x0A24: 0x0924,
    0x0A25: 0x0925,  0x0A26: 0x0926,  0x0A27: 0x0927,  0x0A28: 0x0928,
    0x0A2A: 0x092A,  0x0A2B: 0x092B,  0x0A2C: 0x092C,  0x0A2D: 0x092D,
    0x0A2E: 0x092E,  0x0A2F: 0x092F,  0x0A30: 0x0930,  0x0A32: 0x0932,
    0x0A35: 0x0935,  0x0A38: 0x0938,  0x0A39: 0x0939,
    # ੜ (0A5C) handled in pre-substitutions → ड़
    # Digits (offset 0x100)
    0x0A66: 0x0966,  0x0A67: 0x0967,  0x0A68: 0x0968,  0x0A69: 0x0969,
    0x0A6A: 0x096A,  0x0A6B: 0x096B,  0x0A6C: 0x096C,  0x0A6D: 0x096D,
    0x0A6E: 0x096E,  0x0A6F: 0x096F,
    # Carrier fallbacks (converter.py resolves these; defensive only)
    0x0A72: 0x0907,  # ੲ iri carrier → इ
    0x0A73: 0x0909,  # ੳ ura carrier → उ
    # ੴ (0A74) ik onkar → NOT in table (pass-through, no Devanagari equivalent)
})


def transliterate(text: str) -> str:
    """Transliterate Gurmukhi Unicode text to Devanagari Unicode."""
    # Step 1: addak before nukta-consonants
    for src, dst in _ADDAK_NUKTA:
        text = text.replace(src, dst)

    # Step 2: addak + plain consonant → doubled consonant with virama
    text = _ADDAK_RE.sub(lambda m: m.group(1) + '\u0A4D' + m.group(1), text)

    # Step 3: multi-codepoint substitutions
    for src, dst in _MULTI_SUBS:
        text = text.replace(src, dst)

    # Step 4: single-codepoint translation
    text = text.translate(_TABLE)

    return text
