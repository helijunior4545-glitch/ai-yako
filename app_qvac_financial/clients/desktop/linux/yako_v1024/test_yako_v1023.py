import unittest
from yako_v1023_portfolio import analyze_portfolio
class PortfolioTests(unittest.TestCase):
 def setUp(self):
  self.t="""Available cash: R$1,200,000\nMonthly revenue: R$450,000\nMonthly operating expenses: R$380,000\nOutstanding debt: R$700,000\nMonthly debt repayments: R$25,000\n**Investment A — Expansion**\nInitial investment: R$600,000\nProbability of success: 75%\nAdditional monthly revenue if successful: R$150,000\nAdditional monthly operating expenses if successful: R$60,000\nRevenue begins four months after the investment.\n**Investment B — Automation**\nInitial investment: R$350,000\nProbability of success: 90%\nMonthly operating cost savings if successful: R$80,000\nSavings begin two months after the investment.\n### Required analysis\nCompare all four alternatives."""
 def test_two_projects(self):
  r=analyze_portfolio(self.t);self.assertIsNotNone(r);a=r['answer']
  for v in ('70,000.00','45,000.00','67,500.00','72,000.00','139,500.00','250,000.00','850,000.00'):self.assertIn(v,a)
 def test_no_guessing(self):
  self.assertIsNone(analyze_portfolio('A company has R$500,000 in cash and invests R$350,000.'))
 def test_three_projects(self):
  t=self.t.replace('### Required analysis','**Investment C — Research**\nInitial investment: R$50,000\nProbability of success: 50%\nMonthly cost savings: R$10,000\n### Required analysis')
  r=analyze_portfolio(t);self.assertEqual(r['calculation']['alternatives'],8)
 def test_no_invented_probability(self):
  t=self.t.replace('Probability of success: 90%','Probability unknown')
  a=analyze_portfolio(t)['answer'];self.assertIn('success probabilities for all projects',a)
if __name__=='__main__':unittest.main()
