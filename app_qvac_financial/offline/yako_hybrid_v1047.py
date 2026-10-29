"""AI Yako V10.47 — offline indexed knowledge + safe deterministic fast path.
Only stdlib; never claims model inference. No network calls.
"""
import sqlite3, pathlib, re, json, random, argparse, time
from decimal import Decimal, ROUND_HALF_UP
D=Decimal
DB=pathlib.Path(__file__).with_name("knowledge_v1047.sqlite3")
SEED=[
("reserva de emergência","liquidez e proteção","A reserva de emergência deve priorizar liquidez, segurança e disponibilidade. Dimensione conforme despesas essenciais e estabilidade de renda."),
("liquidez","risco e mercado","Liquidez é a facilidade de transformar um ativo em caixa com rapidez e sem perda relevante."),
("risco de mercado","risco e mercado","Risco de mercado é a exposição a variações de preços, taxas de juros, câmbio e outros fatores."),
("risco de crédito","risco e mercado","Risco de crédito é a possibilidade de a contraparte não cumprir obrigações."),
("risco de liquidez","risco e mercado","Risco de liquidez envolve dificuldade de vender ativos ou honrar obrigações no prazo."),
("juros compostos","matemática financeira","Juros compostos capitalizam juros sobre o saldo acumulado: VF = VP × (1 + i)^n."),
("juros simples","matemática financeira","Juros simples: J = capital × taxa × períodos, com unidades consistentes."),
("taxa efetiva","matemática financeira","Taxas efetivas consideram a capitalização em determinado período; não compare períodos diferentes diretamente."),
("taxa nominal","matemática financeira","Taxa nominal precisa ser interpretada com sua frequência de capitalização."),
("inflação","macroeconomia","Inflação é o aumento generalizado de preços ao longo do tempo; reduz poder de compra."),
("retorno real","matemática financeira","Retorno real = (1 + retorno nominal) / (1 + inflação) - 1, com taxas em decimal."),
("valor presente","matemática financeira","Valor presente desconta fluxos futuros por taxa apropriada ao prazo e ao risco."),
("valor futuro","matemática financeira","Valor futuro acumula o valor atual segundo uma taxa e períodos definidos."),
("amortização","crédito","Amortização reduz o principal de uma dívida; juros incidem segundo o contrato e saldo."),
("tabela price","crédito","Na Tabela Price, parcelas podem ser constantes em condições padronizadas; a composição de juros e amortização varia."),
("sac","crédito","No SAC, amortização do principal é constante e prestações tendem a cair, mantidas as demais condições."),
("custo efetivo total","crédito","CET reúne juros e encargos pertinentes para comparar custos de crédito."),
("inadimplência","crédito","Inadimplência é o descumprimento de obrigação de pagamento no vencimento."),
("orçamento","finanças pessoais","Orçamento organiza receitas, despesas, metas e restrições por período."),
("despesas fixas","finanças pessoais","Despesas fixas tendem a repetir-se periodicamente; podem variar em situações específicas."),
("despesas variáveis","finanças pessoais","Despesas variáveis oscilam conforme consumo e circunstâncias."),
("fluxo de caixa","empresas","Fluxo de caixa registra entradas e saídas de dinheiro; não equivale necessariamente ao lucro contábil."),
("capital de giro","empresas","Capital de giro sustenta operações de curto prazo e depende dos ciclos de recebimento e pagamento."),
("margem líquida","empresas","Margem líquida = lucro líquido / receita líquida, se os conceitos e períodos forem comparáveis."),
("margem bruta","empresas","Margem bruta = lucro bruto / receita líquida, segundo o regime contábil aplicável."),
("ponto de equilíbrio","empresas","Ponto de equilíbrio depende de custos fixos, preço unitário e margem de contribuição."),
("diversificação","investimentos","Diversificação reduz concentração de exposições, mas não elimina risco."),
("volatilidade","investimentos","Volatilidade mede dispersão de retornos; não descreve sozinha todas as perdas possíveis."),
("rentabilidade","investimentos","Rentabilidade compara ganhos ou perdas ao capital de referência e ao horizonte temporal."),
("prazo","planejamento","Horizonte temporal influencia liquidez necessária e exposição ao risco."),
("imposto de renda","tributação","Tributação depende da jurisdição, produto e regras vigentes; dados offline podem estar desatualizados."),
("câmbio","macroeconomia","Taxas de câmbio variam e envolvem custos de conversão; sem cotação atual não é possível afirmar valor vigente."),
("selic","macroeconomia","A Selic é uma taxa básica de juros brasileira; seu valor vigente requer fonte atualizada."),
("ipca","macroeconomia","O IPCA é um índice de preços ao consumidor no Brasil; valores atuais exigem fonte atualizada."),
("vpl","empresas","VPL desconta fluxos de caixa futuros e subtrai o investimento inicial."),
("tir","empresas","TIR é a taxa que zera o valor presente líquido de um fluxo; pode ser ambígua em fluxos não convencionais."),
("alavancagem","risco e mercado","Alavancagem amplia exposição a ganhos e perdas e pode aumentar risco de insolvência."),
("endividamento","finanças pessoais","Endividamento deve ser avaliado junto com fluxo de caixa, custo, prazo e reserva de segurança."),
("patrimônio líquido","empresas","Patrimônio líquido contábil é a diferença entre ativos e passivos conforme regras aplicáveis."),
("liquidez corrente","empresas","Liquidez corrente = ativo circulante / passivo circulante, quando denominador é positivo."),
("índice de cobertura","empresas","Índices de cobertura relacionam recursos disponíveis às obrigações; a definição varia conforme o índice."),
]
def init_db():
 if DB.exists():return
 DB.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect(DB,timeout=5) as c:
  c.execute("CREATE TABLE IF NOT EXISTS topics(id INTEGER PRIMARY KEY,term TEXT UNIQUE,category TEXT,content TEXT)")
  c.executemany("INSERT OR IGNORE INTO topics(term,category,content) VALUES(?,?,?)",SEED)
  try:
   c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS topics_fts USING fts5(term,category,content,content='topics',content_rowid='id')")
   c.execute("INSERT INTO topics_fts(topics_fts) VALUES('rebuild')")
  except sqlite3.OperationalError: pass
  c.commit()
