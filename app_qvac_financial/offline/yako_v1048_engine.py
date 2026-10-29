"""AI Yako V10.48 — English-canonical multilingual deterministic financial engine.
No network, no model inference. Uses V10.47 for bounded offline knowledge.
"""
import re
from decimal import Decimal, ROUND_HALF_UP
try:
 from . import yako_hybrid_v1047 as legacy
except ImportError:
 import importlib.util as _iu
 from pathlib import Path as _Path
 _spec=_iu.spec_from_file_location('yako_hybrid_v1047_legacy',_Path(__file__).with_name('yako_hybrid_v1047.py'))
 legacy=_iu.module_from_spec(_spec)
 _spec.loader.exec_module(legacy)
D=Decimal
M=r'((?:(?:R\$|US\$|\$|€|£)\s*)?[0-9][0-9.,\s]*)'
FIELDS={
 'income':[r'(?:monthly\s+)?(?:income|revenue|earnings|salary)',r'(?:receita|renda|sal[aá]rio)(?:\s+mensal)?',r'(?:ingresos?|sueldo)(?:\s+mensuales?)?',r'(?:revenu|salaire)(?:\s+mensuel)?'],
 'fixed':[r'fixed\s+(?:expenses?|costs?)',r'despesas?\s+fixas?',r'gastos?\s+fijos?',r'd[eé]penses?\s+fixes?'],
 'variable':[r'variable\s+(?:expenses?|costs?)',r'despesas?\s+vari[aá]veis?',r'gastos?\s+variables?',r'd[eé]penses?\s+variables?'],
 'debt':[r'(?:outstanding\s+)?debt',r'd[ií]vida',r'deuda',r'dette'],
 'rate':[r'(?:monthly\s+)?interest\s+rate',r'juros|taxa\s+de\s+juros',r'inter[eé]s|tasa\s+de\s+inter[eé]s',r'int[eé]r[eê]ts?|taux\s+d.int[eé]r[eê]t'],
 'payment':[r'(?:monthly\s+)?payments?|(?:paying|allocate|allocating|set\s+aside)',r'(?:destinando|pagando|parcela|pagamento)',r'(?:pagando|destinando|cuota|pago\s+mensual)',r'(?:versant|paiement|mensualit[eé])'],
}
LABELS={
'en':('Verified financial analysis','Monthly income','Fixed expenses','Variable expenses','Total expenses','Available monthly balance','Income committed to expenses','Debt repayment','months','Total repaid','Total interest','Payment does not cover initial monthly interest; debt cannot be repaid under these assumptions.','Emergency fund','Prioritize liquidity and low risk. Set a target based on essential expenses and income stability; no ideal amount can be verified without those details.','Interpretation','Positive balance before any unreported obligations; long-term sustainability is not established.','Negative monthly cash flow; review expenses and obligations.','Source: deterministic offline calculation; no QVAC inference was executed. Additional fees or assumptions can change results.'),
'pt':('Análise financeira verificada','Receita mensal','Despesas fixas','Despesas variáveis','Despesas totais','Saldo mensal disponível','Receita comprometida com despesas','Quitação da dívida','meses','Total pago','Juros totais','A parcela não cobre os juros mensais iniciais; a dívida não seria quitada nessas condições.','Reserva de emergência','Priorize liquidez e baixo risco. Defina a meta considerando despesas essenciais e estabilidade de renda; sem esses dados não há valor ideal comprovado.','Interpretação','Saldo positivo antes de obrigações não informadas; sustentabilidade de longo prazo não comprovada.','Fluxo mensal negativo; revise despesas e obrigações.','Origem: cálculo determinístico offline; nenhuma inferência QVAC foi executada. Encargos e premissas adicionais podem alterar resultados.'),
'es':('Análisis financiero verificado','Ingresos mensuales','Gastos fijos','Gastos variables','Gastos totales','Saldo mensual disponible','Ingresos comprometidos en gastos','Pago de la deuda','meses','Total pagado','Intereses totales','La cuota no cubre los intereses mensuales iniciales; la deuda no se amortizaría bajo estos supuestos.','Fondo de emergencia','Priorice liquidez y bajo riesgo. Defina la meta según gastos esenciales y estabilidad de ingresos; sin esos datos no se puede verificar una cantidad ideal.','Interpretación','Saldo positivo antes de otras obligaciones no declaradas; no demuestra sostenibilidad a largo plazo.','Flujo mensual negativo; revise gastos y obligaciones.','Fuente: cálculo determinista sin conexión; no se ejecutó inferencia QVAC. Otros cargos o supuestos pueden cambiar los resultados.'),
'fr':('Analyse financière vérifiée','Revenu mensuel','Dépenses fixes','Dépenses variables','Dépenses totales','Solde mensuel disponible','Part du revenu consacrée aux dépenses','Remboursement de la dette','mois','Total remboursé','Intérêts totaux','Le versement ne couvre pas les intérêts mensuels initiaux ; la dette ne peut pas être remboursée dans ces conditions.','Fonds d’urgence','Privilégiez liquidité et faible risque. Fixez un objectif selon les dépenses essentielles et la stabilité des revenus ; aucun montant idéal ne peut être confirmé sans ces données.','Interprétation','Solde positif avant toute autre obligation non déclarée ; la viabilité à long terme n’est pas établie.','Flux mensuel négatif ; réexaminez dépenses et obligations.','Source : calcul déterministe hors ligne ; aucune inférence QVAC exécutée. Des frais ou hypothèses supplémentaires peuvent modifier les résultats.')}
EMERGENCY=r'emergency\s+fund|emergency\s+savings|reserva\s+de\s+emerg[eê]ncia|fondo\s+de\s+emergencia|fonds?\s+d.urgence|[ée]pargne\s+de\s+pr[eé]caution'

