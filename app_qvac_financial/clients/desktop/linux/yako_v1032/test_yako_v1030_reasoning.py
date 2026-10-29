import unittest
from yako_v1030_reasoning import reason,normalize
CRISIS=("A company has $180,000 in available cash, monthly revenue of $95,000, operating expenses of $125,000, "
"and monthly debt payments of $20,000. The company must maintain at least $100,000 in available cash "
"immediately after any investment. Three opportunities are available: Investment A costs $70,000 and increases "
"monthly revenue by $30,000, starting after two months. Investment B costs $50,000 and reduces monthly "
"operating expenses by $20,000, starting immediately. Investment C costs $90,000 and reduces monthly "
"debt payments by $15,000, starting immediately. Investments A and B cannot be combined. "
"Analyze all possible investment combinations. Identify which are financially feasible, calculate the remaining cash "
"and monthly surplus or deficit, and determine whether any investment can eliminate the company's monthly cash-flow deficit.")
class ReasoningTests(unittest.TestCase):
 def test_crisis(self):
  r=reason(CRISIS)
  self.assertIsNotNone(r)
  self.assertEqual(r['calculation']['feasible'],3)
  self.assertEqual(r['calculation']['infeasible'],5)
  for part in ('$50,000.00','No feasible investment eliminates','A: steady-state monthly deficit $20,000.00','B: steady-state monthly deficit $30,000.00','A: M1 $60,000.00, M2 $10,000.00, M3 $-10,000.00'):
   self.assertIn(part,r['answer'])
 def test_old_scenario(self):
  from test_yako_v1029_solver import PROMPT
  r=reason(PROMPT)
  self.assertIsNotNone(r)
  self.assertEqual(r['calculation']['feasible'],4)
  self.assertIn('**Decision:** B',r['answer'])
 def test_no_fabrication(self):self.assertIsNone(reason('Investment A costs $50. Investment B costs $60.'))
 def test_normalization(self):self.assertIn('Investment A:',normalize('Investment A costs $70'))
if __name__=='__main__':unittest.main()