def lookup(text,limit=5):
 q=str(text or "").casefold()
 if DB.exists():
  try:
   with sqlite3.connect("file:"+str(DB)+"?mode=ro",uri=True,timeout=3) as c:
    rows=c.execute("SELECT term,category,content FROM topics").fetchall()
  except sqlite3.Error:rows=SEED
 else:rows=SEED
 ranked=[]
 for term,cat,content in rows:
  t=term.casefold()
  if t in q: ranked.append((len(t),term,cat,content))
 ranked.sort(reverse=True)
 return [{"topic":t,"category":cat,"text":content} for _,t,cat,content in ranked[:limit]]
def number(x):
 s=str(x).strip().replace("R$","").replace(" ","")
 if "," in s:s=s.replace(".","").replace(",",".")
 elif re.fullmatch(r"\d{1,3}(?:\.\d{3})+",s):s=s.replace(".","")
 return D(s)
def br(x):
 return "R$ "+f"{x.quantize(D('0.01'),rounding=ROUND_HALF_UP):,.2f}".replace(",","X").replace(".",",").replace("X",".")
def extract(text,patterns):
 for pattern in patterns:
  m=re.search(pattern,text,re.I)
  if m:
   try:return number(m.group(1))
   except Exception:return None
 return None
M=r"(?:R\$\s*)?([\d][\d.,]*)"
def solve(text,locale="pt"):
 """Strictly conservative: explicit Portuguese labels, no guessing about missing parameters."""
 if locale!="pt" or not isinstance(text,str) or len(text)>12000:return None
 revenue=extract(text,[r"(?:receita|renda)\s*(?:mensal)?\s*(?:de|:|=)\s*"+M])
 fixed=extract(text,[r"despesas?\s+fixas?\s*(?:de|:|=)\s*"+M])
 variable=extract(text,[r"despesas?\s+vari[aá]veis?\s*(?:de|:|=)\s*"+M])
 if any(v is None for v in (revenue,fixed,variable)):return None
 if revenue<=0 or fixed<0 or variable<0:return None
 expenses=fixed+variable
 available=revenue-expenses
 ratio=expenses/revenue*100
 lines=[
 "### Análise financeira — cálculo local verificado",
 f"Receita: {br(revenue)}. Despesas fixas: {br(fixed)}. Despesas variáveis: {br(variable)}.",
 f"Despesas totais = {br(fixed)} + {br(variable)} = **{br(expenses)}**.",
 f"Saldo mensal = {br(revenue)} − {br(expenses)} = **{br(available)}**.",
 f"Comprometimento da receita = ({br(expenses)} ÷ {br(revenue)}) × 100 = **{ratio.quantize(D('0.01'),rounding=ROUND_HALF_UP)}%**.",
 ]
 debt=extract(text,[r"d[ií]vida\s*(?:de|:|=)\s*"+M])
 rate=extract(text,[r"juros\s+de\s*"+M+r"\s*%\s*ao\s*m[eê]s",r"taxa\s*(?:de|:|=)\s*"+M+r"\s*%\s*(?:ao\s*m[eê]s|a\.m\.)"])
 pay=extract(text,[r"(?:destinando|pagando|parcela\s+de|pagamento\s+de)\s*"+M+r"\s*(?:mensais|mensal|por\s+m[eê]s)?"])
 if debt is not None and rate is not None and pay is not None:
  if debt>0 and rate>=0 and pay>0 and rate<=100:
   balance=debt;total=D(0)
   if pay<=balance*rate/100:
    lines.append("A parcela informada não cobre os juros iniciais; a dívida não seria quitada nessas condições.")
   else:
    for month in range(1,1201):
     interest=balance*rate/100
     paid=min(pay,balance+interest)
     total+=paid
     balance=balance+interest-paid
     if balance<=D("0.00000001"):
      lines.append(f"Quitação da dívida: **{month} meses**, com juros de {rate}% ao mês sobre saldo devedor e pagamentos no fim de cada mês. Total estimado: {br(total)}; juros totais: {br(total-debt)}. Última parcela ajustada ao saldo.")
      break
    else:lines.append("Prazo acima de 1.200 meses; cálculo interrompido por segurança.")
 if available<0:lines.append("**Interpretação:** fluxo mensal negativo. Rever despesas e obrigações é prioritário.")
 else:lines.append("**Interpretação:** o saldo é positivo antes de outras obrigações não informadas. Isso não comprova sustentabilidade de longo prazo.")
 if re.search(r"reserva|emerg[eê]ncia",text,re.I):
  lines.append("**Reserva de emergência:** priorize liquidez e baixo risco; defina a meta considerando despesas essenciais e estabilidade de renda. Sem esses dados não há valor ideal comprovado.")
 lines.append("**Origem:** cálculo determinístico offline. Nenhuma inferência QVAC foi necessária ou executada nesta resposta. Premissas e encargos adicionais podem alterar os resultados.")
 return {"answer":"\n\n".join(lines),"engine":"AI Yako V10.47 — deterministic offline","model_used":False,"inference_executed":False,"source":"deterministic_offline","knowledge_matches":lookup(text,3)}
