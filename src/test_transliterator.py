"""
test_transliterator.py — Unit tests for Gurmukhi → Devanagari transliteration.

4 test groups: Atomic mappings, Preprocessing edge cases, Word-level tests, Edge cases.
"""

import unittest
from transliterator import transliterate


class TestAtomicMappings(unittest.TestCase):
    """Test individual character mappings."""

    def test_vowel_a(self):
        self.assertEqual(transliterate('ਅ'), 'अ')

    def test_vowel_aa(self):
        self.assertEqual(transliterate('ਆ'), 'आ')

    def test_vowel_i(self):
        self.assertEqual(transliterate('ਇ'), 'इ')

    def test_vowel_ii(self):
        self.assertEqual(transliterate('ਈ'), 'ई')

    def test_vowel_u(self):
        self.assertEqual(transliterate('ਉ'), 'उ')

    def test_vowel_uu(self):
        self.assertEqual(transliterate('ਊ'), 'ऊ')

    def test_vowel_e(self):
        self.assertEqual(transliterate('ਏ'), 'ए')

    def test_vowel_ai(self):
        self.assertEqual(transliterate('ਐ'), 'ऐ')

    def test_vowel_o(self):
        self.assertEqual(transliterate('ਓ'), 'ओ')

    def test_vowel_au(self):
        self.assertEqual(transliterate('ਔ'), 'औ')

    def test_matra_aa(self):
        self.assertEqual(transliterate('ਕਾ'), 'का')

    def test_matra_i(self):
        self.assertEqual(transliterate('ਕਿ'), 'कि')

    def test_matra_ii(self):
        self.assertEqual(transliterate('ਕੀ'), 'की')

    def test_matra_u(self):
        self.assertEqual(transliterate('ਕੁ'), 'कु')

    def test_matra_uu(self):
        self.assertEqual(transliterate('ਕੂ'), 'कू')

    def test_matra_e(self):
        self.assertEqual(transliterate('ਕੇ'), 'के')

    def test_matra_ai(self):
        self.assertEqual(transliterate('ਕੈ'), 'कै')

    def test_matra_o(self):
        self.assertEqual(transliterate('ਕੋ'), 'को')

    def test_matra_au(self):
        self.assertEqual(transliterate('ਕੌ'), 'कौ')

    def test_consonant_ka(self):
        self.assertEqual(transliterate('ਕ'), 'क')

    def test_consonant_kha(self):
        self.assertEqual(transliterate('ਖ'), 'ख')

    def test_consonant_ga(self):
        self.assertEqual(transliterate('ਗ'), 'ग')

    def test_consonant_gha(self):
        self.assertEqual(transliterate('ਘ'), 'घ')

    def test_consonant_ja(self):
        self.assertEqual(transliterate('ਜ'), 'ज')

    def test_consonant_ta(self):
        self.assertEqual(transliterate('ਤ'), 'त')

    def test_consonant_tha(self):
        self.assertEqual(transliterate('ਥ'), 'थ')

    def test_consonant_da(self):
        self.assertEqual(transliterate('ਦ'), 'द')

    def test_consonant_dha(self):
        self.assertEqual(transliterate('ਧ'), 'ध')

    def test_consonant_na(self):
        self.assertEqual(transliterate('ਨ'), 'न')

    def test_consonant_pa(self):
        self.assertEqual(transliterate('ਪ'), 'प')

    def test_consonant_pha(self):
        self.assertEqual(transliterate('ਫ'), 'फ')

    def test_consonant_ba(self):
        self.assertEqual(transliterate('ਬ'), 'ब')

    def test_consonant_bha(self):
        self.assertEqual(transliterate('ਭ'), 'भ')

    def test_consonant_ma(self):
        self.assertEqual(transliterate('ਮ'), 'म')

    def test_consonant_ya(self):
        self.assertEqual(transliterate('ਯ'), 'य')

    def test_consonant_ra(self):
        self.assertEqual(transliterate('ਰ'), 'र')

    def test_consonant_la(self):
        self.assertEqual(transliterate('ਲ'), 'ल')

    def test_consonant_va(self):
        self.assertEqual(transliterate('ਵ'), 'व')

    def test_consonant_sa(self):
        self.assertEqual(transliterate('ਸ'), 'स')

    def test_consonant_ha(self):
        self.assertEqual(transliterate('ਹ'), 'ह')

    def test_diacritic_bindi(self):
        self.assertEqual(transliterate('ਂ'), 'ं')

    def test_diacritic_visarga(self):
        self.assertEqual(transliterate('ਃ'), 'ः')

    def test_diacritic_nukta(self):
        self.assertEqual(transliterate('਼'), '़')

    def test_diacritic_virama(self):
        self.assertEqual(transliterate('੍'), '्')

    def test_tippi_to_anusvara(self):
        self.assertEqual(transliterate('ੰ'), 'ं')

    def test_digit_zero(self):
        self.assertEqual(transliterate('੦'), '०')

    def test_digit_one(self):
        self.assertEqual(transliterate('੧'), '१')

    def test_digit_five(self):
        self.assertEqual(transliterate('੫'), '५')

    def test_danda(self):
        self.assertEqual(transliterate('।'), '।')

    def test_double_danda(self):
        self.assertEqual(transliterate('॥'), '॥')

    def test_ik_onkar(self):
        self.assertEqual(transliterate('ੴ'), 'ੴ')


