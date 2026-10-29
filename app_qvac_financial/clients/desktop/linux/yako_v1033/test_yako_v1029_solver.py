import unittest
from yako_v1029_solver import solve
PROMPT='''I run a company with $500,000 in available cash. Monthly revenue is $320,000, operating expenses are $250,000, and debt payments are $30,000 per month. I am considering three investments: Investment A: Costs $200,000 and generates an additional $60,000 in monthly revenue, but also increases operating expenses by $25,000 per month. It starts generating revenue after three months. Investment B: Costs $150,000 and reduces monthly operating expenses by $35,000, starting immediately. Investment C: Costs $180,000 and reduces monthly debt payments by $15,000, starting immediately. There are three restrictions: 1. I must maintain at least $200,000 in available cash immediately after investing. 2. Investments A and B cannot be selected together. 3. Investment C can be combined with A or B, but only if the minimum cash reserve is maintained. Analyze every feasible investment combination.'''
class SolverTests(unittest.TestCase):
 def test_full_scenario(self):
  r=solve(PROMPT);self.assertIsNotNone(r);self.assertEqual(r['calculation']['feasible'],4);self.assertEqual(r['calculation']['infeasible'],4)
  for part in ('8.71 months','4.29 months','12.00 months','**Decision:** B','Baseline monthly surplus after stated debt payments: $40,000.00','A + C: remaining cash $120,000.00'):
   self.assertIn(part,r['answer'])
 def test_ambiguous_not_fabricated(self):self.assertIsNone(solve('Investment A: costs $100. Investment B: costs $200.'))
 def test_duplicate_rejected(self):self.assertIsNone(solve('Investment A: costs $100. Investment A: costs $200.'))
if __name__=='__main__':unittest.main()
