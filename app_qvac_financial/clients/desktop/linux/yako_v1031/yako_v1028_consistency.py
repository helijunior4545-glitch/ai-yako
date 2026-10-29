"""Conservative financial semantic guardrails: repair only clearly contradictory claims.
No assumptions about the company's starting cash balance or collected revenue.
"""
import re

MESSAGES={
 'en':{'reserve':'A monthly surplus is a flow, not the company\'s existing cash reserves. The opening cash balance is unknown.',
       'cost':'Holding revenue and other payments constant, lower operating expenses increase the monthly surplus, not decrease it.',
       'cash':'This is an estimated monthly surplus based on the stated figures, not verified cash collected or cash on hand.'},
 'pt':{'reserve':'Excedente mensal é um fluxo, não o saldo de reservas. O caixa inicial é desconhecido.',
       'cost':'Mantidas as demais variáveis, menores despesas operacionais aumentam o excedente mensal.',
       'cash':'O excedente mensal é estimado com base nos valores informados, não confirma recebimentos ou saldo de caixa.'},
 'es':{'reserve':'El excedente mensual es un flujo, no el saldo de reservas existente.',
       'cost':'Si todo lo demás permanece constante, reducir gastos aumenta el excedente mensual.',
       'cash':'El excedente mensual es estimado; no confirma cobros ni efectivo disponible.'},
 'fr':{'reserve':'Un excédent mensuel est un flux, pas la réserve de trésorerie existante.',
       'cost':'Toutes choses égales par ailleurs, une baisse des charges augmente l’excédent.',
       'cash':'L’excédent mensuel est estimé et ne confirme pas les encaissements réels.'},
}
RESERVE=re.compile(r'(?i)(?:it means|this means|therefore|isso significa|esto significa|cela signifie).{0,85}(?:has|possui|tiene|dispose).{0,40}(?:cash reserves?|reservas? (?:de caixa|em dinheiro)|reservas? de efectivo|réserves? de trésorerie)')
COST=re.compile(r'(?i)(?:decrease|reduction|redu(?:ção|zir)|disminuci[oó]n|baisse|r[eé]duction).{0,65}(?:operat(?:ing|ional) costs?|despesas? operacionais|gastos? operativos|charges? d.exploitation).{0,90}(?:surplus|excedente|excédent).{0,35}(?:decrease|decline|reduce|diminuir|cair|disminuir|baisser)|(?:surplus|excedente|excédent).{0,45}(?:decrease|decline|reduce|diminuir|cair|disminuir|baisser).{0,85}(?:operat(?:ing|ional) costs?|despesas? operacionais|gastos? operativos|charges? d.exploitation)')

def review_financial_consistency(answer,scenario,locale='en'):
    """Return original text plus explicit corrections; never silently erase the model's text."""
    if not isinstance(answer,str):answer=str(answer or '')
    locale=locale if locale in MESSAGES else 'en'
    flags=[]
    if RESERVE.search(answer):flags.append('surplus_confused_with_reserves')
    if COST.search(answer):flags.append('expense_direction_inverted')
    # The note applies only to surplus questions; no invented figures or advice.
    if re.search(r'(?i)\b(?:surplus|excedente|excédent|superávit)\b',scenario) and re.search(r'(?i)\b(?:surplus|excedente|excédent|superávit)\b',answer):
        flags.append('cash_flow_assumptions_not_verified')
    corrections=[MESSAGES[locale]['reserve'] for f in flags if f=='surplus_confused_with_reserves']
    if 'expense_direction_inverted' in flags:corrections.append(MESSAGES[locale]['cost'])
    if 'cash_flow_assumptions_not_verified' in flags:corrections.append(MESSAGES[locale]['cash'])
    if corrections:
        heading={'en':'Financial consistency notes','pt':'Notas de consistência financeira','es':'Notas de consistencia financiera','fr':'Notes de cohérence financière'}[locale]
        answer=answer.rstrip()+f'\n\n{heading}:\n'+'\n'.join('- '+v for v in corrections)
    return {'answer':answer,'flags':flags,'repaired':bool(corrections)}
