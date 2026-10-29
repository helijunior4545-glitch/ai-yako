import unittest
from pathlib import Path
from yako_v1028_consistency import review_financial_consistency
class ConsistencyTests(unittest.TestCase):
 def test_reserve_confusion(self):
  r=review_financial_consistency('It means the company has $30,000 in cash reserves.','Calculate the monthly cash surplus.','en')
  self.assertIn('surplus_confused_with_reserves',r['flags']);self.assertIn('opening cash balance is unknown',r['answer'])
 def test_cost_direction(self):
  r=review_financial_consistency('If there is a decrease in operational costs, its cash surplus might decrease.','Explain the surplus.','en')
  self.assertIn('expense_direction_inverted',r['flags'])
 def test_no_false_reserve_flag(self):
  r=review_financial_consistency('The company has a $30,000 monthly surplus, but its cash reserves are unknown.','Calculate monthly surplus.','en')
  self.assertNotIn('surplus_confused_with_reserves',r['flags'])
 def test_simple_answer(self):
  r=review_financial_consistency('The total is $30,000.','Calculate 310000 minus 280000.','en')
  self.assertFalse(r['repaired'])
 def test_assets(self):
  h=Path(__file__).with_name('yako_v102_ui.html').read_text()
  j=Path(__file__).with_name('yako_v102_ui.js').read_text()
  c=Path(__file__).with_name('yako_v102_ui.css').read_text()
  self.assertIn('id="railToggle"',h);self.assertIn('rail-width:76px',c);self.assertIn('yako-sidebar-open',j)
if __name__=='__main__':unittest.main()
