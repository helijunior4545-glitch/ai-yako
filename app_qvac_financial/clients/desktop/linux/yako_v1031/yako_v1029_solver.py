"""V10.29 bounded, evidence-first investment scenario solver. No external services."""
import re
from decimal import Decimal
from itertools import combinations
from yako_v1027_validation import _number
MONEY=r'(?:US\$|R\$|\$|USD\s*|BRL\s*)\s*([\d,.]+(?:\s*(?:million|mil|k|m))?)'
def amount(s):
 m=re.search(MONEY,s,re.I)
 return _number(m.group(0)) if m else None
def fact(text,pattern):
 m=re.search(pattern+r'\s*(?:is|of|are|:|=|de|em)?\s*'+MONEY,text,re.I)
 return amount(m.group(0)) if m else None
def fmt(n):return '${:,.2f}'.format(n)
def solve(text,locale='en'):
 if not isinstance(text,str) or len(text)>20000:return None
 # Accept headings inside a single flattened paragraph, but do not confuse references to investments with definitions.
 head=r'\b(?:investment|investimento|project|projeto)\s+([A-Z])\s*:\s*'
 heads=list(re.finditer(head,text,re.I))
 if not 2<=len(heads)<=10:return None
 if len(set(h.group(1).upper() for h in heads))!=len(heads):return None
 company=text[:heads[0].start()]
 cash=fact(company,r'(?:available\s+cash|cash\s+available|caixa\s+dispon[ií]vel)')
 revenue=fact(company,r'(?:monthly\s+revenue|receita\s+mensal)')
 expenses=fact(company,r'(?:operating\s+expenses|despesas\s+operacionais)')
 debt=fact(company,r'(?:debt\s+payments?\s+(?:are\s+)?per\s+month|debt\s+payments?|pagamentos?\s+mensais\s+da\s+d[ií]vida)')
 if cash is None:
  m=re.search(MONEY+r'\s+in\s+available\s+cash',company,re.I)
  if m:cash=amount(m.group(0))
 if cash is None:return None
 # Terminate the last project at explicit restrictions/analysis sections.
 end=re.search(r'\b(?:there\s+are\s+\w+\s+restrictions?|restrictions?\s*:|constraints?\s*:|restri[cç][oõ]es\s*:|analyze\s+every|analise\s+todas)\b',text[heads[-1].end():],re.I)
 last_end=heads[-1].end()+(end.start() if end else len(text)-heads[-1].end())
 projects=[]
 for i,h in enumerate(heads):
  chunk=text[h.end():(heads[i+1].start() if i+1<len(heads) else last_end)]
  cost=fact(chunk,r'(?:costs?|initial\s+cost|custa|investimento\s+inicial)')
  if cost is None:return None
  rev=fact(chunk,r'(?:additional|extra|adicional)\s*'+r'(?:monthly\s+)?(?:revenue|receita)')
  # Accept "generates an additional $X in monthly revenue" and similar structures.
  if rev is None:
   m=re.search(r'(?:generates?|gera)\s+(?:an?\s+)?(?:additional|extra|adicional)\s+'+MONEY+r'\s+(?:in\s+)?(?:monthly\s+)?(?:revenue|receita)',chunk,re.I)
   if m:rev=amount(m.group(0))
  extra=fact(chunk,r'(?:increases?|aumenta)\s+(?:monthly\s+)?(?:operating\s+)?(?:expenses|despesas)\s+by')
  saving=fact(chunk,r'(?:reduces?|decreases?|reduz|diminui)\s+(?:monthly\s+)?(?:operating\s+)?(?:expenses|despesas)\s+by')
  debt_save=fact(chunk,r'(?:reduces?|decreases?|reduz|diminui)\s+(?:monthly\s+)?(?:debt\s+payments?|pagamentos?\s+da\s+d[ií]vida)\s+by')
  # Strictly require an identifiable benefit, never invent unknown economics.
  if all(x is None for x in (rev,extra,saving,debt_save)):return None
  delay=re.search(r'(?:after|ap[oó]s)\s+(\d+)\s+(?:months?|meses)',chunk,re.I)
  if not delay:
   word_delay=re.search(r'(?:after|ap[oó]s)\s+(one|two|three|four|five|six|seven|eight|nine|ten)\s+months?',chunk,re.I)
   word_months={'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10}
  else:word_delay=None
  starts_now=bool(re.search(r'(?:starting|starts?|beginning)\s+immediately|imediatamente',chunk,re.I))
  projects.append(dict(id=h.group(1).upper(),cost=cost,improvement=(rev or 0)-(extra or 0)+(saving or 0)+(debt_save or 0),delay=int(delay.group(1)) if delay else (word_months[word_delay.group(1).lower()] if word_delay else 0),starts_now=starts_now))
 tail=text[last_end:]
 reserve=None
 for pattern in [r'(?:maintain|keep|preserve|manter|preservar)\s+(?:at\s+least|pelo\s+menos)\s*'+MONEY+r'\s+(?:in\s+)?(?:available\s+)?cash',r'(?:minimum\s+(?:cash\s+)?reserve|reserva\s+m[ií]nima)\s*(?:of|de|:)?\s*'+MONEY]:
  m=re.search(pattern,tail,re.I)
  if m:reserve=amount(m.group(0));break
 # Never claim to solve constraints when the reserve is mentioned but cannot be extracted.
 if re.search(r'(?:minimum\s+cash\s+reserve|at\s+least.{0,40}cash|reserva\s+m[ií]nima)',tail,re.I) and reserve is None:return None
 exclusions=set()
 for m in re.finditer(r'investments?\s+([A-Z])\s+and\s+([A-Z])\s+cannot\s+be\s+(?:selected|implemented|chosen)\s+together|investimentos?\s+([A-Z])\s+e\s+([A-Z])\s+n[aã]o\s+podem\s+ser\s+selecionados\s+juntos',tail,re.I):
  pair=[x.upper() for x in m.groups() if x];exclusions.add(frozenset(pair))
 # If text contains unrecognized prohibitions, do not silently ignore them.
 prohibition_count=len(re.findall(r'\bcannot\s+be\s+selected\s+together\b|\bn[aã]o\s+podem\s+ser\s+selecionados\s+juntos\b',tail,re.I))
 if prohibition_count>len(exclusions):return None
 ids={p['id'] for p in projects}
 if any(not pair<=ids for pair in exclusions):return None
 baseline=revenue-expenses-debt if None not in (revenue,expenses,debt) else None
 rows=[]
 for k in range(len(projects)+1):
  for group in combinations(projects,k):
   selected={p['id'] for p in group};spent=sum((p['cost'] for p in group),Decimal(0));remaining=cash-spent
   reasons=[]
   if remaining<0:reasons.append('insufficient cash')
   if reserve is not None and remaining<reserve:reasons.append('minimum reserve breached')
   if any(pair<=selected for pair in exclusions):reasons.append('mutual exclusion')
   improvement=sum((p['improvement'] for p in group),Decimal(0))
   # For multi-project combinations with different starts, total improvement is steady-state only.
   payback=None
   if group and improvement>0:
    elapsed=0;recovered=Decimal(0)
    for month in range(1,1201):
     month_gain=sum((p['improvement'] for p in group if month>p['delay']),Decimal(0))
     if month_gain<=0:continue
     if recovered+month_gain>=spent:
      payback=Decimal(month-1)+(spent-recovered)/month_gain;break
     recovered+=month_gain
   rows.append(dict(label=' + '.join(sorted(selected)) if selected else 'None',remaining=remaining,improvement=improvement,payback=payback,violations=reasons))
 feasible=[r for r in rows if not r['violations']]
 lines=['**YAKO V10.29 — VERIFIED INVESTMENT CONSTRAINT ANALYSIS**','Deterministic Decimal calculations; no QVAC inference required. Currency assumed USD from the $ amounts.']
 lines.append('Available cash: '+fmt(cash)+'.'+(' Minimum immediate cash reserve: '+fmt(reserve)+'.' if reserve is not None else ''))
 if baseline is not None:lines.append('Baseline monthly surplus after stated debt payments: '+fmt(baseline)+'. This is a monthly flow, not a cash reserve.')
 lines.append('**All investment combinations**')
 for r in rows:
  status='FEASIBLE' if not r['violations'] else 'INFEASIBLE ('+', '.join(r['violations'])+')'
  pay='n/a' if r['payback'] is None else f'{r["payback"]:.2f} months'
  lines.append(f'- {r["label"]}: remaining cash {fmt(r["remaining"])}; steady-state monthly improvement {fmt(r["improvement"])}; simple payback {pay}; {status}.')
 candidates=[r for r in feasible if r['payback'] is not None]
 if candidates:
  best=min(candidates,key=lambda r:(r['payback'],-r['remaining']))
  lines.append('**Decision:** '+best['label']+' has the shortest estimated simple payback among feasible investments, with '+fmt(best['remaining'])+' cash remaining. This is not proof of lowest risk or highest NPV.')
 lines.append('Payback is measured from investment date; a benefit starting after 3 months first contributes in month 4. The payback calculation assumes stated improvements are constant and realized as cash flows.')
 lines.append('**Limits:** No taxes, working capital, demand uncertainty, financing changes, discount rate or implementation costs were supplied. These risks cannot be quantified from the prompt.')
 return {'answer':'\n\n'.join(lines),'engine':'Yako V10.29 · deterministic constraint solver · Decimal','model_used':False,'inference_executed':False,'response_accepted':True,'total_seconds':0,'calculation':{'alternatives':len(rows),'feasible':len(feasible),'infeasible':len(rows)-len(feasible),'minimum_reserve':str(reserve) if reserve is not None else None},'facts':{'project_count':len(projects),'available_cash':str(cash)}}
