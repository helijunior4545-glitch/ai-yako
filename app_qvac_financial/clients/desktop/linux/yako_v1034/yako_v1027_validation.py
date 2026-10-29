"""Financial figure guard: permit explicit inputs and provable small arithmetic, not invented figures.

Conservative by design: ambiguous monetary units, unstated assumptions and
complex forecasts are NOT verified by this module. Deterministic tools should
handle complex financial projections separately.
"""
import re
from decimal import Decimal, InvalidOperation
from itertools import combinations, product

FIGURE = re.compile(r'(?<!\w)(?:R\$|US\$|\$|BRL\s*|USD\s*)\s*\d[\d.,]*(?:\s*(?:k|m|million|milh(?:ão|ões)|mil))?|(?<!\w)\d[\d.,]*\s*%', re.I)


def _number(raw):
    s=re.sub(r'^(?:R\$|US\$|\$|BRL\s*|USD\s*)\s*','',raw.strip(),flags=re.I)
    is_pct=s.endswith('%')
    if is_pct:s=s[:-1].strip()
    multiplier=Decimal(1)
    suffix=re.search(r'\s*(million|milh(?:ão|ões)|mil|k|m)$',s,re.I)
    if suffix:
        multiplier=Decimal(1000000 if suffix.group(1).casefold() in ('m','million','milhão','milhões') else 1000)
        s=s[:suffix.start()].strip()
    if not s or not re.fullmatch(r'\d[\d.,]*',s):return None
    if ',' in s and '.' in s:
        s=s.replace('.','').replace(',','.') if s.rfind(',')>s.rfind('.') else s.replace(',','')
    elif ',' in s:
        chunks=s.split(',')
        s=''.join(chunks) if len(chunks)>2 or len(chunks[-1])==3 else s.replace(',','.')
    elif '.' in s:
        chunks=s.split('.')
        s=''.join(chunks) if len(chunks)>2 or len(chunks[-1])==3 else s
    try:return Decimal(s)*multiplier
    except InvalidOperation:return None


def _figures(text):
    out=[]
    for m in FIGURE.finditer(text):
        raw=m.group().rstrip('.,');n=_number(raw)
        if n is None:continue
        kind='pct' if raw.strip().endswith('%') else 'money'
        out.append((kind,n,raw))
    return out


def _provable(target,values):
    """Check a small set of exact, bounded arithmetic operations (no LLM trust)."""
    vals=list(dict.fromkeys(values))[:18]
    if target in vals:return True
    for a,b in combinations(vals,2):
        if target in (a+b,a-b,b-a,a*b):return True
        if b and target==a/b:return True
        if a and target==b/a:return True
    # Allow 3-input sums/differences, e.g. revenue - expenses - debt.
    for group in combinations(vals,3):
        for signs in product((1,-1),repeat=3):
            if sum((v*sign for v,sign in zip(group,signs)),Decimal(0))==target:return True
    return False


def validate_financial_response(answer,scenario):
    """Return an auditable verdict. This is a conservative numeric filter, not proof of truth."""
    inputs=_figures(scenario);outputs=_figures(answer)
    money=[n for kind,n,_ in inputs if kind=='money']
    pcts=[n for kind,n,_ in inputs if kind=='pct']
    invalid=[];derived=[]
    for kind,value,raw in outputs:
        pool=money if kind=='money' else pcts
        if value in pool:continue
        valid=_provable(value,pool)
        if kind=='money' and not valid:
            # A monetary percentage of a supplied monetary figure is verifiable.
            valid=any(value==m*p/Decimal(100) for m in money for p in pcts)
        if kind=='pct' and not valid:
            # E.g. 20% margin from 20/100, if inputs contain both monetary amounts.
            valid=any(den and value==num*Decimal(100)/den for num in money for den in money)
        (derived if valid else invalid).append(raw)
    return {'accepted':not invalid,'reason':None if not invalid else 'unverified_financial_figures',
            'unverified_figures':invalid[:20],'verified_derived_figures':derived[:20],
            'checked_figure_count':len(outputs)}
