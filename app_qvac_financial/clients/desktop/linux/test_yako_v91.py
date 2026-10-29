import unittest
from yako_v91_engine import analyze_rules, build_prompt

class V91Tests(unittest.TestCase):
    def test_variable_monthly_rate(self):
        for value in (25, 30, 40):
            report = analyze_rules(f'Retorno garantido de {value}% ao mês')
            matches = [x for x in report['rules']['findings'] if x['flag'] == 'Extraordinary promised monthly return']
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0]['rate_percent_monthly'], value)
            self.assertIn(f'{value}%', matches[0]['evidence'])
    def test_no_invented_rate(self):
        report = analyze_rules('Retorno garantido sem percentual declarado')
        self.assertFalse(any(x['flag'] == 'Extraordinary promised monthly return' for x in report['rules']['findings']))
    def test_prompt_evidence(self):
        scenario = 'Retorno garantido de 30% ao mês'
        prompt = build_prompt(scenario, analyze_rules(scenario))
        self.assertIn('30%', prompt)
        self.assertIn('não recuse', prompt)
        self.assertIn('FATOS', prompt)
    def test_v9_unchanged(self):
        from yako_v9_engine import analyze_rules as v9
        self.assertEqual(v9('garantido 25% ao mês')['schema'], 'ai-yako-v9-evidence-1')

if __name__ == '__main__': unittest.main()