def enrich(text,locale="pt",max_chars=850):
 """Only selected offline knowledge; bounded to protect 1B context."""
 if locale!="pt":return ""
 items=lookup(text,3)
 if not items:return ""
 return "\nConhecimento local de referência (não são fatos específicos do usuário):\n"+"\n".join(f"- {x['topic']}: {x['text']}" for x in items)[:max_chars]
def stress(n=10000):
 rng=random.Random(1047);start=time.monotonic()
 for i in range(n):
  revenue=D(rng.randint(1000,100000));fixed=D(rng.randint(0,int(revenue)));variable=D(rng.randint(0,20000))
  prompt=f"Tenho uma receita mensal de R$ {revenue}, despesas fixas de R$ {fixed}, despesas variáveis de R$ {variable}."
  ans=solve(prompt)
  assert ans and br(revenue-fixed-variable) in ans["answer"],(i,prompt)
  if i%1000==0:assert lookup("risco de liquidez")
 return {"passed":n,"seconds":round(time.monotonic()-start,2),"offline":True}
def main():
 p=argparse.ArgumentParser();p.add_argument("--test",action="store_true");p.add_argument("--stress",type=int,default=0);p.add_argument("--query");a=p.parse_args()
 init_db()
 if a.test:
  q="Tenho uma receita mensal de R$ 12.500, despesas fixas de R$ 5.200, despesas variáveis de R$ 2.300 e uma dívida de R$ 9.000 com juros de 2% ao mês. Quero quitar destinando R$ 2.000 mensais e melhorar minha reserva de emergência."
  r=solve(q);assert r and "R$ 5.000,00" in r["answer"] and "60.00%" in r["answer"] and "5 meses" in r["answer"]
  assert solve("Como está o mercado hoje?") is None
  assert len(lookup("risco de liquidez"))>0
  print("PASS: integração determinística, dívida, busca local e não-invenção")
 if a.stress:print(json.dumps(stress(a.stress),ensure_ascii=False))
 if a.query:print(json.dumps({"computed":solve(a.query),"knowledge":lookup(a.query)},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
