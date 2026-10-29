import unittest
from decimal import Decimal
from yako_v1033_finance import analyze_natural_finance,explain_concept
class FinanceTests(unittest.TestCase):
 def test_concept(self):
  self.assertIn('Revenue is',explain_concept('What is the difference between revenue and profit? Answer in two short sentences.')['answer'])
 def test_unstructured(self):
  t='My company is growing, but I am worried about running out of money. We currently have $85,000 in the bank. Our customers pay us approximately $42,000 every month, while salaries, rent, and other operating expenses total around $51,000. We also have a loan payment of $6,000 every month. A supplier is offering us new equipment for $30,000. They claim it could increase our revenue by 25%, but they have not provided evidence. Should I buy the equipment now?'
  result=analyze_natural_finance(t)
  self.assertIsNotNone(result)
  for value in ('$-15,000.00','5.67 months','$55,000.00','3.67 months','$10,500.00','$-4,500.00'):self.assertIn(value,result['answer'])
 def test_simple(self):
  t='A company has $120,000 in cash, earns $50,000 per month, spends $42,000 on operations, and pays $5,000 in monthly debt. What is its monthly cash-flow surplus?'
  self.assertIsNotNone(analyze_natural_finance(t))
 def test_not_invent(self):
  self.assertIsNone(analyze_natural_finance('My company has $40,000 in the bank. Should I buy?'))
if __name__=='__main__':unittest.main()
