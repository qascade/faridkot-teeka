"""
converter.py — SriAngad font (legacy pre-Unicode Gurmukhi) → Unicode Gurmukhi

Key encoding rules:
1. Sihari (ਿ) is pre-base in SriAngad: coded BEFORE its consonant.
   Unicode requires it AFTER. _process_char() handles this reordering.
   With subscript cluster: i + base + subscript → base + subscript + ਿ
   Special: i + e → ਇ (U+0A07, independent short-i vowel)

2. Ø + z together → ੱ (addak); Ø alone → no output.

3. Vowel carriers use look-ahead — the carrier alone has no output; the carrier
   plus the following matra together form the correct precomposed independent vowel:
     a (mukta) + w → ਆ    a + O → ਔ    a + Y → ਐ    a + W → ਆਂ
     e (iri)   + y → ਏ    e + I → ਈ
     A (ura)   + u → ਉ    A + U → ਊ    A + o → ਓ
   Standalone a/e/A (not followed by a matra) → ਅ / ੲ / ੳ respectively.

4. E = ਓ (U+0A13) — direct standalone long-O vowel (no look-ahead needed).
"""

import re

# ---------------------------------------------------------------------------
# Mapping: SriAngad byte → Unicode string
# 'i', 'Ø', 'a', 'e', 'A' are handled in _process_char (special look-ahead).
# ---------------------------------------------------------------------------
CHAR_MAP: dict[str, str] = {
    # --- Vowel matras ---
    'w': '\u0A3E',              # ਾ  aa matra
    'W': '\u0A3E\u0A02',        # ਾਂ aa + bindi (nasalized)
    # 'i' handled separately — sihari reordering
    'I': '\u0A40',              # ੀ  ii matra
    'u': '\u0A41',              # ੁ  u matra
    'U': '\u0A42',              # ੂ  uu matra
    'y': '\u0A47',              # ੇ  e matra
    'Y': '\u0A48',              # ੈ  ai matra
    'o': '\u0A4B',              # ੋ  o matra
    'O': '\u0A4C',              # ੌ  au matra
    'M': '\u0A70',              # ੰ  tippi
    'x': '\u0A02',              # ਂ  bindi
    'z': '\u0A71',              # ੱ  addak
    # Cluster-context matra variants
    '\xfb': '\u0A70',           # û (251) tippi variant  = M
    '\xfc': '\u0A41',           # ü (252) aunkar variant = u  (after subscript Ra)
    '\xc1': '\u0A42',           # Á (193) dulainkar variant = U (after subscript Ra)
    '\xc0': '\u0A02',           # À (192) bindi variant  = x

    # --- Independent vowel (E only; a/e/A handled in _process_char) ---
    'E': '\u0A13',              # ਓ  standalone long-O

    # --- Consonants ---
    'k': '\u0A15',  'K': '\u0A16',  'g': '\u0A17',  'G': '\u0A18',
    'c': '\u0A1A',  'C': '\u0A1B',  'j': '\u0A1C',  'J': '\u0A1D',
    't': '\u0A1F',  'T': '\u0A20',  'f': '\u0A21',  'd': '\u0A26',
    'D': '\u0A27',  'F': '\u0A22',  'q': '\u0A24',  'Q': '\u0A25',
    'n': '\u0A28',  'N': '\u0A23',  'p': '\u0A2A',  'P': '\u0A2B',
    'b': '\u0A2C',  'B': '\u0A2D',  'm': '\u0A2E',  'r': '\u0A30',
    'l': '\u0A32',  'v': '\u0A35',  'V': '\u0A5C',  'h': '\u0A39',
    's': '\u0A38',  'X': '\u0A2F',

    # --- Multi-char output consonants ---
    'S': '\u0A38\u0A3C',        # ਸ਼  sha  (sa + nukta)
    'Z': '\u0A1C\u0A3C',        # ਜ਼  za   (ja + nukta)
    '\xdf': '\u0A17\u0A3C',     # ß (223) gha + nukta
    '\xf8': '\u0A1E',           # ø (248) nya  (rare)
    '\xf9': '\u0A19',           # ù (249) nga  (rare)

    # --- Subscript / cluster forms ---
    'R': '\u0A4D\u0A30',        # ੍ਰ  subscript Ra
    'H': '\u0A4D\u0A39',        # ੍ਹ  subscript Ha
    '\xc3': '\u0A4D\u0A1F',     # Ã (195) subscript Tainka
    '\xcd': '\u0A4D\u0A35',     # Í (205) subscript Va
    '\xce': '\u0A4D\u0A2F',     # Î (206) subscript Ya
    '\xc4': '\u0A4D',           # Ä (196) trailing virama

    # --- Special / compound ---
    'L': '\u0A28\u0A42\u0A70',  # ਨੂੰ  dative postposition (3 chars, 1 byte)
    '\xa1': '\u0A74',           # ¡ (161) Ik Onkar ੴ
    '\xda': '\u0A03',           # Ú (218) Visarga ਃ

    # --- Punctuation / verse markers ---
    '[': '\u0964',              # । single danda (sentence end)
    ']': '\u0965',              # ॥ double danda (verse end)

    # --- Digits → Gurmukhi digits ---
    '0': '\u0A66',  '1': '\u0A67',  '2': '\u0A68',  '3': '\u0A69',
    '4': '\u0A6A',  '5': '\u0A6B',  '6': '\u0A6C',  '7': '\u0A6D',
    '8': '\u0A6E',  '9': '\u0A6F',
}

