"""Deterministic, bounded business-finance scenario analyzer (no model guesses)."""
import re
from decimal import Decimal

MONEY = r'(?:R\$|BRL|\$)\s*([\d.,]+)'
NUM = re.compile(MONEY, re.I)
LANGS = ('en','pt','es','fr')

def money_number(s):
    s=s.strip().rstrip('.,')
    if ',' in s and '.' in s:
        s=s.replace('.','').replace(',','.') if s.rfind(',')>s.rfind('.') else s.replace(',','')
    elif ',' in s:
        s=s.replace(',','.') if len(s.split(',')[-1])<=2 else s.replace(',','')
    elif '.' in s and len(s.split('.')[-1])==3:
        s=s.replace('.','')
    return Decimal(s)

def find_value(text, terms):
    # Bind a currency value to a local label; avoid borrowing an unrelated value.
    # Require label before currency and limit intervening text.
    pattern=r'(?:'+ '|'.join(terms)+r')\b[^\n,.!?;]{0,30}?'+MONEY
    m=re.search(pattern,text,re.I)
    if m:return money_number(m.group(1))
    # Also handle "R$ 500.000 em caixa" and "R$ 350.000 na operação".
    pattern=MONEY+r'\s*(?:em|de|no|na|for|in|of)?\s*(?:'+ '|'.join(terms)+r')\b'
    m=re.search(pattern,text,re.I)
    return money_number(m.group(1)) if m else None

def fmt(v,locale):
    v=f'{v:,.2f}'
    if locale in ('pt','es'):v=v.replace(',','@').replace('.',',').replace('@','.')
    return ('R$ ' if locale in ('pt','es') else 'BRL ')+v

