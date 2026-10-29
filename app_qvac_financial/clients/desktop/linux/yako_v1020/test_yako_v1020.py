import unittest
from yako_v1020_finance import smart_analysis
class FinanceTests(unittest.TestCase):
 def test_full_english(self):
  t=('A company has R$500,000 in cash, monthly revenue of R$200,000, and monthly expenses of R$170,000. '
  'The CEO wants to invest R$350,000 in a new business operation. If successful, the operation will generate '
  'an additional R$80,000 in monthly revenue starting after three months. The estimated probability of failure is 40%. '
  'The company also has R$600,000 in outstanding debt, but the interest rates and repayment dates are unknown.')
  r=smart_analysis(t,'en');self.assertIsNotNone(r)
  c=r['calculation'];self.assertEqual(c.get('cash_after_investment'),'150000');self.assertEqual(c.get('operating_result'),'30000');self.assertEqual(c.get('expected_additional_revenue'),'48000');self.assertEqual(c.get('investment_cash_percent'),'70.0')
 def test_independent(self):
  r=smart_analysis('A different company has R$100,000 in cash and wants to invest R$20,000 in a new project.','en')
  self.assertEqual(r['calculation']['cash_after_investment'],'80000')
 def test_portuguese(self):
  r=smart_analysis('Uma empresa possui R$ 250.000 em caixa e pretende investir R$ 75.000.','pt')
  self.assertEqual(r['calculation']['cash_after_investment'],'175000')
 def test_partial(self):
  r=smart_analysis('Monthly revenue of R$200,000 and monthly expenses of R$170,000.','en')
  self.assertEqual(r['calculation']['operating_result'],'30000')
if __name__=='__main__':unittest.main()
