"""
test_converter.py — Comprehensive tests for SriAngad → Unicode converter.

Organised into 4 groups:
  Group 1: Individual character mapping (one assertion per CHAR_MAP entry)
  Group 2: Sihari (ਿ) reordering algorithm (critical)
  Group 3: Word-level tests from sample_mappings.md (ground truth)
  Group 4: Full-line integration tests
"""

import unittest
from converter import convert


class TestIndividualChars(unittest.TestCase):
    """Group 1 — Every entry in CHAR_MAP must produce the correct output."""

    # --- Vowel matras ---
    def test_w_aa_matra(self):        self.assertEqual(convert('w'), 'ਾ')
    def test_W_aa_bindi(self):        self.assertEqual(convert('W'), 'ਾਂ')
    def test_I_ii_matra(self):        self.assertEqual(convert('I'), 'ੀ')
    def test_u_u_matra(self):         self.assertEqual(convert('u'), 'ੁ')
    def test_U_uu_matra(self):        self.assertEqual(convert('U'), 'ੂ')
    def test_y_e_matra(self):         self.assertEqual(convert('y'), 'ੇ')
    def test_Y_ai_matra(self):        self.assertEqual(convert('Y'), 'ੈ')
    def test_o_o_matra(self):         self.assertEqual(convert('o'), 'ੋ')
    def test_O_au_matra(self):        self.assertEqual(convert('O'), 'ੌ')
    def test_M_tippi(self):           self.assertEqual(convert('M'), 'ੰ')
    def test_x_bindi(self):           self.assertEqual(convert('x'), 'ਂ')
    def test_z_addak(self):           self.assertEqual(convert('z'), 'ੱ')

    # --- Cluster-context matra variants ---
    def test_u_circ_tippi_variant(self):      self.assertEqual(convert('û'), 'ੰ')   # û = M variant
    def test_u_uml_aunkar_variant(self):      self.assertEqual(convert('ü'), 'ੁ')   # ü = u variant
    def test_A_acute_dulainkar_variant(self): self.assertEqual(convert('Á'), 'ੂ')   # Á = U variant
    def test_A_grave_bindi_variant(self):     self.assertEqual(convert('À'), 'ਂ')   # À = x variant

    # --- Independent vowel carriers ---
    def test_a_mukta(self):   self.assertEqual(convert('a'), 'ਅ')
    def test_A_ura(self):     self.assertEqual(convert('A'), 'ੳ')
    def test_e_iri(self):     self.assertEqual(convert('e'), 'ੲ')
    def test_E_long_o(self):  self.assertEqual(convert('E'), 'ਓ')

    # --- Consonants (all 30) ---
    def test_k(self): self.assertEqual(convert('k'), 'ਕ')
    def test_K(self): self.assertEqual(convert('K'), 'ਖ')
    def test_g(self): self.assertEqual(convert('g'), 'ਗ')
    def test_G(self): self.assertEqual(convert('G'), 'ਘ')
    def test_c(self): self.assertEqual(convert('c'), 'ਚ')
    def test_C(self): self.assertEqual(convert('C'), 'ਛ')
    def test_j(self): self.assertEqual(convert('j'), 'ਜ')
    def test_J(self): self.assertEqual(convert('J'), 'ਝ')
    def test_t(self): self.assertEqual(convert('t'), 'ਟ')
    def test_T(self): self.assertEqual(convert('T'), 'ਠ')
    def test_f(self): self.assertEqual(convert('f'), 'ਡ')
    def test_d(self): self.assertEqual(convert('d'), 'ਦ')   # d=ਦ NOT ਡ
    def test_D(self): self.assertEqual(convert('D'), 'ਧ')   # D=ਧ NOT ਢ
    def test_F(self): self.assertEqual(convert('F'), 'ਢ')   # F=ਢ
    def test_q(self): self.assertEqual(convert('q'), 'ਤ')
    def test_Q(self): self.assertEqual(convert('Q'), 'ਥ')
    def test_n(self): self.assertEqual(convert('n'), 'ਨ')
    def test_N(self): self.assertEqual(convert('N'), 'ਣ')
    def test_p(self): self.assertEqual(convert('p'), 'ਪ')
    def test_P(self): self.assertEqual(convert('P'), 'ਫ')
    def test_b(self): self.assertEqual(convert('b'), 'ਬ')
    def test_B(self): self.assertEqual(convert('B'), 'ਭ')
    def test_m(self): self.assertEqual(convert('m'), 'ਮ')
    def test_r(self): self.assertEqual(convert('r'), 'ਰ')
    def test_l(self): self.assertEqual(convert('l'), 'ਲ')
    def test_v(self): self.assertEqual(convert('v'), 'ਵ')
    def test_V(self): self.assertEqual(convert('V'), 'ੜ')
    def test_h(self): self.assertEqual(convert('h'), 'ਹ')
    def test_s(self): self.assertEqual(convert('s'), 'ਸ')
    def test_X(self): self.assertEqual(convert('X'), 'ਯ')

    # --- Multi-char output consonants ---
    def test_S_sha(self):        self.assertEqual(convert('S'), '\u0A38\u0A3C')   # ਸ਼
    def test_Z_za(self):         self.assertEqual(convert('Z'), '\u0A1C\u0A3C')   # ਜ਼
    def test_ss_gha_nukta(self): self.assertEqual(convert('ß'), '\u0A17\u0A3C')   # ਗ਼
    def test_o_stroke_nya(self): self.assertEqual(convert('ø'), '\u0A1E')          # ਞ
    def test_u_grave_nga(self):  self.assertEqual(convert('ù'), '\u0A19')          # ਙ

    # --- Subscript / cluster forms ---
    def test_R_subsc_ra(self):  self.assertEqual(convert('R'), '\u0A4D\u0A30')  # ੍ਰ
    def test_H_subsc_ha(self):  self.assertEqual(convert('H'), '\u0A4D\u0A39')  # ੍ਹ
    def test_A_tilde_subsc_tta(self): self.assertEqual(convert('Ã'), '\u0A4D\u0A1F')  # ੍ਟ
    def test_I_acute_subsc_va(self):  self.assertEqual(convert('Í'), '\u0A4D\u0A35')  # ੍ਵ
    def test_I_circ_subsc_ya(self):   self.assertEqual(convert('Î'), '\u0A4D\u0A2F')  # ੍ਯ
    def test_A_uml_virama(self):      self.assertEqual(convert('Ä'), '\u0A4D')         # ੍

    # --- Special / compound ---
    def test_L_nuu(self):       self.assertEqual(convert('L'), '\u0A28\u0A42\u0A70')  # ਨੂੰ
    def test_inverted_exc_ik_onkar(self): self.assertEqual(convert('¡'), '\u0A74')    # ੴ
    def test_U_acute_visarga(self):       self.assertEqual(convert('Ú'), '\u0A03')    # ਃ

    # --- Null characters ---
    def test_ae_artifact_null(self):    self.assertEqual(convert('æ'), '')
    def test_O_stroke_alone_null(self): self.assertEqual(convert('Ø'), '')  # Ø alone → no output

    # --- Pass-through (digits, spaces, punctuation) ---
    def test_digit_gurmukhi(self):      self.assertEqual(convert('1'), '੧')
    def test_space_passthrough(self):   self.assertEqual(convert(' '), ' ')
    def test_bracket_danda(self):       self.assertEqual(convert(']'), '॥')


