"""Yako V10.23 portfolio reasoning: bounded, evidence-first, Decimal arithmetic."""
import re
from decimal import Decimal
from itertools import combinations

MONEY=r'(?:R\$|BRL|\$)\s*([\d,.]+)'
def dec(s):
 s=s.strip()
 if ',' in s and '.' in s:s=s.replace('.','').replace(',','.') if s.rfind(',')>s.rfind('.') else s.replace(',','')
 elif ',' in s:s=s.replace(',','.') if len(s.split(',')[-1])!=3 else s.replace(',','')
 elif '.' in s and len(s.split('.')[-1])==3:s=s.replace('.','')
 return Decimal(s)
def find_money(text,pat):
 m=re.search(pat+r'\s*(?:of|is|:|=|de|em)?\s*'+MONEY,text,re.I)
 return dec(m.group(1)) if m else None
def percent(text):
 m=re.search(r'(?:probability of success|success probability|probabilidade de sucesso|chance of success)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*%',text,re.I)
 if not m:m=re.search(r'(\d+(?:\.\d+)?)\s*%\s*(?:probability of success|chance of success|de sucesso)',text,re.I)
 if m:return Decimal(m.group(1))/100
 m=re.search(r'(?:probability of failure|failure probability|probabilidade de fracasso)\s*(?:is|:|=)?\s*(\d+(?:\.\d+)?)\s*%',text,re.I)
 return 1-Decimal(m.group(1))/100 if m else None