LABELS={
'en':{'title':'BUSINESS FINANCIAL ANALYSIS','facts':'VERIFIED CALCULATIONS','cash':'Initial cash','investment':'Proposed investment','remaining':'Cash immediately after investment','revenue':'Current monthly revenue','expenses':'Current monthly expenses','operating':'Current simplified monthly operating result','success':'Probability of success','failure':'Probability of failure','potential':'Additional monthly revenue if successful (after the delay)','expected':'Probability-weighted additional monthly revenue (after the delay)','debt':'Outstanding debt','risk':'LIQUIDITY AND DECISION RISKS','risktxt':'The investment consumes {pct}% of available cash. Debt servicing and future operating cash flows cannot be established from the supplied information.','scenario':'SCENARIOS (ADDITIONAL MONTHLY REVENUE)','optimistic':'Success','average':'Probability-weighted expectation (not a guaranteed outcome)','pessimistic':'Failure','unknown':'UNKNOWNS AND LIMITATIONS','unknowntext':'Incremental operating costs, taxes, collection timing, debt interest and maturities are unknown. Additional revenue is not profit or cash flow. The expected value is not a third outcome.','recommend':'DECISION','recommendtext':'Do not approve the investment based on these figures alone. Request a cash-flow forecast, debt repayment schedule, incremental cost estimates and contingency plan.','delay':'Revenue begins after the stated three-month delay, not immediately.','prob':'The failure probability is an estimate, not an independently verified statistic.'},
'pt':{'title':'ANÁLISE FINANCEIRA EMPRESARIAL','facts':'CÁLCULOS VERIFICADOS','cash':'Caixa inicial','investment':'Investimento proposto','remaining':'Caixa imediatamente após o investimento','revenue':'Receita mensal atual','expenses':'Despesas mensais atuais','operating':'Resultado operacional mensal simplificado','success':'Probabilidade de sucesso','failure':'Probabilidade de fracasso','potential':'Receita adicional mensal em caso de sucesso (após o prazo)','expected':'Receita adicional mensal ponderada pela probabilidade (após o prazo)','debt':'Dívida existente','risk':'RISCOS DE LIQUIDEZ E DECISÃO','risktxt':'O investimento consome {pct}% do caixa disponível. Não é possível determinar o serviço da dívida nem os fluxos futuros de caixa com os dados fornecidos.','scenario':'CENÁRIOS (RECEITA MENSAL ADICIONAL)','optimistic':'Sucesso','average':'Valor esperado probabilístico (não é resultado garantido)','pessimistic':'Fracasso','unknown':'INFORMAÇÕES AUSENTES E LIMITAÇÕES','unknowntext':'Custos incrementais, tributos, prazos de recebimento, juros e vencimentos da dívida são desconhecidos. Receita adicional não é lucro nem fluxo de caixa. O valor esperado não é um terceiro resultado.','recommend':'DECISÃO','recommendtext':'Não aprove o investimento apenas com esses dados. Solicite projeção de fluxo de caixa, cronograma da dívida, estimativas de custos adicionais e plano de contingência.','delay':'A receita começa após os três meses informados, não imediatamente.','prob':'A probabilidade de fracasso é uma estimativa, não uma estatística verificada independentemente.'},
'es':{'title':'ANÁLISIS FINANCIERO EMPRESARIAL','facts':'CÁLCULOS VERIFICADOS','cash':'Efectivo inicial','investment':'Inversión propuesta','remaining':'Efectivo después de invertir','revenue':'Ingresos mensuales actuales','expenses':'Gastos mensuales actuales','operating':'Resultado operativo mensual simplificado','success':'Probabilidad de éxito','failure':'Probabilidad de fracaso','potential':'Ingresos mensuales adicionales si tiene éxito','expected':'Ingresos mensuales adicionales esperados (ponderados)','debt':'Deuda pendiente','risk':'RIESGOS DE LIQUIDEZ','risktxt':'La inversión consume el {pct}% del efectivo disponible. No conocemos el servicio de la deuda ni los flujos futuros.','scenario':'ESCENARIOS (INGRESOS MENSUALES ADICIONALES)','optimistic':'Éxito','average':'Valor esperado (no es un resultado garantizado)','pessimistic':'Fracaso','unknown':'DATOS FALTANTES','unknowntext':'Se desconocen costos adicionales, impuestos, cobros, intereses y vencimientos. Ingresos no equivalen a beneficios ni a flujo de caja.','recommend':'DECISIÓN','recommendtext':'No apruebe la inversión solo con estos datos. Solicite previsiones de caja, vencimientos de deuda y costos adicionales.','delay':'Los ingresos adicionales comenzarían después de tres meses.','prob':'La probabilidad de fracaso es una estimación no verificada.'},
'fr':{'title':'ANALYSE FINANCIÈRE D’ENTREPRISE','facts':'CALCULS VÉRIFIÉS','cash':'Trésorerie initiale','investment':'Investissement proposé','remaining':'Trésorerie après investissement','revenue':'Revenu mensuel actuel','expenses':'Dépenses mensuelles','operating':'Résultat opérationnel mensuel simplifié','success':'Probabilité de réussite','failure':'Probabilité d’échec','potential':'Revenu mensuel supplémentaire en cas de réussite','expected':'Revenu mensuel supplémentaire espéré (pondéré)','debt':'Dette existante','risk':'RISQUES DE LIQUIDITÉ','risktxt':'L’investissement absorbe {pct}% de la trésorerie disponible. Le service de la dette et les flux futurs sont inconnus.','scenario':'SCÉNARIOS (REVENUS MENSUELS SUPPLÉMENTAIRES)','optimistic':'Réussite','average':'Espérance probabiliste (non garantie)','pessimistic':'Échec','unknown':'INFORMATIONS MANQUANTES','unknowntext':'Coûts supplémentaires, impôts, encaissements, intérêts et échéances inconnus. Le chiffre d’affaires ne constitue ni un bénéfice ni un flux de trésorerie.','recommend':'DÉCISION','recommendtext':'Ne validez pas cet investissement sans prévisions de trésorerie, échéancier de dette et estimation des coûts.','delay':'Les revenus supplémentaires débuteraient après trois mois.','prob':'La probabilité d’échec est une estimation non vérifiée.'}}

