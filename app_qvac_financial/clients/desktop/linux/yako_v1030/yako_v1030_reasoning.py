"""Bounded local financial reasoning pipeline: normalize -> solve -> audit -> explain.
No LLM inference, no network, no speculative inputs. Financial scope intentionally narrow.
"""
import re
from decimal import Decimal
from yako_v1029_solver import solve

def normalize(text):
    if not isinstance(text,str) or len(text)>20000:return None
    t=' '.join(text.split())
    # Normalize recognized project definition styles without changing monetary facts.
    t=re.sub(r'\b(Investment|Investimento|Project|Projeto)\s+([A-Z])\s+(?=costs?\s|custa\s)',r'\1 \2: ',t,flags=re.I)
    # The V10.29 solver requires an explicit tail delimiter; these are semantic equivalents.
    t=re.sub(r'\b(?:Three|Four|Two|Several)\s+opportunities\s+are\s+available\s*:', 'The following investments are available:',t,flags=re.I)
    # Move an early reserve requirement to the restrictions section without changing its terms.
    early=re.search(r'(?:The company|I) must maintain at least \$[\d,]+ in available cash immediately after (?:any )?invest(?:ment|ing)',t,re.I)
    if early and 'Investment A' in t and early.start()<t.find('Investment A'):
        clause=early.group(0);t=t[:early.start()]+t[early.end():]+' Restrictions: '+clause+'.'
    # V10.29 recognizes these exclusivity expressions.
    t=re.sub(r'\bInvestments?\s+([A-Z])\s+and\s+([A-Z])\s+cannot\s+be\s+combined\b',r'Investments \1 and \2 cannot be selected together',t,flags=re.I)
    # Ensure last investment ends before the constraints, avoiding accidental benefit parsing.
    t=re.sub(r'\bThe company must maintain\b','Restrictions: The company must maintain',t,flags=re.I)
    t=re.sub(r'\bInvestments?\s+([A-Z])\s+and\s+([A-Z])\s+cannot\s+be\s+selected\s+together\b',r'Investments \1 and \2 cannot be selected together',t,flags=re.I)
    return t

def _currency(v):return '${:,.2f}'.format(v)

def reason(text,locale='en'):
    t=normalize(text)
    if t is None:return None
    # Explicitly delimit restrictions following project descriptions.
    t=re.sub(r'(?<!Restrictions: )\b(Investments?\s+[A-Z]\s+and\s+[A-Z]\s+cannot\s+be\s+selected\s+together)',r'There are three restrictions \1',t,count=1,flags=re.I)
    # Alternative statement style: 'increases monthly revenue by $X'.
    t=re.sub(r'\bincreases\s+monthly\s+revenue\s+by\s+(\$[\d,.]+)',r'generates an additional \1 in monthly revenue',t,flags=re.I)
    result=solve(t,locale)
    if result is None:return None
    # The existing solver is the calculation authority; this stage adds cash-flow interpretation.
    baseline_match=re.search(r'Baseline monthly surplus after stated debt payments: \$(-?[\d,]+\.\d{2})',result['answer'])
    if not baseline_match:return result
    baseline=Decimal(baseline_match.group(1).replace(',',''))
    if baseline>=0:return result
    # Parse the solver's output, not the raw language model response.
    rows=[]
    for line in result['answer'].splitlines():
        m=re.search(r'^- (.+?): remaining cash \$(-?[\d,.]+); steady-state monthly improvement \$(-?[\d,.]+); .*?; (FEASIBLE|INFEASIBLE)',line)
        if m:
            rows.append({'name':m.group(1),'cash':Decimal(m.group(2).replace(',','')),'gain':Decimal(m.group(3).replace(',','')),'feasible':m.group(4)=='FEASIBLE'})
    if not rows:return result
    feasible=[r for r in rows if r['feasible']]
    restores=[r for r in feasible if baseline+r['gain']>=0]
    # A short investment payback does not establish corporate solvency.
    result['answer']=re.sub(r'\*\*Decision:\*\*[^\n]*', '**Investment-only payback:** These payback figures describe incremental benefits, not elimination of the company-wide deficit.', result['answer'])
    notes=['**Cash-flow resilience assessment**',
           'The company starts with a monthly cash-flow deficit of '+_currency(-baseline)+'.',
           'Steady-state surplus/deficit = baseline monthly cash flow + investment improvement.']
    for r in rows:
        notes.append('- '+r['name']+': steady-state monthly '+('surplus ' if baseline+r['gain']>=0 else 'deficit ')+_currency(abs(baseline+r['gain']))+'; '+('FEASIBLE' if r['feasible'] else 'INFEASIBLE')+'.')
    if not restores:
        notes.append('**Finding:** No feasible investment eliminates the monthly deficit. An infeasible combination must not be recommended as a solution.')
        candidates=[r for r in feasible if r['name']!='None']
        if candidates:
            # A recommendation cannot be based solely on the final steady-state deficit when timing differs.
            notes.append('**Decision:** No investment is demonstrated to be sustainable. Evaluate liquidity runway and benefit start dates before committing; preserving cash and reducing the operating deficit may be more defensible than investing.')
    else:
        notes.append('At least one immediately feasible option eliminates the steady-state deficit, but its timing and interim cash consumption must be evaluated separately.')
    notes.append('**Liquidity warning:** The minimum reserve is an immediate post-investment constraint, not a guarantee that cash remains above it in subsequent months.')
    # Timing matters: obtain delay from normalized project definition and project first 3 months for each feasible option.
    definitions=list(re.finditer(r'\b(?:investment|investimento|project|projeto)\s+([A-Z])\s*:',t,re.I))
    delays={}
    for i,h in enumerate(definitions):
        chunk=t[h.end():(definitions[i+1].start() if i+1<len(definitions) else len(t))]
        m=re.search(r'\bafter\s+(\d+|one|two|three|four|five|six)\s+months?\b',chunk,re.I)
        words={'one':1,'two':2,'three':3,'four':4,'five':5,'six':6}
        delays[h.group(1).upper()]=int(m.group(1)) if m and m.group(1).isdigit() else (words.get(m.group(1).lower(),0) if m else 0)
    # Infer individual improvements only from solver's verified single-project rows.
    single={r['name']:r['gain'] for r in rows if re.fullmatch('[A-Z]',r['name'])}
    notes.append('**Three-month illustrative cash projection** (assumes starting cash is current cash, investment paid now, and stated monthly cash flows realized at month-end):')
    for r in feasible:
        ids=[] if r['name']=='None' else r['name'].split(' + ')
        if any(x not in single for x in ids):continue
        cash=r['cash']; path=[]
        for month in range(1,4):
            gain=sum((single[x] for x in ids if month>delays.get(x,0)),Decimal(0))
            cash+=baseline+gain
            path.append('M'+str(month)+' '+_currency(cash))
        notes.append('- '+r['name']+': '+', '.join(path)+'.')
    notes.append('This is a conditional projection, not a forecast; taxes, payment timing, additional liabilities and implementation costs were not supplied.')
    result['answer']+='\n\n'+'\n'.join(notes)
    result['engine']='Yako V10.30 · bounded reasoning + deterministic constraint solver'
    result['reasoning_review']={'negative_baseline':True,'feasible_eliminates_deficit':bool(restores),'projection_months':3,'model_used':False}
    return result