def locale_of(text, locale):
 if locale in LABELS and locale!='en':return locale
 if re.search(r'\b(?:tenho|despesas|receita|quitar|reserva)\b',text,re.I):return 'pt'
 if re.search(r'\b(?:tengo|gastos|ingresos|deuda)\b',text,re.I):return 'es'
 if re.search(r'\b(?:revenu|d[eé]penses|dette|rembourser)\b',text,re.I):return 'fr'
 return locale if locale in LABELS else 'en'

def amount(raw):
 s=re.sub(r'[^0-9.,]','',raw)
 if not s:return None
 if ',' in s and '.' in s:decimal_sep=',' if s.rfind(',')>s.rfind('.') else '.'
 elif ',' in s:decimal_sep=',' if len(s.rsplit(',',1)[-1]) in (1,2) else None
 elif '.' in s:decimal_sep='.' if len(s.rsplit('.',1)[-1]) in (1,2) else None
 else:decimal_sep=None
 if decimal_sep:
  whole,frac=s.rsplit(decimal_sep,1)
  whole=re.sub(r'[.,]','',whole)
  s=whole+'.'+frac
 else:s=re.sub(r'[.,]','',s)
 try:return D(s)
 except Exception:return None

def extract(text,key):
 for word in FIELDS[key]:
  pattern=r'(?<!\w)(?:'+word+r')\b\s*(?:of|is|are|at|de|d[eu]|:|=|a|à|worth|amounting\s+to)?\s*'+M
  m=re.search(pattern,text,re.I)
  if m:
   value=amount(m.group(1))
   if value is not None:return value
 return None

def money(x,symbol,locale):
 val=f'{x.quantize(D("0.01"),rounding=ROUND_HALF_UP):,.2f}'
 if locale in ('pt','es','fr'):val=val.replace(',','X').replace('.',',').replace('X','.')
 return (symbol+' '+val) if symbol!='€' else (val+' €')