def business_analysis(text, locale='en'):
    """Only handle sufficiently complete, explicitly labelled business scenarios."""
    if locale not in LANGS:locale='en'
    t=text
    cash=find_value(t,[r'caixa(?:\s+(?:atual|dispon[ií]vel))?',r'cash(?:\s+(?:on\s+hand|available))?',r'efectivo',r'tr[eé]sorerie'])
    investment=find_value(t,[r'investimento',r'investir',r'investment',r'invest',r'inversi[oó]n',r'investissement'])
    revenue=find_value(t,[r'faturamento(?:\s+mensal)?',r'receita\s+mensal',r'monthly\s+revenue',r'ingresos\s+mensuales',r'revenu\s+mensuel'])
    expenses=find_value(t,[r'despesas\s+mensais',r'custos\s+mensais',r'monthly\s+expenses',r'gastos\s+mensuales',r'd[eé]penses\s+mensuelles'])
    debt=find_value(t,[r'd[ií]vida(?:\s+total)?',r'debt',r'deuda',r'dette'])
    extra=find_value(t,[r'(?:receita|faturamento)\s+adicional',r'adicionais\s+de\s+receita',r'additional\s+(?:monthly\s+)?revenue',r'ingresos\s+adicionales',r'revenu\s+suppl[eé]mentaire'])
    # 'R$ 80.000 adicionais de receita mensal'
    if extra is None:
        m=re.search(MONEY+r'\s+adicionais\s+de\s+receita',t,re.I)
        if m:extra=money_number(m.group(1))
    failure=re.search(r'(\d{1,2}(?:[.,]\d+)?)\s*%\s*(?:de\s+)?(?:a\s+opera[cç][aã]o\s+)?(?:fracass|falh|failure|fail|fracaso|[eé]chec)',t,re.I)
    if not failure:
        failure=re.search(r'(?:probabilidade\s+(?:estimada\s+)?de|probability\s+of)\s*(\d{1,2}(?:[.,]\d+)?)\s*%[^.!?]{0,55}(?:fracass|falh|failure|fail|fracaso|[eé]chec)',t,re.I)
    # English '40% probability of failure' etc
    if not failure:
        failure=re.search(r'(\d{1,2}(?:[.,]\d+)?)\s*%\s*(?:probability\s+of\s+failure|chance\s+of\s+failure)',t,re.I)
    if any(v is None for v in (cash,investment,revenue,expenses,extra)) or not failure:return None
    pf=Decimal(failure.group(1).replace(',','.'))
    if not 0<=pf<=100:return None
    ps=100-pf
    rem=cash-investment
    operating=revenue-expenses
    expected=extra*ps/100
    l=LABELS[locale]
    pct=(investment/cash*100) if cash>0 else Decimal(0)
    rows=[('cash',cash),('investment',investment),('remaining',rem),('revenue',revenue),('expenses',expenses),('operating',operating)]
    if debt is not None:rows.append(('debt',debt))
    body='**'+l['title']+'**\n\n**'+l['facts']+'**\n'
    body+='\n'.join('• '+l[k]+': '+fmt(v,locale) for k,v in rows)
    body+='\n• '+l['success']+': '+str(ps).replace('.',',')+'%\n• '+l['failure']+': '+str(pf).replace('.',',')+'%'
    body+='\n• '+l['potential']+': '+fmt(extra,locale)+'\n• '+l['expected']+': '+fmt(expected,locale)
    body+='\n\n**'+l['scenario']+'**\n• '+l['optimistic']+': '+fmt(extra,locale)+'\n• '+l['average']+': '+fmt(expected,locale)+'\n• '+l['pessimistic']+': '+fmt(Decimal(0),locale)
    body+='\n\n**'+l['risk']+'**\n• '+l['risktxt'].format(pct=f'{pct:.1f}')+'\n• '+l['prob']
    body+='\n\n**'+l['unknown']+'**\n'+l['unknowntext']+'\n\n**'+l['recommend']+'**\n'+l['recommendtext']
    return {'answer':body,'engine':'Python Decimal · verified business scenario','total_seconds':0,'model_used':False,'calculation':{'cash_after_investment':str(rem),'operating_result':str(operating),'expected_additional_revenue':str(expected),'probability_success_percent':str(ps)}}