def fmt(x):return 'BRL '+format(x,',.2f')
def analyze_portfolio(text,locale='en'):
 # Require explicitly separated projects. Do not invent a portfolio from a single investment.
 heads=list(re.finditer(r'(?im)^\s*(?:\*\*)?\s*(?:investment|investimento|project|projeto)\s+([A-Z]|\d+)\s*(?:[—–:-]|\*\*)',text))
 if len(heads)<2:return None
 if len(heads)>12:return None
 company=text[:heads[0].start()]
 cash=find_money(company,r'(?:available\s+cash|cash|caixa\s+dispon[ií]vel)')
 revenue=find_money(company,r'(?:monthly\s+revenue|receita\s+mensal)')
 expenses=find_money(company,r'(?:monthly\s+operating\s+expenses|monthly\s+expenses|despesas\s+mensais)')
 debt=find_money(company,r'(?:outstanding\s+debt|d[ií]vida\s+total)')
 repayments=find_money(company,r'(?:monthly\s+debt\s+repayments|monthly\s+debt\s+payments|parcelas\s+mensais\s+da\s+d[ií]vida)')
 if cash is None:return None
 projects=[]
 for i,h in enumerate(heads):
  chunk=text[h.end():heads[i+1].start() if i+1<len(heads) else len(text)]
  # End project facts before generic numbered task requirements.
  chunk=re.split(r'(?im)^\s*(?:#{1,3}\s*)?(?:required analysis|critical requirements|an[aá]lise solicitada|requisitos)',chunk)[0]
  cost=find_money(chunk,r'(?:initial\s+investment|capital\s+required|investimento\s+inicial)')
  p=percent(chunk)
  extra_rev=find_money(chunk,r'(?:additional\s+monthly\s+revenue\s+if\s+successful|additional\s+monthly\s+revenue|receita\s+mensal\s+adicional)')
  extra_exp=find_money(chunk,r'(?:additional\s+monthly\s+operating\s+expenses\s+if\s+successful|additional\s+monthly\s+operating\s+expenses|despesas\s+operacionais\s+adicionais)')
  saving=find_money(chunk,r'(?:monthly\s+operating\s+cost\s+savings\s+if\s+successful|monthly\s+operating\s+cost\s+savings|monthly\s+cost\s+savings|economia\s+mensal)')
  delay=re.search(r'(?:begin|begins|starting|start|come[cç]am)\s+(?:after|in|ap[oó]s)\s+(\d+)\s+months?',chunk,re.I)
  if not delay:delay=re.search(r'(\d+)\s+months?\s+after',chunk,re.I)
  if cost is None:return None
  projects.append(dict(id=h.group(1),cost=cost,p=p,rev=extra_rev,exp=extra_exp,saving=saving,delay=int(delay.group(1)) if delay else None))
 if len({p['id'] for p in projects})!=len(projects):return None
 lines=['**VERIFIED MULTI-INVESTMENT ANALYSIS**','**Extracted facts and calculations — not model-generated figures.**',f'• Available cash: {fmt(cash)}']
 if revenue is not None:lines.append(f'• Monthly revenue: {fmt(revenue)}')
 if expenses is not None:lines.append(f'• Monthly operating expenses: {fmt(expenses)}')
 if debt is not None:lines.append(f'• Outstanding debt: {fmt(debt)}')
 if repayments is not None:lines.append(f'• Monthly debt repayments: {fmt(repayments)}')
 if revenue is not None and expenses is not None:
  op=revenue-expenses;lines.append(f'• Simplified monthly operating surplus: {fmt(op)} = revenue − expenses')
  if repayments is not None:lines.append(f'• Surplus after stated debt repayments: {fmt(op-repayments)} (before other unlisted adjustments)')
 lines.append('**PROJECT ECONOMICS**')
 for p in projects:
  lines.append(f'• Investment {p["id"]}: initial cost {fmt(p["cost"])}; cash if selected alone {fmt(cash-p["cost"])}')
  if p['p'] is not None:lines.append(f'  Success probability: {p["p"]*100:g}%')
  parts=[]
  if p['rev'] is not None:parts.append(('additional revenue',p['rev']))
  if p['exp'] is not None:parts.append(('additional expenses',p['exp']))
  if p['saving'] is not None:parts.append(('cost savings',p['saving']))
  for k,v in parts:lines.append(f'  {k}: {fmt(v)} if successful')
  if parts:
   contribution=(p['rev'] or 0)-(p['exp'] or 0)+(p['saving'] or 0)
   p['contribution']=contribution
   lines.append(f'  Conditional incremental monthly operating contribution: {fmt(contribution)}')
   if p['p'] is not None:
    p['expected']=contribution*p['p'];lines.append(f'  Probability-weighted monthly contribution: {fmt(p["expected"])}')
  if p['delay'] is not None:lines.append(f'  Benefits begin after {p["delay"]} months (conditional).')
 # Parse explicitly stated project constraints, without inventing hidden conditions.
 constraints_text=text[heads[-1].end():]
 section=re.search(r'(?im)^\s*#{1,4}\s*(?:critical investment dependencies|critical requirements|investment dependencies|restri[cç][oõ]es|depend[eê]ncias)',constraints_text)
 if section:constraints_text=constraints_text[section.start():]
 reserve=find_money(company,r'(?:minimum\s+required\s+cash\s+reserve|minimum\s+cash\s+reserve|reserva\s+m[ií]nima\s+de\s+caixa)')
 if reserve is None:reserve=find_money(constraints_text,r'(?:at least|minimum of|minimum|required|pelo menos)') if re.search(r'(?i)(?:cash|caixa|reserve|reserva)',constraints_text) else None
 ids={p['id'].upper() for p in projects}
 dependencies=[]; exclusions=[]; timing=[]
 for sentence in re.split(r'(?<=[.!?])\s+|\n+',constraints_text):
  sentence=sentence.strip().strip('* ')
  if not sentence:continue
  m=re.search(r'(?i)investment\s+([A-Z])\s+cannot\s+be\s+implemented\s+unless\s+investment\s+([A-Z])\s+is\s+also\s+implemented',sentence)
  if m and set(m.groups())<=ids:dependencies.append(tuple(m.groups()));continue
  m=re.search(r'(?i)investments?\s+([A-Z])\s+and\s+([A-Z])\s+cannot\s+be\s+implemented\s+simultaneously',sentence)
  if m and set(m.groups())<=ids:exclusions.append(tuple(m.groups()));continue
  m=re.search(r'(?i)investment\s+([A-Z])\s+must\s+be\s+completed\s+before\s+investment\s+([A-Z])\s+can\s+begin',sentence)
  if m and set(m.groups())<=ids:timing.append(tuple(m.groups()))
 lines.append('**CAPITAL ALLOCATION — ALL SUBSETS**')
 feasible=[];infeasible=[]
 if len(projects)<=8:
  lines.append(f'• Neither: {fmt(cash)} remaining; additional monthly contribution {fmt(Decimal(0))}; FEASIBLE')
  feasible.append(('Neither',cash,Decimal(0)))
  for size in range(1,len(projects)+1):
   for group in combinations(projects,size):
    used=sum((p['cost'] for p in group),Decimal(0));remain=cash-used
    label=' + '.join(p['id'] for p in group)
    detail=f'• {label}: {fmt(remain)} remaining; committed {used/cash*100:.2f}%' if cash else f'• {label}: {fmt(remain)} remaining'
    if all('expected' in p for p in group):detail+=f'; expected incremental monthly contribution {fmt(sum((p["expected"] for p in group),Decimal(0)))} once all benefits begin'
    selected={p['id'].upper() for p in group};violations=[]
    if remain<0:violations.append('insufficient available cash')
    if reserve is not None and remain<reserve:violations.append('minimum cash reserve '+fmt(reserve))
    for dependent,required in dependencies:
     if dependent in selected and required not in selected:violations.append(f'{dependent} requires {required}')
    for left,right in exclusions:
     if left in selected and right in selected:violations.append(f'{left} and {right} mutually exclusive')
    expected=sum((p['expected'] for p in group),Decimal(0)) if all('expected' in p for p in group) else None
    if violations:detail+='; INFEASIBLE — '+', '.join(violations);infeasible.append((label,violations))
    else:
     detail+='; FEASIBLE';feasible.append((label,remain,expected))
    lines.append(detail)
 else:lines.append('• More than 8 projects: exhaustive combinations omitted to prevent exponential computation.')
 lines.append('**CONSTRAINT VERIFICATION AND DECISION**')
 lines.append(f'• Feasible allocations: {len(feasible)}; infeasible allocations: {len(infeasible)}.')
 if reserve is not None:lines.append(f'• Mandatory post-investment cash reserve: {fmt(reserve)}.')
 for dependent,required in dependencies:lines.append(f'• Dependency: {dependent} requires {required}.')
 for left,right in exclusions:lines.append(f'• Mutual exclusion: {left} and {right} cannot be selected together.')
 for first,second in timing:lines.append(f'• Scheduling: {first} must finish before {second} starts. Project completion durations are not provided; exact benefit dates cannot be derived.')
 candidates=[f for f in feasible if f[2] is not None]
 if candidates:
  best=max(candidates,key=lambda row:(row[2],row[1]))
  lines.append(f'• Highest expected monthly incremental operating contribution among feasible combinations: {best[0]} — {fmt(best[2])}; remaining cash {fmt(best[1])}.')
  liquid=max(candidates,key=lambda row:row[1])
  lines.append(f'• Maximum-liquidity feasible choice: {liquid[0]} — remaining cash {fmt(liquid[1])}. This is not automatically the lowest-risk or best investment decision.')
  if reserve is not None:lines.append(f'• Reserve headroom of maximum-contribution allocation: {fmt(best[1]-reserve)}.')
  lines.append('• Decision: maximum expected monthly contribution is not automatically the best choice; compare liquidity headroom, implementation delays, downside outcomes and missing cash-flow data.')
 if not (dependencies or exclusions or reserve is not None):lines.append('• No machine-verifiable dependency or minimum-reserve rule was extracted; do not assume none exist.')
 lines.append('**RISK AND DECISION FRAMEWORK**')
 lines.append('• Preserve liquidity for debt service and operating obligations. Cash divided by monthly expenses is not a reliable survival forecast.')
 lines.append('• Probability-weighted operating contributions are not profit, NPV, payback, or free cash flow. They exclude initial capital, timing, taxes and unknown cash-flow adjustments.')
 lines.append('• Joint success probability is NOT identifiable without a dependence assumption. If explicitly assuming independent outcomes, multiply individual probabilities; independence is not established by these facts.')
 lines.append('• Compare feasible allocations and consider sequencing projects to reduce simultaneous capital exposure. No unconditional approval follows from these figures.')
 lines.append('• Reliable NPV/payback requires a forecast horizon, discount rate, project-specific cash conversion, tax and working-capital effects, and terminal or residual values.')
 missing=[]
 if repayments is None:missing.append('monthly debt service')
 if any(p['p'] is None for p in projects):missing.append('success probabilities for all projects')
 if any('contribution' not in p for p in projects):missing.append('project operating contributions')
 if missing:lines.append('• Missing for complete evaluation: '+', '.join(missing)+'.')
 answer='\n\n'.join(lines)
 return {'answer':answer,'engine':'Yako V10.24 · constraint-aware verified analysis · Decimal','model_used':False,'total_seconds':0,'calculation':{'alternatives':2**len(projects),'feasible':len(feasible),'infeasible':len(infeasible),'constraints':{'dependencies':dependencies,'exclusions':exclusions,'timing':timing,'minimum_reserve':str(reserve) if reserve is not None else None}},'facts':{'project_count':len(projects),'available_cash':str(cash)}}