# Visual artifacts: stripped before processing — no Gurmukhi meaning.
# Characters that can be a base consonant after sihari 'i'
_BASE_CONSONANTS: frozenset[str] = frozenset(
    'kKgGcCjJtTfFdDqQnNpPbBmrlvVhsXSZ'
    + '\xdf\xf8\xf9'   # ß ø ù
)

# Subscript forms that can follow a base consonant in a cluster
_SUBSCRIPT_FORMS: frozenset[str] = frozenset('RH\xc3\xcd\xce')  # R H Ã Í Î

# Mukta (a) + following matra → precomposed independent vowel
_MUKTA_MATRA: dict[str, str] = {
    'w': '\u0A06',              # aw  → ਆ  (AA)
    'W': '\u0A06\u0A02',        # aW  → ਆਂ (AA + bindi)
    'O': '\u0A14',              # aO  → ਔ  (AU)
    'Y': '\u0A10',              # aY  → ਐ  (AI)
    'o': '\u0A13',              # ao  → ਓ  (OO)
    'y': '\u0A0F',              # ay  → ਏ  (EE)
}

# Iri carrier (e) + following matra → precomposed independent vowel
_IRI_MATRA: dict[str, str] = {
    'y': '\u0A0F',              # ey  → ਏ  (EE)
    'I': '\u0A08',              # eI  → ਈ  (II)
}

# Ura carrier (A) + following matra → precomposed independent vowel
_URA_MATRA: dict[str, str] = {
    'u': '\u0A09',              # Au  → ਉ  (U)
    'U': '\u0A0A',              # AU  → ਊ  (UU)
    'o': '\u0A13',              # Ao  → ਓ  (OO)
}


def _process_char(text: str, pos: int) -> tuple[str, int]:
    """Process one logical SriAngad character. Returns (unicode_output, chars_consumed)."""
    ch = text[pos]
    ahead = text[pos + 1:]  # remaining text after current char

    # Ø: silent prefix — Øz → ੱ, Ø alone → no output
    if ch == '\xd8':
        if ahead and ahead[0] == 'z':
            return '\u0A71', 2  # ੱ addak
        return '', 1

    # Sihari 'i': pre-base matra, must be reordered after its consonant
    if ch == 'i':
        if not ahead:
            return '\u0A3F', 1  # edge case: 'i' at end of string
        if ahead[0] == 'e':
            return '\u0A07', 2  # i + e → ਇ (independent short-i vowel)
        if ahead[0] in _BASE_CONSONANTS:
            output = CHAR_MAP[ahead[0]]
            consumed = 2
            if len(ahead) > 1 and ahead[1] in _SUBSCRIPT_FORMS:
                output += CHAR_MAP[ahead[1]]
                consumed = 3
            return output + '\u0A3F', consumed  # consonant [+ subscript] + ਿ
        return '\u0A3F', 1  # 'i' before non-consonant → emit sihari as-is

    # Mukta 'a': standalone ਅ, or + matra → precomposed independent vowel
    if ch == 'a':
        if ahead and ahead[0] in _MUKTA_MATRA:
            return _MUKTA_MATRA[ahead[0]], 2
        return '\u0A05', 1  # standalone ਅ

    # Iri carrier 'e': standalone ੲ, or + matra → precomposed independent vowel
    if ch == 'e':
        if ahead and ahead[0] in _IRI_MATRA:
            return _IRI_MATRA[ahead[0]], 2
        return '\u0A72', 1  # standalone ੲ

    # Ura carrier 'A': standalone ੳ, or + matra → precomposed independent vowel
    if ch == 'A':
        if ahead and ahead[0] in _URA_MATRA:
            return _URA_MATRA[ahead[0]], 2
        return '\u0A73', 1  # standalone ੳ

    if ch in CHAR_MAP:
        return CHAR_MAP[ch], 1

    return ch, 1  # pass through: spaces, unknown punctuation, etc.


def convert(text: str) -> str:
    """Convert a SriAngad-encoded string to Unicode Gurmukhi."""
    result: list[str] = []
    pos = 0
    while pos < len(text):
        chunk, consumed = _process_char(text, pos)
        result.append(chunk)
        pos += consumed
    output = ''.join(result)
    # Fix matra ordering: nasalization marks (ੰ ਂ) must come AFTER vowel matras (ੁ ੂ)
    # SriAngad typists wrote in visual top-to-bottom order; Unicode requires vowel first.
    for nasal in ('\u0A70', '\u0A02'):       # ੰ tippi, ਂ bindi
        for vowel in ('\u0A42', '\u0A41'):   # ੂ dulainkar, ੁ aunkar
            output = output.replace(nasal + vowel, vowel + nasal)
    return output
