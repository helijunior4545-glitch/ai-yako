import unittest
from pathlib import Path
class ThemeTests(unittest.TestCase):
 def test_graphite(self):
  css=Path(__file__).with_name('yako_v102_ui.css').read_text()
  self.assertIn('--bg:#101112',css)
  self.assertIn('--accent:#c9ff47',css)
 def test_html(self):
  html=Path(__file__).with_name('yako_v102_ui.html').read_text()
  self.assertIn('1034-unified',html)
  self.assertIn('id="send"',html)
if __name__=='__main__':unittest.main()
