"""Bounded, deterministic English cash-flow analysis. Never impersonates QVAC inference."""
import re
from decimal import Decimal

MONEY=r'\$\s*([\d,]+(?:\.\d{1,2})?)'
def extract(text,patterns):
    for pat in patterns:
        m=re.search(pat,text,re.I|re.S)
        if m:return Decimal(m.group(1).replace(',',''))
    return None

def fmt(n):return f'${n:,.2f}'

def explain_concept(text,locale='en'):
    t=text.lower()
    if locale!='en' or not ('revenue' in t and 'profit' in t) or not re.search(r'\b(difference|explain|define|what is)\b',t):return None
    if re.search(r'\$|\d{3,}',text):return None
    answer='Revenue is the total value of sales before expenses. Profit is the amount remaining after relevant expenses, under the applicable accounting method.'
    if 'cash flow' in t or 'cash-flow' in t:answer+=' Cash flow is the actual movement of cash into and out of the business over a period.'
    if 'example' in t:answer+=' Example: a business records $10,000 in sales and $7,000 in expenses, giving $3,000 accounting profit under simplified assumptions. If only $6,000 of those sales were collected in cash during that period, cash receipts differ from recorded revenue; net cash flow also depends on actual cash payments.'
    return {'answer':answer,'engine':'Verified local financial definitions (not QVAC inference)','model_used':False,'inference_executed':False}

def analyze_natural_finance(text,locale='en'):
    if locale!='en':return None
    t=text.lower()
    if not any(x in t for x in ('company','business','cash flow','cash-flow','monthly revenue')):return None
    cash=extract(text,[rf'(?:have|has|currently have|cash balance is|cash on hand is|available cash(?: of)?|in the bank(?: is)?)\s*(?:about|approximately|around)?\s*{MONEY}',rf'{MONEY}\s+(?:in (?:the )?bank|in (?:available )?cash|cash on hand)'])
    revenue=extract(text,[rf'(?:monthly revenue(?: of| is)?|revenue of|earns?|customers pay us|receive(?:s)?|sales(?: of| are)?)\s*(?:us )?(?:about|approximately|around|of)?\s*{MONEY}(?:\s*(?:every|per|a)\s*month)?',rf'{MONEY}\s*(?:in monthly revenue|per month in revenue)'])
    expense=extract(text,[rf'(?:operating expenses(?: total| of| are)?|expenses(?: total| of| are)?|spends?|salaries, rent, and other operating expenses total)\s*(?:about|approximately|around|of)?\s*{MONEY}',rf'{MONEY}\s*(?:in (?:monthly )?(?:operating )?expenses|on operations)'])
    debt=extract(text,[rf'(?:loan payment(?: of| is)?|debt payments?(?: of| are)?|pays?\s+(?:about\s+)?(?:a\s+)?(?:monthly\s+)?(?:debt|loan)(?:\s+payment)?(?:\s+of)?)\s*(?:about|approximately|around)?\s*{MONEY}',rf'{MONEY}\s*(?:in (?:monthly )?(?:debt|loan) payments?|in monthly debt)'])
    if revenue is None or expense is None:return None
    if debt is None:
        if re.search(r'\b(debt|loan|repayment)\b',t):return None
        debt=Decimal(0)
    flow=revenue-expense-debt
    lines=['**Verified cash-flow analysis (deterministic, not QVAC inference)**',f'Monthly revenue: {fmt(revenue)}; operating expenses: {fmt(expense)}; stated monthly debt payments: {fmt(debt)}.',f'Monthly net cash flow (assuming these amounts represent cash receipts/payments): {fmt(revenue)} − {fmt(expense)} − {fmt(debt)} = {fmt(flow)}.']
    if cash is not None:
        lines.append(f'Current cash: {fmt(cash)}.')
        if flow<0:lines.append(f'Simplified cash runway without new changes: {fmt(cash)} / {fmt(-flow)} = {cash/-flow:.2f} months. Actual timing may differ.')
        else:lines.append('No positive cash-burn runway can be calculated from the stated monthly figures.')
    cost=extract(text,[rf'(?:equipment|investment|machine)(?:\s+(?:for|costs?|price(?:d)? at|priced at))\s*{MONEY}',rf'{MONEY}\s*(?:for (?:new )?equipment|equipment cost)'])
    pct=re.search(r'(?:increase|boost|raise)\s+(?:our\s+)?(?:monthly\s+)?revenue\s+by\s+(\d+(?:\.\d+)?)\s*%',text,re.I)
    if cost is not None and cash is not None:
        after=cash-cost;lines.append(f'If the purchase is paid immediately: {fmt(cash)} − {fmt(cost)} = {fmt(after)} remaining cash.')
        if flow<0 and after>=0:lines.append(f'Without any benefit, simplified post-purchase runway: {after/-flow:.2f} months.')
        if after<0:lines.append('The purchase exceeds current cash; financing is not assumed.')
    if pct:
        benefit=revenue*Decimal(pct.group(1))/100
        lines.append(f'Claimed {pct.group(1)}% revenue increase would equal {fmt(benefit)} additional monthly revenue IF achieved; this is not necessarily profit or collected cash.')
        lines.append(f'Illustrative monthly flow assuming all extra revenue becomes cash with no new costs: {fmt(flow)} + {fmt(benefit)} = {fmt(flow+benefit)}. This is an optimistic assumption, not a forecast.')
    if cost is not None:lines.append('Decision: do not treat an unverified supplier claim as sufficient justification. Confirm timing, evidence, maintenance/implementation costs, payment terms, and the cash-conversion rate before deciding.')
    lines.append('Limitations: assumes stated monthly figures are comparable cash amounts; excludes taxes, working capital changes and payment timing unless supplied.')
    return {'answer':'\n'.join(lines),'engine':'Verified local cash-flow parser (not QVAC inference)','model_used':False,'inference_executed':False}
