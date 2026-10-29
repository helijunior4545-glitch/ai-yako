"""AI Yako deterministic financial toolkit. Offline, stdlib-only. No model claims."""
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import json, re, argparse, time
D=Decimal
def money(x): return str(D(str(x)).quantize(D('0.01'), rounding=ROUND_HALF_UP))
def parse_money(s):
    s=str(s).strip().replace('R$','').replace(' ','')
    if ',' in s: s=s.replace('.','').replace(',','.')
    return D(s)
def analyze_budget(revenue, fixed, variable):
    r,f,v=map(parse_money,(revenue,fixed,variable))
    if r<=0 or f<0 or v<0: raise ValueError('Receita deve ser positiva e despesas não negativas.')
    expenses=f+v
    return {'kind':'budget','revenue':money(r),'expenses':money(expenses),'available':money(r-expenses),'expense_ratio_percent':money(expenses/r*100),'currency':'BRL','source':'deterministic_offline'}
def debt_schedule(principal, monthly_rate_percent, payment, max_months=1200):
    p,r,a=map(parse_money,(principal,monthly_rate_percent,payment))
    if p<=0 or r<0 or a<=0:raise ValueError('Dívida e parcela devem ser positivas; taxa não negativa.')
    rate=r/100
    if a<=p*rate: raise ValueError('Parcela não cobre os juros do primeiro mês; dívida não amortiza.')
    original=p; total=D('0'); rows=[]
    for n in range(1,max_months+1):
        interest=p*rate
        paid=min(a,p+interest)
        p=(p+interest-paid).quantize(D('0.00000001'))
        total+=paid
        if n<=12:rows.append({'month':n,'interest':money(interest),'payment':money(paid),'balance':money(max(p,0))})
        if p<=D('0.00000001'):
            return {'kind':'debt','months':n,'total_paid':money(total),'total_interest':money(total-original),'first_12_months':rows,'source':'deterministic_offline'}
    raise ValueError('Prazo acima do limite de segurança de 1200 meses.')
def compound_interest(principal, rate_percent, months):
    p,r=map(parse_money,(principal,rate_percent));n=int(months)
    if p<0 or r<=-100 or not 0<=n<=1200:raise ValueError('Parâmetros fora dos limites.')
    amount=p*(1+r/100)**n
    return {'kind':'compound','future_value':money(amount),'gain':money(amount-p),'months':n,'source':'deterministic_offline'}
# Curated offline knowledge: not live financial or regulatory guidance.
KNOWLEDGE={
 'reserva de emergência':('Reserva de emergência','Liquidez, baixo risco e acesso rápido são prioridades. Uma referência educacional comum é cobrir alguns meses de despesas essenciais; o valor adequado depende da estabilidade da renda e das necessidades.'),
 'juros compostos':('Juros compostos','Capitalização periódica: VF = VP × (1+i)^n. Taxa e períodos precisam estar na mesma unidade.'),
 'liquidez':('Liquidez','Capacidade de converter um ativo em dinheiro sem perda relevante de valor e dentro do prazo necessário.'),
 'risco de mercado':('Risco de mercado','Possibilidade de perdas causadas por movimentos de preços, taxas de juros, câmbio e outros fatores de mercado.'),
 'inflação':('Inflação','Variação geral dos preços ao longo do tempo; retorno nominal não equivale a retorno real.'),
 'fluxo de caixa':('Fluxo de caixa','Entradas e saídas de recursos em períodos definidos. Lucro contábil e disponibilidade de caixa são conceitos distintos.'),
 'diversificação':('Diversificação','Distribuir exposição entre ativos e fatores de risco pode reduzir concentração, mas não elimina risco de perda.'),
 'custo efetivo total':('Custo efetivo total','Ao comparar empréstimos, considere juros, tarifas, tributos e demais encargos aplicáveis.'),
 'orçamento':('Orçamento','Organização de receitas, despesas e metas em um período para acompanhar sustentabilidade financeira.'),
 'valor presente':('Valor presente','Valor atual de fluxos futuros descontados por uma taxa compatível com o risco e a periodicidade.'),
 'taxa real':('Taxa real','Relação entre taxa nominal e inflação: (1+nominal)/(1+inflação)-1.'),
 'amortização':('Amortização','Redução do saldo principal de uma dívida; o método de amortização influencia juros e parcelas.'),
}
def lookup(query):
    q=query.casefold(); matches=[{'topic':k,'title':v[0],'text':v[1]} for k,v in KNOWLEDGE.items() if k in q]
    return {'kind':'knowledge','matches':matches,'source':'curated_offline','warning':'Conteúdo educacional; não representa cotação ou norma atualizada.'}
def analyze_text(query):
    """Conservative fast-path: explicit keyword-value fields only; never invent missing data."""
    def extract(names):
        for name in names:
            m=re.search(r'(?<!\w)'+name+r'\s*[:=]\s*(?:R\$\s*)?([\d.,]+)',query,re.I)
            if m:return m.group(1)
        return None
    r=extract(['receita']); f=extract(['fixas','despesas fixas']);v=extract(['variáveis','variaveis','despesas variáveis','despesas variaveis'])
    if r and f and v:return analyze_budget(r,f,v)
    return lookup(query)
def main():
    p=argparse.ArgumentParser();p.add_argument('--test',action='store_true');p.add_argument('--query');a=p.parse_args()
    if a.test:
        assert analyze_budget('12500','5200','2300')['available']=='5000.00'
        assert analyze_budget('12500','5200','2300')['expense_ratio_percent']=='60.00'
        assert debt_schedule('9000','2','2000')['months']==5
        assert compound_interest('10000','1','12')['future_value']=='11268.25'
        try: debt_schedule('9000','2','180')
        except ValueError:pass
        else:raise AssertionError('Negative amortization not rejected')
        print('PASS: 5 deterministic checks, no network required');return
    print(json.dumps(analyze_text(a.query or 'reserva de emergência'),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