class TestSihariReordering(unittest.TestCase):
    """Group 2 — Sihari (ਿ) reordering is the most critical algorithm."""

    def test_basic_reorder_h(self):
        # ih → ਹਿ  (h before ਿ in output)
        self.assertEqual(convert('ih'), '\u0A39\u0A3F')

    def test_basic_reorder_j(self):
        # ij → ਜਿ
        self.assertEqual(convert('ij'), '\u0A1C\u0A3F')

    def test_basic_reorder_k(self):
        # ik → ਕਿ
        self.assertEqual(convert('ik'), '\u0A15\u0A3F')

    def test_reorder_with_subscript_ra(self):
        # iqR → ਤ੍ਰਿ  (NOT ਤਿ੍ਰ — the ਿ goes AFTER the full cluster ਤ੍ਰ)
        self.assertEqual(convert('iqR'), '\u0A24\u0A4D\u0A30\u0A3F')

    def test_reorder_with_subscript_ra_2(self):
        # isR → ਸ੍ਰਿ
        self.assertEqual(convert('isR'), '\u0A38\u0A4D\u0A30\u0A3F')

    def test_i_e_gives_short_i_vowel(self):
        # ie → ਇ (U+0A07, independent short-i vowel)
        self.assertEqual(convert('ie'), '\u0A07')

    def test_i_before_sha(self):
        # iS → ਸ਼ਿ  (S is in _BASE_CONSONANTS)
        self.assertEqual(convert('iS'), '\u0A38\u0A3C\u0A3F')

    def test_double_sihari(self):
        # isiKaw → ਸਿਖਿਆ  (aw normalizes to ਆ via mukta look-ahead)
        result = convert('isiKaw')
        self.assertEqual(result, 'ਸਿਖਿਆ')

    def test_sihari_before_subsc_ya(self):
        # iesiQq → ਇਸਥਿਤ  (ie=ਇ, s=ਸ, iQ with Q=ਥ then ਿ, q=ਤ)
        self.assertEqual(convert('iesiQq'), '\u0A07\u0A38\u0A25\u0A3F\u0A24')

    def test_sihari_trailing(self):
        # krih → ਕਰਹਿ  (i before trailing h)
        self.assertEqual(convert('krih'), '\u0A15\u0A30\u0A39\u0A3F')


