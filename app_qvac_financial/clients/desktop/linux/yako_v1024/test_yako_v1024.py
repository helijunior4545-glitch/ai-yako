import unittest
from yako_v1023_portfolio import analyze_portfolio
class ConstraintTests(unittest.TestCase):
 def setUp(self):
  self.prompt="""Available cash: R$1,500,000
Monthly revenue: R$500,000
Monthly operating expenses: R$410,000
Monthly debt repayments: R$30,000
Minimum required cash reserve: R$400,000
**Investment A — Expansion**
Initial investment: R$650,000
Probability of success: 80%
Additional monthly revenue if successful: R$180,000
Additional monthly operating expenses if successful: R$70,000
**Investment B — Automation**
Initial investment: R$300,000
Probability of success: 95%
Monthly operating cost savings if successful: R$75,000
**Investment C — SaaS**
Initial investment: R$500,000
Probability of success: 65%
Additional monthly revenue if successful: R$160,000
Additional monthly operating expenses if successful: R$60,000
**Investment D — Infrastructure**
Initial investment: R$250,000
Probability of success: 100%
Monthly operating cost savings: R$40,000
### Critical Investment Dependencies
Investment C cannot be implemented unless Investment D is also implemented.
Investments A and B cannot be implemented simultaneously because they require the same engineering team.
Investment D must be completed before Investment C can begin implementation.
### Required Analysis
Find the best feasible portfolio."""
 def test_feasibility(self):
  r=analyze_portfolio(self.prompt);self.assertIsNotNone(r)
  self.assertEqual(r['calculation']['alternatives'],16)
  self.assertEqual(r['calculation']['feasible'],8)
  self.assertEqual(r['calculation']['infeasible'],8)
  self.assertIn('B + C + D — BRL 176,250.00',r['answer'])
  self.assertIn('A and B mutually exclusive',r['answer'])
  self.assertIn('C requires D',r['answer'])
 def test_without_constraints(self):
  t=self.prompt.split('### Critical Investment Dependencies')[0].replace('Minimum required cash reserve: R$400,000','')
  r=analyze_portfolio(t)
  self.assertEqual(r['calculation']['feasible'],15)
 def test_minimum_reserve(self):
  r=analyze_portfolio(self.prompt)
  self.assertEqual(r['calculation']['constraints']['minimum_reserve'],'400000')
if __name__=='__main__':unittest.main()
