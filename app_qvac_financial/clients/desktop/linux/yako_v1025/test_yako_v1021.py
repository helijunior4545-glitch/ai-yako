import unittest
from yako_v1020_finance import smart_analysis

class EnhancedFinanceTests(unittest.TestCase):
 def test_ratios_and_surplus(self):
  text=('A company has R$500,000 in cash, monthly revenue of R$200,000, and monthly expenses of R$170,000. '
        'The CEO wants to invest R$350,000 in a new business operation. '
        'If successful, the operation will generate an additional R$80,000 in monthly revenue starting after three months. '
        'The estimated probability of failure is 40%. The company has R$600,000 in outstanding debt.')
  r=smart_analysis(text,'en');self.assertIsNotNone(r)
  c=r['calculation'];self.assertEqual(c['cash_after_investment'],'150000')
  self.assertEqual(c['operating_result'],'30000')
  self.assertEqual(c['expected_additional_revenue'],'48000')
  self.assertEqual(c['investment_cash_percent'],'70.0')
  self.assertAlmostEqual(float(c['cash_expense_coverage_months']),150000/170000)
  self.assertEqual(c['debt_monthly_revenue_ratio'],'3')
  self.assertIn('not runway',r['answer'])
 def test_no_invented_ratios(self):
  r=smart_analysis('A company has R$100,000 in cash and wants to invest R$20,000.','en')
  self.assertNotIn('cash_expense_coverage_months',r['calculation'])
 def test_partial(self):
  r=smart_analysis('Monthly revenue of R$200,000 and monthly expenses of R$170,000.','en')
  self.assertEqual(r['calculation']['operating_result'],'30000')
if __name__=='__main__':unittest.main()
