"""AI Yako V10.20: independently verifiable, partial financial analysis."""
import re
from decimal import Decimal
from yako_v1019_finance import money_number, fmt, business_analysis, LANGS

MONEY_RE=re.compile(r'(?:R\$|BRL|\$)\s*([\d.,]+)',re.I)
TERMS={
 'cash':r'cash(?:\s+on\s+hand)?|caixa|efectivo|tr[eé]sorerie',
 'investment':r'invest(?:ment|ir|imento)?|inversi[oó]n|investissement',
 'revenue':r'(?:monthly\s+revenue|receita\s+mensal|faturamento\s+mensal|ingresos\s+mensuales|revenu\s+mensuel)',
 'expenses':r'(?:monthly\s+expenses|despesas\s+mensais|custos\s+mensais|gastos\s+mensuales|d[eé]penses\s+mensuelles)',
 'debt':r'(?:outstanding\s+debt|debt|d[ií]vida|deuda|dette)',
 'extra':r'(?:additional|extra|adicional|adicionais|suppl[eé]mentaire|adicionales)',
}
LABELS={
 'en':{'title':'VERIFIED FINANCIAL ANALYSIS','cash':'Initial cash','investment':'Investment','remaining':'Cash remaining after investment','share':'Cash committed','revenue':'Monthly revenue','expenses':'Monthly expenses','operating':'Simplified monthly operating surplus','debt':'Outstanding debt','failure':'Failure probability','success':'Success probability','extra':'Additional monthly revenue if successful','expected':'Probability-weighted additional monthly revenue','scenario':'SCENARIOS — ADDITIONAL MONTHLY REVENUE','success_case':'Success','average':'Expected value (not a third outcome)','failure_case':'Failure','limitations':'LIMITATIONS','notes':'Additional revenue is not profit. Incremental costs, taxes, collection timing, debt interest and maturities are unknown unless stated. Do not infer future cash balances from revenue alone.','decision':'DECISION','recommend':'Assess debt servicing, incremental costs and liquidity before committing capital. No unconditional investment approval is justified by these figures alone.','partial':'Only supplied values and mathematically derived results are shown.'},
 'pt':{'title':'ANÁLISE FINANCEIRA VERIFICADA','cash':'Caixa inicial','investment':'Investimento','remaining':'Caixa restante após investimento','share':'Caixa comprometido','revenue':'Receita mensal','expenses':'Despesas mensais','operating':'Resultado operacional mensal simplificado','debt':'Dívida existente','failure':'Probabilidade de fracasso','success':'Probabilidade de sucesso','extra':'Receita mensal adicional em caso de sucesso','expected':'Receita mensal adicional esperada ponderada','scenario':'CENÁRIOS — RECEITA MENSAL ADICIONAL','success_case':'Sucesso','average':'Valor esperado (não é terceiro resultado)','failure_case':'Fracasso','limitations':'LIMITAÇÕES','notes':'Receita adicional não é lucro. Custos incrementais, tributos, recebimentos, juros e vencimentos da dívida são desconhecidos salvo informação explícita. Não se pode inferir caixa futuro apenas da receita.','decision':'DECISÃO','recommend':'Avalie serviço da dívida, custos adicionais e liquidez antes de investir. Esses dados não justificam aprovação incondicional.','partial':'Somente valores informados e cálculos matematicamente derivados.'},
 'es':{'title':'ANÁLISIS FINANCIERO VERIFICADO','cash':'Efectivo inicial','investment':'Inversión','remaining':'Efectivo restante','share':'Efectivo comprometido','revenue':'Ingresos mensuales','expenses':'Gastos mensuales','operating':'Resultado operativo simplificado','debt':'Deuda','failure':'Probabilidad de fracaso','success':'Probabilidad de éxito','extra':'Ingresos mensuales adicionales si tiene éxito','expected':'Ingresos mensuales adicionales esperados','scenario':'ESCENARIOS — INGRESOS ADICIONALES','success_case':'Éxito','average':'Valor esperado (no es otro resultado)','failure_case':'Fracaso','limitations':'LIMITACIONES','notes':'Los ingresos no son beneficios. Se desconocen costes adicionales, impuestos, cobros e intereses de la deuda.','decision':'DECISIÓN','recommend':'Revise deuda, costes y liquidez antes de invertir.','partial':'Solo cifras dadas y resultados matemáticos.'},
 'fr':{'title':'ANALYSE FINANCIÈRE VÉRIFIÉE','cash':'Trésorerie initiale','investment':'Investissement','remaining':'Trésorerie restante','share':'Trésorerie engagée','revenue':'Revenu mensuel','expenses':'Dépenses mensuelles','operating':'Résultat opérationnel simplifié','debt':'Dette','failure':'Probabilité d’échec','success':'Probabilité de réussite','extra':'Revenu mensuel supplémentaire en cas de réussite','expected':'Revenu mensuel supplémentaire espéré','scenario':'SCÉNARIOS — REVENUS SUPPLÉMENTAIRES','success_case':'Réussite','average':'Espérance (pas un autre résultat)','failure_case':'Échec','limitations':'LIMITES','notes':'Le chiffre d’affaires n’est pas un bénéfice. Coûts, impôts, encaissements et échéances de dette restent inconnus.','decision':'DÉCISION','recommend':'Évaluez la dette, les coûts et la liquidité avant d’investir.','partial':'Seuls les chiffres fournis et les calculs vérifiés sont affichés.'}}

