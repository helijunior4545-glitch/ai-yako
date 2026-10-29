"""V10.1 smoke tests; real QVAC inference must be tested on target Linux."""
import unittest
from yako_v10_core import analyze, simulate
import yako_v101_desktop as ui

class WorkstationTests(unittest.TestCase):
    def test_evidence_rate(self):
        r=analyze('Promessa de lucro garantido de 30% ao mês')
        self.assertIn(30.0,[f['rate_percent_monthly'] for f in r['findings'] if 'rate_percent_monthly' in f])
    def test_simulation(self):
        self.assertEqual(simulate('1000','10',2)['final_balance'],1210)
    def test_ui_pages(self):
        self.assertEqual(len(ui.PAGES),6)
        self.assertTrue(callable(ui.App.page_ai_intelligence))
        self.assertTrue(callable(ui.App.page_model_center))
    def test_readonly_design(self):
        self.assertNotIn('wallet',ui.PAGES)

if __name__=='__main__':unittest.main()
