import unittest
from pathlib import Path
class V1032Integrity(unittest.TestCase):
 def test_diagnostic_stage_and_rejection(self):
  s=(Path(__file__).parent/'yako_v102_server.py').read_text()
  self.assertIn('error_stage',s)
  self.assertIn('model_output_characters',s)
 def test_composer_clearance(self):
  j=(Path(__file__).parent/'yako_v102_ui.js').read_text()
  self.assertIn('(height+8)',j)
  self.assertIn('qvac_error',j)
 def test_tighter_spacing(self):
  c=(Path(__file__).parent/'yako_v102_ui.css').read_text()
  self.assertIn('V10.32: subtle tighter',c)
