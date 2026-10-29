import unittest
from yako_v10_core import analyze, simulate, prompt_for, rule_explanation
class V10Tests(unittest.TestCase):
    def test_rates(self):
        r=analyze('Lucro garantido de 30% ao mês')
        self.assertEqual([f['rate_percent_monthly'] for f in r['findings'] if 'rate_percent_monthly' in f],[30.0])
        self.assertNotIn('25%',str(r))
    def test_compound(self):
        r=simulate('1000','10',2)
        self.assertEqual(r['final_balance'],1210)
    def test_no_claims(self):
        r=analyze('Retorno garantido de 25% ao mês')
        self.assertIn('Nunca afirme',prompt_for(r))
        self.assertIn('não comprova fraude',rule_explanation(r))
    def test_reject_invalid(self):
        with self.assertRaises(ValueError): simulate('nan',10,12)
        with self.assertRaises(ValueError): analyze('')
if __name__=='__main__':unittest.main()
