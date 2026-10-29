import unittest
from yako_v9_engine import analyze_rules, build_prompt

class V9Tests(unittest.TestCase):
    def test_guarantee(self):
        r = analyze_rules('Retorno garantido de 25% ao mês')
        flags = [x['flag'] for x in r['rules']['findings']]
        self.assertIn('Unrealistic guarantee', flags)
        self.assertIn('Extraordinary promised monthly return', flags)

    def test_empty(self):
        with self.assertRaises(ValueError):
            analyze_rules('  ')

    def test_no_execution(self):
        r = analyze_rules('Investimento comum')
        self.assertEqual(r['financial_execution'], 'DISABLED')
        self.assertFalse(r['network_isolation_verified'])

    def test_prompt(self):
        r = analyze_rules('guaranteed 25% monthly')
        self.assertIn('possible fraud', build_prompt('guaranteed 25% monthly', r))

if __name__ == '__main__':
    unittest.main()
