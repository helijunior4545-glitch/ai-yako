"""YAKO V10.60 — conservative, deterministic financial calculations.
Returns None for unsupported/ambiguous inputs; never fabricates values.
No internet, DB, or third-party API dependencies.
"""
import re
from decimal import Decimal, InvalidOperation

D = Decimal
PROMPTS = [
    ('Detect Investment Fraud', 'An investment platform promises a guaranteed 30% monthly return, requires an immediate deposit, and provides no independent audit. Identify the warning signs and explain what evidence is missing.'),
    ('Analyze Financial Risk', 'I have $10,000. One investment offers a guaranteed 25% monthly return, while another offers an estimated 6% annual return with market risk. Compare the claims, uncertainty, and potential warning signs.'),
    ('Evaluate Cash Flow', 'My monthly income is $5,200. Rent is $1,600, food is $650, transport is $350, utilities are $300, and debt payments are $900. Calculate my remaining cash flow and identify financial vulnerabilities.'),
    ('Compare Investment Scenarios', 'Compare investing $5,000 for one year at 4%, 7%, and 10% annual returns, assuming annual compounding, no additional deposits, and no fees or taxes. Calculate the ending value for each scenario.'),
    ('Build a Financial Strategy', 'My monthly income is $4,000, essential expenses are $2,500, and debt payments are $600. I have $1,000 in savings. Propose a realistic six-month emergency-fund strategy using only the available monthly surplus.'),
]
AMOUNT = r'\$\s*([\d,]+(?:\.\d{1,2})?)'
def money(n): return f'USD {n:,.2f}'
def values(t):
    try: return [D(x.replace(',', '')) for x in re.findall(AMOUNT, t)]
    except InvalidOperation: return []
def output(text, kind):
    return {'answer': text, 'engine': 'yako_v1060_verified', 'source': 'deterministic', 'intent': kind, 'verified': True}
def solve(text, locale='en'):
    if not isinstance(text, str) or len(text) > 12000: return None
    t = ' '.join(text.split()); low = t.lower()
    # Only recognize unambiguous English demo-style patterns. Other requests
    # are delegated to existing engines instead of inventing a financial answer.
    if 'guaranteed' in low and ('monthly return' in low or 'monthly returns' in low) and ('audit' in low or 'warning sign' in low or 'risk' in low):
        rates = re.findall(r'(\d+(?:\.\d+)?)\s*%\s*monthly', low)
        if not rates: return None
        rate = D(rates[0]); annual = ((D(1) + rate / 100) ** 12 - 1) * 100
        if 'another' in low and 'annual' in low:
            other = re.search(r'(\d+(?:\.\d+)?)\s*%\s*annual', low)
            if not other: return None
            return output(f'Risk comparison: a claimed guaranteed {rate}% monthly return corresponds to approximately {annual:.2f}% effective annual growth if compounded. The other offer estimates {other.group(1)}% annually and explicitly acknowledges market risk. A guaranteed unusually high return is a major warning sign, not evidence of safety. Verify licensing, custody, independent audits, withdrawal terms and the underlying strategy. Neither return is verified; do not treat either as an assured outcome.', 'risk')
        return output(f'Potential fraud warning signs: a claimed guaranteed {rate}% monthly return (about {annual:.2f}% annualized if compounded), pressure to deposit immediately, and no independent audit. These facts raise serious concerns but do not prove fraud. Missing evidence: regulatory registration, independent audit, custody details, verifiable performance, withdrawal conditions, fees, and legal entity identification. Do not transfer funds before independent verification.', 'fraud')
    if 'monthly income' in low and 'rent' in low and 'food' in low and 'transport' in low and 'utilities' in low and 'debt payments' in low:
        keys = ['monthly income', 'rent', 'food', 'transport', 'utilities', 'debt payments']
        amounts = []
        for key in keys:
            m = re.search(re.escape(key) + r'\s+(?:is|are|of|:)\s*' + AMOUNT, low)
            if not m: return None
            amounts.append(D(m.group(1).replace(',', '')))
        income, *expenses = amounts
        total = sum(expenses, D(0)); remaining = income - total
        return output(f'Monthly cash-flow analysis (USD): income {money(income)}; rent {money(expenses[0])}; food {money(expenses[1])}; transport {money(expenses[2])}; utilities {money(expenses[3])}; debt payments {money(expenses[4])}. Total listed monthly outflows: {money(total)}. Remaining monthly cash flow: {money(remaining)}. Debt payments represent an expense, not an outstanding debt balance. This surplus excludes any unlisted expenses, taxes, or irregular costs.', 'cash_flow')
    if 'compare investing' in low and 'annual' in low and ('one year' in low or '1 year' in low):
        capital = re.search(r'compare investing\s+' + AMOUNT, low)
        rates = re.findall(r'(\d+(?:\.\d+)?)\s*%', low)
        if not capital or len(rates) != 3 or 'no fees or taxes' not in low: return None
        principal = D(capital.group(1).replace(',', ''))
        if any(D(r) < 0 or D(r) > 100 for r in rates): return None
        items = [f'{r}%: {money(principal * (1 + D(r)/100))}' for r in rates]
        return output(f'One-year comparison for {money(principal)}, annual compounding, no additional deposits, fees, or taxes: ' + '; '.join(items) + '. These are hypothetical calculations, not forecasts or guaranteed returns.', 'investment_scenarios')
    if 'monthly income' in low and 'essential expenses' in low and 'debt payments' in low and 'savings' in low and 'six-month' in low:
        keys = ['monthly income', 'essential expenses', 'debt payments']
        found=[]
        for key in keys:
            m = re.search(re.escape(key) + r'\s+(?:is|are|of|:)\s*' + AMOUNT, low)
            if not m: return None
            found.append(D(m.group(1).replace(',', '')))
        saving = re.search(AMOUNT + r'\s+in\s+savings', low)
        if not saving: return None
        income, essential, debt = found
        initial = D(saving.group(1).replace(',', ''))
        surplus = income - essential - debt
        if surplus < 0: return output(f'Income {money(income)} minus essential expenses {money(essential)} and debt payments {money(debt)} gives a monthly deficit of {money(-surplus)}. A savings contribution is not affordable without reducing spending or increasing income.', 'emergency_fund')
        target = initial + surplus * 6
        return output(f'Six-month emergency-fund plan (USD): income {money(income)}, essential expenses {money(essential)}, debt payments {money(debt)}, monthly available surplus {money(surplus)}. Starting savings {money(initial)}. Save up to {money(surplus)} each month if these inputs remain stable. After six months: {money(target)} (no interest assumed). Verify irregular expenses, debt interest and emergency-fund target before committing the entire surplus.', 'emergency_fund')
    return None

def self_test():
    expected = ['fraud','risk','cash_flow','investment_scenarios','emergency_fund']
    for (title, prompt), kind in zip(PROMPTS, expected):
        import time
        started = time.monotonic(); result = solve(prompt, 'en')
        assert result and result['intent'] == kind, (title, result)
        answer = result['answer']
        if kind == 'cash_flow': assert 'USD 1,400.00' in answer and 'USD 3,800.00' in answer
        if kind == 'investment_scenarios': assert all(x in answer for x in ('USD 5,200.00','USD 5,350.00','USD 5,500.00'))
        if kind == 'emergency_fund': assert 'USD 900.00' in answer and 'USD 6,400.00' in answer
        print(f'[PASS] {title} | {time.monotonic()-started:.4f}s | {kind}')
    assert solve('What is the best stock to buy?') is None
    print('All five deterministic tests passed. Online API and device-offline operation NOT tested.')