class TestPreprocessing(unittest.TestCase):
    """Test preprocessing edge cases: addak, sha, rra."""

    def test_addak_ka(self):
        self.assertEqual(transliterate('ੱਕ'), 'क्क')

    def test_addak_ta(self):
        self.assertEqual(transliterate('ੱਤ'), 'त्त')

    def test_addak_sa(self):
        self.assertEqual(transliterate('ੱਸ'), 'स्स')

    def test_addak_in_word(self):
        self.assertEqual(transliterate('ਉੱਤਰ'), 'उत्तर')

    def test_addak_before_sha(self):
        # ੱਸ਼ = addak + (sa+nukta) → just (sa+nukta) → श
        self.assertEqual(transliterate('\u0A71\u0A38\u0A3C'), 'श')

    def test_sha_two_codepoints(self):
        self.assertEqual(transliterate('ਸ਼'), 'श')

    def test_sha_in_word(self):
        self.assertEqual(transliterate('ਸ਼ਰਮ'), 'शरम')

    def test_za_two_codepoints(self):
        # ja + nukta → ज़
        self.assertEqual(transliterate('ਜ਼'), 'ज़')

    def test_gha_nukta(self):
        # ga + nukta → ग़
        self.assertEqual(transliterate('ਗ਼'), 'ग़')

    def test_rra(self):
        self.assertEqual(transliterate('ੜ'), 'ड़')

    def test_ik_onkar_preserved(self):
        self.assertEqual(transliterate('ੴ'), 'ੴ')


class TestWordLevel(unittest.TestCase):
    """Test real Braj/Gurbani words."""

    def test_manmukh(self):
        # ਮਨਮੁਖ → मनमुख
        self.assertEqual(transliterate('ਮਨਮੁਖ'), 'मनमुख')

    def test_uttara(self):
        # ਉੱਤਰ → उत्तर (addak expansion)
        self.assertEqual(transliterate('ਉੱਤਰ'), 'उत्तर')

    def test_guru(self):
        # ਗੁਰੂ → गुरू
        self.assertEqual(transliterate('ਗੁਰੂ'), 'गुरू')

    def test_sharam(self):
        # ਸ਼ਰਮ → शरम (sha)
        self.assertEqual(transliterate('ਸ਼ਰਮ'), 'शरम')

    def test_svarup(self):
        # ਸ੍ਵਰੂਪ → स्वरूप (subscript va)
        self.assertEqual(transliterate('ਸ੍ਵਰੂਪ'), 'स्वरूप')

    def test_hirade(self):
        # ਹਿਰਦੇ → हिरदे
        self.assertEqual(transliterate('ਹਿਰਦੇ'), 'हिरदे')

    def test_nahi(self):
        # ਨਹੀਂ → नहीं (bindi preserved)
        self.assertEqual(transliterate('ਨਹੀਂ'), 'नहीं')

    def test_main(self):
        # ਮੈਂ → मैं
        self.assertEqual(transliterate('ਮੈਂ'), 'मैं')

    def test_bund(self):
        # ਬੂੰਦ → बूंद (tippi after dulainkar)
        self.assertEqual(transliterate('ਬੂੰਦ'), 'बूंद')

    def test_makri(self):
        # ਮਕੜੀ → मकड़ी (rra → ड़)
        self.assertEqual(transliterate('ਮਕੜੀ'), 'मकड़ी')

    def test_sri(self):
        # ਸ੍ਰੀ → स्री
        self.assertEqual(transliterate('ਸ੍ਰੀ'), 'स्री')

    def test_trisna(self):
        # ਤ੍ਰਿਸਨਾ → त्रिसना (subscript ra)
        self.assertEqual(transliterate('ਤ੍ਰਿਸਨਾ'), 'त्रिसना')


class TestEdgeCases(unittest.TestCase):
    """Edge cases and regression tests."""

    def test_empty_string(self):
        self.assertEqual(transliterate(''), '')

    def test_latin_passthrough(self):
        self.assertEqual(transliterate('abc'), 'abc')

    def test_space_passthrough(self):
        self.assertEqual(transliterate(' '), ' ')

    def test_digits_in_context(self):
        # ਪੰਨਾ ੯੨ → पंना ९२
        self.assertEqual(transliterate('ਪੰਨਾ ੯੨'), 'पंना ९२')

    def test_danda_sequence(self):
        self.assertEqual(transliterate('ਗੁਰੂ ।'), 'गुरू ।')
        self.assertEqual(transliterate('ਗੁਰੂ ॥'), 'गुरू ॥')

    def test_ik_onkar_with_text(self):
        result = transliterate('ੴ ਸਤਿਗੁਰ')
        self.assertIn('ੴ', result)
        self.assertIn('सतिगुर', result)

    def test_no_gurmukhi_in_output(self):
        # After transliteration, no Gurmukhi consonants should remain
        text = 'ਮਨਮੁਖ ਭੈ ਕੀ ਸਾਰ ਨ ਜਾਣਨੀ'
        result = transliterate(text)
        # Check that no Gurmukhi codepoints in consonant/vowel ranges remain
        for cp in range(0x0A05, 0x0A3E):  # vowels and some chars
            self.assertNotIn(chr(cp), result, f"Gurmukhi U+{cp:04X} leaked")


if __name__ == '__main__':
    unittest.main(verbosity=2)
