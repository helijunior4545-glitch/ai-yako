import unittest
from yako_v1027_validation import validate_financial_response as v

class ValidationTests(unittest.TestCase):
    def test_three_term_surplus(self):
        q='Revenue $310,000, operating expenses $245,000, debt $35,000.'
        self.assertTrue(v('Monthly surplus is $30,000.',q)['accepted'])
    def test_unfounded_number_rejected(self):
        self.assertFalse(v('Surplus is $50,000.','Revenue $310,000, expenses $245,000, debt $35,000.')['accepted'])
    def test_exact_input(self):
        self.assertTrue(v('Revenue is $310,000.','Revenue $310,000.')['accepted'])
    def test_percentage(self):
        self.assertTrue(v('Expected result is $80,000.','Investment $100,000 with 80% chance.')['accepted'])
    def test_unfounded_percentage(self):
        self.assertFalse(v('Margin is 77%.','Revenue $310,000, expenses $245,000.')['accepted'])
    def test_no_numbers(self):
        self.assertTrue(v('Cash flow differs from profit.','Explain profit and cash flow.')['accepted'])
    def test_european_format(self):
        self.assertTrue(v('Saldo: R$ 30.000,00.','Receita R$ 310.000,00, custos R$ 245.000,00 e dívida R$ 35.000,00.')['accepted'])
    def test_diagnostic(self):
        r=v('Cash: $999,999.','Cash: $100,000.')
        self.assertEqual(r['reason'],'unverified_financial_figures')
        self.assertEqual(r['unverified_figures'],['$999,999'])
if __name__=='__main__':unittest.main()