def _extract(text):
    matches=list(MONEY_RE.finditer(text)); result={}; used=set()
    for key in ('extra','cash','investment','expenses','revenue','debt'):
        pat=TERMS[key]
        candidates=[]
        for i,m in enumerate(matches):
            if i in used:continue
            before=text[max(0,m.start()-80):m.start()]
            after=text[m.end():min(len(text),m.end()+70)]
            # Nearby keywords must be in the same clause, not another financial field.
            before=re.split(r'[.;!?\n]',before)[-1]
            after=re.split(r'[.;!?\n]',after)[0]
            found=[]
            for x in re.finditer(pat,before,re.I):found.append((m.start()-(m.start()-len(before)+x.end()),'before'))
            for x in re.finditer(pat,after,re.I):found.append((x.start(),'after'))
            if not found:continue
            dist,direction=min(found,key=lambda x:x[0])
            if dist>55:continue
            window=(before[-60:]+' '+after[:55]).lower()
            if key=='revenue' and re.search(TERMS['extra'],window,re.I):continue
            if key=='cash' and re.search(r'after\s+(?:the\s+)?invest|ap[oó]s\s+(?:o\s+)?invest',window,re.I):continue
            if key=='investment' and re.search(r'additional\s+monthly\s+revenue|receita\s+adicional',window,re.I):continue
            score=dist+(0 if direction=='before' else 3)
            candidates.append((score,i,m))
        if candidates:
            _,i,m=min(candidates,key=lambda x:x[0]);result[key]=money_number(m.group(1));used.add(i)
    return result

def _probability(text):
    patterns=[r'(?:probability|chance|probabilidade|probabilidad|probabilit[eé])\s+(?:of|de|d[’\']|estimada\s+de)\s*(?:failure|fail(?:ure)?|fracass[oa]?|falha|fracaso|[eé]chec)\s*(?:is|of|de|:|=|est|[eé])?\s*(\d+(?:[.,]\d+)?)\s*%',
      r'(\d+(?:[.,]\d+)?)\s*%\s*(?:chance|probability|probabilidade|probabilidad|probabilit[eé])\s+(?:of|de|d[’\'])\s*(?:failure|fail|fracass|falha|fracaso|[eé]chec)',
      r'(\d+(?:[.,]\d+)?)\s*%\s*(?:de\s+)?(?:fracasso|fracasar|failure|fail|fracaso|[eé]chec)',
      r'(?:failure|fracasso|fracaso|[eé]chec)\s*(?:probability|rate|probabilidade|:|=|of|de|est|is)?\s*(\d+(?:[.,]\d+)?)\s*%']
    for p in patterns:
        m=re.search(p,text,re.I)
        if m:
            v=Decimal(m.group(1).replace(',','.'))
            return v if 0<=v<=100 else None
    return None

def smart_analysis(text,locale='en'):
    if locale not in LANGS:locale='en'
    facts=_extract(text)
    pf=_probability(text)
    # Keep legacy coverage for its exact supported patterns.
    if not facts:
        return business_analysis(text,locale)
    l=LABELS[locale];rows=[]; derived={}; pct=None
    for key in ('cash','investment','revenue','expenses','debt','extra'):
        if key in facts:rows.append((l[key],fmt(facts[key],locale)))
    if 'cash' in facts and 'investment' in facts:
        rem=facts['cash']-facts['investment'];derived['cash_after_investment']=str(rem)
        rows.append((l['remaining'],fmt(rem,locale)))
        if facts['cash']>0:
            pct=facts['investment']/facts['cash']*100
            derived['investment_cash_percent']=str(pct)
            rows.append((l['share'],f'{pct:.2f}%'))
    if 'revenue' in facts and 'expenses' in facts:
        op=facts['revenue']-facts['expenses'];derived['operating_result']=str(op)
        rows.append((l['operating'],fmt(op,locale)))
    if pf is not None:
        ps=Decimal(100)-pf
        rows.extend(((l['failure'],f'{pf}%'),(l['success'],f'{ps}%')))
        derived['probability_success_percent']=str(ps)
        if 'extra' in facts:
            expected=facts['extra']*ps/100
            derived['expected_additional_revenue']=str(expected)
            rows.append((l['expected'],fmt(expected,locale)))
    if not rows:return None
    sections=['**'+l['title']+'**','**'+l['partial']+'**','\n'.join('• '+k+': '+v for k,v in rows)]
    if pf is not None and 'extra' in facts:
        sections.extend(('**'+l['scenario']+'**','• '+l['success_case']+': '+fmt(facts['extra'],locale)+'\n• '+l['average']+': '+fmt(expected,locale)+'\n• '+l['failure_case']+': '+fmt(Decimal(0),locale)))
    if 'investment' in facts or 'debt' in facts or 'extra' in facts:
        sections.extend(('**'+l['limitations']+'**',l['notes'],'**'+l['decision']+'**',l['recommend']))
    return {'answer':'\n\n'.join(sections),'engine':'Yako V10.20 · Python Decimal · verified facts','model_used':False,'total_seconds':0,'calculation':derived,'facts':{k:str(v) for k,v in facts.items()}}