def solve(text,locale='en'):
 if not isinstance(text,str) or not 1<=len(text.strip())<=12000:return None
 lang=locale_of(text,locale)
 values={k:extract(text,k) for k in ('income','fixed','variable')}
 if any(v is None for v in values.values()):return None
 income,fixed,variable=(values[k] for k in ('income','fixed','variable'))
 if income<=0 or fixed<0 or variable<0:return None
 symbols=re.findall(r'R\$|US\$|\$|€|£',text)
 if len(set(symbols))>1:return None # do not silently mix currencies
 symbol=symbols[0] if symbols else {'pt':'R$','en':'$','es':'$','fr':'€'}[lang]
 fmt=lambda n:money(n,symbol,lang)
 L=LABELS[lang];expenses=fixed+variable;available=income-expenses
 ratio=(expenses/income*100).quantize(D('0.01'),rounding=ROUND_HALF_UP)
 lines=[f'### {L[0]}',f'{L[1]}: {fmt(income)}. {L[2]}: {fmt(fixed)}. {L[3]}: {fmt(variable)}.',f'{L[4]} = {fmt(fixed)} + {fmt(variable)} = **{fmt(expenses)}**.',f'{L[5]} = {fmt(income)} − {fmt(expenses)} = **{fmt(available)}**.',f'{L[6]} = ({fmt(expenses)} ÷ {fmt(income)}) × 100 = **{ratio}%**.']
 debt=extract(text,'debt');rate=extract(text,'rate');pay=extract(text,'payment')
 # Interest must explicitly be a monthly percentage, and payment must be monthly.
 monthly_rate=bool(re.search(r'(?:monthly\s+interest\s+rate\s+(?:of\s+)?[0-9.,]+\s*%)|(?:interest|juros|inter[eé]s|int[eé]r[eê]t).{0,45}(?:%\s*(?:per\s+month|a\s+month|monthly|ao\s+m[eê]s|al\s+mes|par\s+mois)|monthly\s+interest)|(?:taxa|tasa|taux).{0,35}%\s*(?:ao\s+m[eê]s|al\s+mes|par\s+mois)',text,re.I))
 monthly_payment=bool(re.search(r'monthly\s+payments?|payments?\s+(?:of\s+)?[^.\n]{0,30}(?:per\s+month|monthly)|(?:destinando|pagando|parcela|cuota|mensualit[eé]).{0,40}(?:mensais|mensal|por\s+m[eê]s|mensual|par\s+mois)|(?:payments?|allocate|allocating|paying)\s+(?:of\s+)?[^.\n]{0,35}(?:per\s+month|monthly)',text,re.I))
 if debt is not None and rate is not None and pay is not None and monthly_rate and monthly_payment and debt>0 and 0<=rate<=100 and pay>0:
  if pay<=debt*rate/100:lines.append(L[11])
  else:
   balance=debt;total=D(0)
   for month in range(1,1201):
    interest=balance*rate/100;paid=min(pay,balance+interest);total+=paid;balance+=interest-paid
    if balance<=D('0.00000001'):
     lines.append(f'{L[7]}: **{month} {L[8]}**. {L[9]}: **{fmt(total)}**. {L[10]}: **{fmt(total-debt)}**.');break
 if debt is not None and not (rate is not None and pay is not None and monthly_rate and monthly_payment):
  lines.append({'en':'Debt payoff not calculated: an explicit monthly interest rate and monthly payment are required.','pt':'Quitação não calculada: informe taxa de juros mensal e parcela mensal explícitas.','es':'Amortización no calculada: se requieren tasa de interés mensual y cuota mensual explícitas.','fr':'Remboursement non calculé : taux d’intérêt mensuel et mensualité explicites requis.'}[lang])
 lines.append(f'**{L[14]}:** {L[15] if available>=0 else L[16]}')
 if re.search(EMERGENCY,text,re.I):lines.append(f'**{L[12]}:** {L[13]}')
 lines.append(L[17])
 return {'answer':'\n\n'.join(lines),'engine':'AI Yako V10.48 — English-canonical deterministic offline','model_used':False,'inference_executed':False,'source':'deterministic_offline','locale':lang,'canonical_fields':{k:str(v) for k,v in values.items()},'knowledge_matches':[]}

def enrich(text,locale='en',max_chars=850):
 return legacy.enrich(text,locale,max_chars)
