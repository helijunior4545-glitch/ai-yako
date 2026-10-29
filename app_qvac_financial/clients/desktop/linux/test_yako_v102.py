import unittest
from yako_v102_engine import analyze,simulation,prompt
class V102Tests(unittest.TestCase):
 def test_fraud_patterns(self):
  r=analyze('Uma empresa promete 30% de lucro ao mês sem risco de perdas, exige depósito imediato, usa algoritmo secreto e não apresenta demonstrações financeiras auditadas.')
  codes={f['code'] for f in r['findings']}
  self.assertTrue({'MONTHLY_RETURN','NO_LOSS','URGENCY','SECRET','UNAUDITED'}<=codes,codes)
 def test_old_rate(self):
  self.assertIn('MONTHLY_RETURN',{f['code'] for f in analyze('Retorno garantido de 25% ao mês')['findings']})
 def test_facts_evidence(self):
  r=analyze('Retorno garantido de 25% ao mês')
  self.assertIn('FATOS',prompt(r))
  self.assertEqual(r['financial_execution'],'DISABLED')
 def test_math(self):
  self.assertEqual(simulation(1000,10,2)['final_balance'],1210)
 def test_negative(self):
  with self.assertRaises(ValueError):simulation(1000,0,0)
if __name__=='__main__':unittest.main()
