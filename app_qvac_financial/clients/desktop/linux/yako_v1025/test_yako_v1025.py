import unittest
from yako_v1025_reasoning import classify_request,build_reasoning_context,verified_fallback
class TestReasoning(unittest.TestCase):
 def test_open_question(self):
  s=build_reasoning_context('Why can a profitable business fail?')
  self.assertIn('profitable business fail?',s)
  self.assertIn('conceptual',s)
 def test_paraphrases(self):
  self.assertIn('liquidity',classify_request('Our overdue receivables threaten cash flow'))
  self.assertIn('credit',classify_request('Should we refinance the loan?'))
 def test_honest_fallback(self):
  self.assertIn('did not produce',verified_fallback('Why?'))
 def test_history(self):
  s=build_reasoning_context('What now?',history=[{'role':'user','content':'My previous question'}]);self.assertIn('My previous question',s)
if __name__=='__main__':unittest.main()
