SPELLING_CORRECTION_PROMPT = """\
You are proofreading Devanagari text that was machine-transliterated from Gurmukhi script.
Fix ONLY Devanagari spelling errors introduced by the transliteration process.

Errors to fix:
- Wrong matra order (e.g. ंू should be ूं)
- Anusvara/chandrabindu confusion (ं vs ँ)
- Missing or extra nukta (़)
- Virama artifacts or stray halant (्)
- Doubled or missing conjunct consonants

Rules:
- Do NOT change vocabulary, word choice, or Braj Bhasha forms
- Do NOT rephrase or modernize — spelling fixes only
- Return ONLY a JSON array. Include only paragraphs you changed.
- Format: [{{"index": <para_idx>, "corrected": "<full corrected text>"}}]
- If no changes needed, return: []

Paragraphs (index: text):
{numbered_paragraphs}
"""
