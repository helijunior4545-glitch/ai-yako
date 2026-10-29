import unittest
from yako_v1033_finance import explain_concept,analyze_natural_finance
class Regression(unittest.TestCase):
 def test_three_definitions_and_example(self):
  r=explain_concept('What is the difference between revenue, profit, and cash flow? Explain each concept and provide a practical example.')
  self.assertIsNotNone(r)
  for word in ('Revenue','Profit','Cash flow','Example:'):self.assertIn(word,r['answer'])
  self.assertFalse(r['model_used'])
 def test_cash_flow_existing(self):
  r=analyze_natural_finance('My company earns $75,000 per month, spends $48,000 on operations, and pays $12,000 in monthly debt obligations. Calculate my monthly cash-flow surplus and explain the result.')
  self.assertIsNotNone(r)
  self.assertIn('$15,000.00',r['answer'])
if __name__=='__main__':unittest.main()