class TestWordLevel(unittest.TestCase):
    """Group 3 — Word-level tests from sample_mappings.md (verified ground truth)."""

    # --- Mapping 1 — Gurbani line ---
    def test_mnmuK(self): self.assertEqual(convert('mnmuK'), 'ਮਨਮੁਖ')
    def test_BY(self):    self.assertEqual(convert('BY'), 'ਭੈ')
    def test_kI(self):    self.assertEqual(convert('kI'), 'ਕੀ')
    def test_swr(self):   self.assertEqual(convert('swr'), 'ਸਾਰ')

    def test_jwNnI(self):
        # N=ਣ
        self.assertEqual(convert('jwNnI'), 'ਜਾਣਨੀ')

    def test_iqRsnw(self):
        # sihari reorder + R=੍ਰ cluster
        self.assertEqual(convert('iqRsnw'), 'ਤ੍ਰਿਸਨਾ')

    def test_jlqy(self): self.assertEqual(convert('jlqy'), 'ਜਲਤੇ')

    def test_krih(self):
        # trailing sihari
        self.assertEqual(convert('krih'), 'ਕਰਹਿ')

    def test_pukwr(self): self.assertEqual(convert('pukwr'), 'ਪੁਕਾਰ')
    def test_nwnk(self):  self.assertEqual(convert('nwnk'), 'ਨਾਨਕ')

    def test_nwvY(self):
        # v=ਵ, Y=ੈ
        self.assertEqual(convert('nwvY'), 'ਨਾਵੈ')

    def test_suKu(self):    self.assertEqual(convert('suKu'), 'ਸੁਖੁ')
    def test_gurmqI(self):  self.assertEqual(convert('gurmqI'), 'ਗੁਰਮਤੀ')

    def test_Auir(self):
        # A=ੳ carrier, u=ੁ, i before r → ਰਿ
        self.assertEqual(convert('Auir'), 'ਉਰਿ')

    def test_Dwr(self):
        # D=ਧ (NOT ਢ which is F)
        self.assertEqual(convert('Dwr'), 'ਧਾਰ')

    # --- Mapping 1 — Braj meaning ---
    def test_purS(self):
        # S=ਸ਼ (sha)
        self.assertEqual(convert('purS'), 'ਪੁਰਸ਼')

    def test_nhIx(self):
        # x=ਂ
        self.assertEqual(convert('nhIx'), 'ਨਹੀਂ')

    def test_hYx(self): self.assertEqual(convert('hYx'), 'ਹੈਂ')

    def test_iqRSnW(self):
        # R=੍ਰ, S=ਸ਼, W=ਾਂ (all three corrections verified)
        self.assertEqual(convert('iqRSnW'), 'ਤ੍ਰਿਸ਼ਨਾਂ')

    def test_hUey(self):
        # U=ੂ, e=ੲ (iri carrier), y=ੇ
        self.assertEqual(convert('hUey'), 'ਹੂਏ')

    def test_sRI(self):
        # R=੍ਰ subscript
        self.assertEqual(convert('sRI'), 'ਸ੍ਰੀ')

    def test_gurU(self):
        # U=ੂ
        self.assertEqual(convert('gurU'), 'ਗੁਰੂ')

    def test_ihrdy(self):
        # d=ਦ (NOT ਡ which is f)
        self.assertEqual(convert('ihrdy'), 'ਹਿਰਦੇ')

    def test_mYx(self): self.assertEqual(convert('mYx'), 'ਮੈਂ')

    def test_AuOzqr(self):
        # Øz=ੱ addak two-byte sequence
        self.assertEqual(convert('AuØzqr'), 'ਉੱਤਰ')

    def test_aiDk(self):
        # D=ਧ
        self.assertEqual(convert('aiDk'), 'ਅਧਿਕ')

    def test_anMd(self):
        # M=ੰ tippi
        self.assertEqual(convert('anMd'), 'ਅਨੰਦ')

    # --- Mapping 2 ---
    def test_slok(self):  self.assertEqual(convert('slok'), 'ਸਲੋਕ')

    def test_mU(self):
        # Ú=ਃ Visarga
        self.assertEqual(convert('mÚ'), 'ਮਃ')

    def test_rUpY(self):  self.assertEqual(convert('rUpY'), 'ਰੂਪੈ')

    def test_dosqI(self):
        # d=ਦ confirmed again
        self.assertEqual(convert('dosqI'), 'ਦੋਸਤੀ')

    def test_BuKY(self):  self.assertEqual(convert('BuKY'), 'ਭੁਖੈ')

    def test_gMFu(self):
        # F=ਢ, M=ੰ
        self.assertEqual(convert('gMFu'), 'ਗੰਢੁ')

    def test_aOr(self):
        # a+O → precomposed ਔ (AU vowel)
        self.assertEqual(convert('aOr'), 'ਔਰ')

    # --- Mapping 3 ---
    def test_rwju(self):  self.assertEqual(convert('rwju'), 'ਰਾਜੁ')
    def test_pMjy(self):  self.assertEqual(convert('pMjy'), 'ਪੰਜੇ')

    def test_Tg(self):
        # T=ਠ
        self.assertEqual(convert('Tg'), 'ਠਗ')

    def test_eynI(self):
        # e=ੲ (iri carrier), y=ੇ → ੲੇ renders as ਏ
        self.assertEqual(convert('eynI'), 'ਏਨੀ')

    def test_TgIx(self):  self.assertEqual(convert('TgIx'), 'ਠਗੀਂ')

    def test_Tigaw(self):
        # T=ਠ, i+g → ਗਿ, a+w → ਆ
        self.assertEqual(convert('Tigaw'), 'ਠਗਿਆ')

    def test_Srm(self):
        # S=ਸ਼
        self.assertEqual(convert('Srm'), 'ਸ਼ਰਮ')

    def test_crNI(self):
        # c=ਚ
        self.assertEqual(convert('crNI'), 'ਚਰਣੀ')

    def test_pUCNy(self):
        # C=ਛ, N=ਣ
        self.assertEqual(convert('pUCNy'), 'ਪੂਛਣੇ')

    # --- Mapping 4 ---
    def test_eynw(self):
        # e=ੲ, y=ੇ, n=ਨ, w=ਾ
        self.assertEqual(convert('eynw'), 'ਏਨਾ')

    def test_TginA(self):
        # T=ਠ, g=ਗ, i+n → ਨਿ, Ä=੍ trailing virama
        self.assertEqual(convert('TginÄ'), 'ਠਗਨਿ੍')

    def test_pYrI(self): self.assertEqual(convert('pYrI'), 'ਪੈਰੀ')

    # --- Mapping 5 ---
    def test_lzKNIu(self):
        # z=ੱ, Î=੍ਯ
        self.assertEqual(convert('lzKNÎu'), 'ਲੱਖਣ੍ਯੁ')

    def test_XogI(self):
        # X=ਯ, o=ੋ, g=ਗ, Î=੍ਯ
        self.assertEqual(convert('XogÎ'), 'ਯੋਗ੍ਯ')

    def test_sIrUp(self):
        # Í=੍ਵ subscript Va
        self.assertEqual(convert('sÍrUp'), 'ਸ੍ਵਰੂਪ')

    def test_prmysIr(self):
        # Í=੍ਵ
        self.assertEqual(convert('prmysÍr'), 'ਪਰਮੇਸ੍ਵਰ')

    def test_iesiQq(self):
        # ie=ਇ, s=ਸ, i+Q → ਥਿ, q=ਤ
        self.assertEqual(convert('iesiQq'), 'ਇਸਥਿਤ')

    def test_eIhW(self):
        # e=ੲ, I=ੀ → ੲੀ renders as ਈ; h=ਹ, W=ਾਂ
        self.assertEqual(convert('eIhW'), 'ਈਹਾਂ')

    def test_mkVI(self):
        # V=ੜ
        self.assertEqual(convert('mkVI'), 'ਮਕੜੀ')

    def test_kIoxik(self):
        # Î=੍ਯ, o=ੋ, x=ਂ, i+k → ਕਿ
        self.assertEqual(convert('kÎoxik'), 'ਕ੍ਯੋਂਕਿ')

    def test_DRA(self):
        # D=ਧ, R=੍ਰ, Á=ੂ (dulainkar after subscript)
        self.assertEqual(convert('DRÁ'), 'ਧ੍ਰੂ')

    def test_icq(self):
        # c=ਚ, i+c → ਚਿ, q=ਤ → wait: i is at pos 0, c at pos 1
        # i sees c → emit c(ਚ) + ਿ, then q=ਤ
        self.assertEqual(convert('icq'), 'ਚਿਤ')

    def test_mYL(self):
        # L=ਨੂੰ (3-char compound)
        self.assertEqual(convert('mYL'), 'ਮੈਨੂੰ')

    def test_qtsq(self):
        # q=ਤ, t=ਟ, s=ਸ, q=ਤ
        self.assertEqual(convert('qtsq'), 'ਤਟਸਤ')

    def test_sbd(self):
        # b=ਬ
        self.assertEqual(convert('sbd'), 'ਸਬਦ')

    # --- ANALYSIS.md-only words (chars not in sample_mappings) ---
    def test_ijnHW(self):
        # H=੍ਹ subscript Ha, W=ਾਂ
        self.assertEqual(convert('ijnHW'), 'ਜਿਨ੍ਹਾਂ')

    def test_tIkw(self):
        # t=ਟ
        self.assertEqual(convert('tIkw'), 'ਟੀਕਾ')

    def test_PrI(self):
        # P=ਫ
        self.assertEqual(convert('PrI'), 'ਫਰੀ')

    def test_ZhrIlI(self):
        # Z=ਜ਼ (ja + nukta)
        self.assertEqual(convert('ZhrIlI'), 'ਜ਼ਹਰੀਲੀ')

    def test_suMoI(self):
        # ø=ਞ Nya (rare consonant)
        self.assertEqual(convert('suMøI'), 'ਸੁੰਞੀ')

    def test_uaw(self):
        # ù=ਙ Nga (rare), a+w → ਆ
        self.assertEqual(convert('ùaw'), 'ਙਆ')

    def test_ss_Yr(self):
        # ß=ਗ਼ (ga + nukta)
        self.assertEqual(convert('ßYr'), 'ਗ਼ੈਰ')

    def test_aiDsAn(self):
        # Ã=੍ਟ subscript Tta
        self.assertEqual(convert('aiDsÃwn'), 'ਅਧਿਸ੍ਟਾਨ')

    def test_anûdu(self):
        # û=ੰ tippi variant
        self.assertEqual(convert('anûdu'), 'ਅਨੰਦੁ')

    def test_sRüqI(self):
        # R=੍ਰ, ü=ੁ aunkar after subscript
        self.assertEqual(convert('sRüqI'), 'ਸ੍ਰੁਤੀ')

    def test_CUaet(self):
        # æ=null stripped, C=ਛ, U=ੂ, t=ਟ
        self.assertEqual(convert('CUæt'), 'ਛੂਟ')

    def test_EaMkwru(self):
        # E=ਓ standalone long-O vowel
        self.assertEqual(convert('EaMkwru'), 'ਓਅੰਕਾਰੁ')


class TestFullLines(unittest.TestCase):
    """Group 4 — Full-line integration tests using confirmed Gurbani lines."""

    def test_mapping1_gurbani_line(self):
        src = 'mnmuK BY kI swr n jwNnI iqRsnw jlqy krih pukwr'
        # Word by word: ਮਨਮੁਖ ਭੈ ਕੀ ਸਾਰ ਨ ਜਾਣਨੀ ਤ੍ਰਿਸਨਾ ਜਲਤੇ ਕਰਹਿ ਪੁਕਾਰ
        result = convert(src)
        self.assertIn('ਮਨਮੁਖ', result)
        self.assertIn('ਭੈ', result)
        self.assertIn('ਜਾਣਨੀ', result)
        self.assertIn('ਤ੍ਰਿਸਨਾ', result)
        self.assertIn('ਕਰਹਿ', result)
        self.assertIn('ਪੁਕਾਰ', result)

    def test_mapping2_gurbani_line(self):
        src = 'rUpY kwmY dosqI BuKY swdY gMFu'
        result = convert(src)
        self.assertIn('ਰੂਪੈ', result)
        self.assertIn('ਦੋਸਤੀ', result)
        self.assertIn('ਗੰਢੁ', result)

    def test_mapping3_gurbani_line(self):
        src = 'rwju mwlu rUpu jwiq jobnu pMjy Tg'
        result = convert(src)
        self.assertIn('ਰਾਜੁ', result)
        self.assertIn('ਰੂਪੁ', result)
        self.assertIn('ਪੰਜੇ', result)
        self.assertIn('ਠਗ', result)

    def test_no_latin_consonants_remain(self):
        """After conversion, no SriAngad consonant letters should survive."""
        src = 'mnmuK BY kI swr n jwNnI'
        result = convert(src)
        for ch in 'kKgGcCjJtTdDFqQnNpPbBmrlvVhsX':
            self.assertNotIn(ch, result, f"Latin char '{ch}' leaked into output")

    def test_oz_sequence_within_line(self):
        """Øz pair correctly becomes ੱ in context."""
        src = 'SyK bRhm bhuq pRSn krqw rhw gurU jI AuØzqr dyqy rhy'
        result = convert(src)
        self.assertIn('ਉੱਤਰ', result)
        self.assertNotIn('Ø', result)

    # ------------------------------------------------------------------
    # Matra ordering fixes (from doc_generation_instructions.md)
    # ਬੰੂਦ → ਬੂੰਦ  and  ਹੰੂ → ਹੂੰ
    # ------------------------------------------------------------------

    def test_tippi_before_dulainkar_fixed(self):
        """Tippi typed before dulainkar in source must swap to dulainkar+tippi."""
        self.assertEqual(convert('bMUd'), 'ਬੂੰਦ')

    def test_tippi_before_dulainkar_hoon(self):
        self.assertEqual(convert('hMU'), 'ਹੂੰ')

    def test_tippi_before_aunkar_fixed(self):
        self.assertEqual(convert('bMu'), 'ਬੁੰ')

    def test_bindi_before_dulainkar_fixed(self):
        self.assertEqual(convert('hxU'), 'ਹੂਂ')


if __name__ == '__main__':
    unittest.main(verbosity=2)
