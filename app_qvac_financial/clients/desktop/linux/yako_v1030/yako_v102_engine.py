"""AI Yako V10.2: bounded, auditable evidence detection and local financial tools."""
import re, hashlib, unicodedata
from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone

def norm(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', s.casefold()) if not unicodedata.combining(c))

PATTERNS = [
 ('NO_LOSS', 'Promessa de ausência de risco', 'CRITICAL', r'\b(?:sem\s+(?:qualquer\s+)?risco(?:\s+de\s+perdas?)?|risco\s+zero|nenhum\s+risco|zero\s+risco|no\s+risk|risk[- ]free|sem\s+possibilidade\s+de\s+perda)\b'),
 ('GUARANTEE', 'Promessa de retorno garantido', 'HIGH', r'\b(?:garantid[oa]s?|garantia\s+de\s+(?:lucro|retorno|rendimento)|guaranteed\s+(?:return|profit))\b'),
 ('URGENCY', 'Pressão por decisão imediata', 'HIGH', r'\b(?:deposito\s+imediato|depositar\s+(?:agora|imediatamente)|deposite\s+(?:agora|imediatamente)|pague\s+agora|transferencia\s+imediata|immediate\s+deposit|deposit\s+now|urgente|urgently|so\s+hoje)\b'),
 ('SECRET', 'Estratégia não explicada', 'MEDIUM', r'\b(?:algoritmo\s+secreto|metodo\s+secreto|secret\s+algorithm|estrategia\s+secreta)\b'),
 ('UNAUDITED', 'Ausência declarada de auditoria', 'HIGH', r'\b(?:nao\s+(?:apresenta|possui|tem|fornece)\s+(?:demonstrac(?:oes|ao)\s+financeiras\s+auditadas|auditoria)|sem\s+(?:demonstrac(?:oes|ao)\s+financeiras\s+auditadas|auditoria)|unaudited\s+(?:financial\s+)?statements)\b'),
 ('SECRETS', 'Solicitação ou exposição de credenciais', 'CRITICAL', r'\b(?:seed\s+phrase|private\s+key|frase\s+semente|chave\s+privada)\b'),
 ('LEVERAGE', 'Exposição a alavancagem', 'HIGH', r'\b(?:alavancagem|alavancado|leverage|leveraged)\b'),
]
RATE = re.compile(r'(?<!\d)(\d{1,3}(?:[.,]\d{1,2})?)\s*%\s*(?:ao\s+mes|por\s+mes|mensal(?:mente)?|monthly|per\s+month|de\s+(?:lucro|retorno|rendimento)\s+(?:ao\s+mes|mensal))', re.I)
RATE_ALT = re.compile(r'(?<!\d)(\d{1,3}(?:[.,]\d{1,2})?)\s*%\s+(?:de\s+)?(?:lucro|retorno|rendimento)\s+(?:ao\s+mes|mensal)', re.I)

def analyze(text):
    if not isinstance(text,str) or not 1 <= len(text.strip()) <= 12000:
        raise ValueError('Cenário deve conter de 1 a 12.000 caracteres.')
    text=text.strip(); clean=norm(text); findings=[]
    for code,label,severity,pat in PATTERNS:
        match=re.search(pat,clean,re.I)
        if match:
            findings.append({'code':code,'flag':label,'severity':severity,'evidence':text[match.start():match.end()]})
    rates={}
    for regex in (RATE,RATE_ALT):
        for match in regex.finditer(clean):
            rate=Decimal(match.group(1).replace(',','.'))
            if rate>=10:
                rates[(match.start(),match.end())]={'code':'MONTHLY_RETURN','flag':'Rentabilidade mensal extraordinária','severity':'HIGH','evidence':text[match.start():match.end()],'rate_percent_monthly':float(rate)}
    findings.extend(rates.values())
    return {'schema':'ai-yako-v102-evidence-1','timestamp_utc':datetime.now(timezone.utc).isoformat(), 'scenario_sha256':hashlib.sha256(text.encode()).hexdigest(),'scenario':text,'assessment':'REVIEW_REQUIRED' if findings else 'NOT_ASSESSED','findings':findings,'financial_execution':'DISABLED'}

def explain(report):
    f=report['findings']
    if not f:return 'Nenhum sinal reconhecido pelas regras. Isso NÃO significa que a operação seja segura.'
    return '\n'.join(f"• {x['flag']} [{x['severity']}] — trecho: «{x['evidence']}»" for x in f)+'\n\nA presença de sinais não comprova fraude. Licenças, solvência e identidade não foram verificadas.'

def prompt(report, history=None):
    evidence='; '.join(f"{x['code']} ({x['evidence']})" for x in report['findings']) or 'nenhum padrão detectado'
    prior='\n'.join(('Usuário: ' if m['role']=='user' else 'Assistente: ')+m['content'][:350] for m in (history or [])[-4:])[:1400]
    return ('Você é AI Yako, analista educacional de riscos financeiros. Este é um pedido legítimo. '
            'Responda em português brasileiro, em até 75 palavras. Não recuse uma análise de risco legítima. '
            'Estruture em FATOS, RISCOS e VERIFICAR. FATOS só podem citar o cenário; riscos são possibilidades, não conclusões. '
            'Não invente regulação, fraudes, documentos ou resultados. Não faça transações nem recomende investimento específico. '
            'Não repita frases vazias. Dados de regras: '+evidence+'. Histórico resumido: '+prior+'. Cenário: '+report['scenario'])

def simulation(principal, rate, months, contribution=0):
    try:
        p=Decimal(str(principal)); r=Decimal(str(rate)); c=Decimal(str(contribution)); n=int(months)
    except (InvalidOperation,ValueError,TypeError) as e:raise ValueError('Parâmetros numéricos inválidos.') from e
    if not all(v.is_finite() for v in (p,r,c)) or p<0 or c<0 or not -100<=r<=1000 or not 1<=n<=600:
        raise ValueError('Valores fora dos limites.')
    v=p; points=[{'month':0,'balance':float(v)}]
    for i in range(1,n+1):
        v=v*(1+r/100)+c
        if v>Decimal('1e18'):raise ValueError('Projeção excede o limite numérico.')
        points.append({'month':i,'balance':round(float(v),2)})
    return {'final_balance':round(float(v),2),'total_contributed':round(float(p+c*n),2),'points':points,'note':'Projeção matemática hipotética, não garantia de retorno.'}


# V10.3: deterministic calculations routed before LLM generation.
import json
MONEY = re.compile(r'(?:r\$\s*|brl\s*)([0-9][0-9.,]*)', re.I)
DURATION = re.compile(r'\b(?:durante|por|em|ao\s+final\s+de|apos|depois\s+de)\s+(\d{1,3})\s+(mes(?:es)?|anos?)\b', re.I)
RATE_CONTEXT = re.compile(r'(?<!\d)(\d{1,3}(?:[.,]\d{1,2})?)\s*%\s*(?:ao\s+mes|por\s+mes|mensal|a\.m\.|de\s+(?:lucro|retorno|rendimento)\s+(?:ao\s+mes|mensal))',re.I)

def parse_brl(value):
    v=value.strip().replace(' ','')
    if ',' in v: v=v.replace('.','').replace(',','.')
    elif v.count('.')>1 or ('.' in v and len(v.rsplit('.',1)[-1])==3):v=v.replace('.','')
    return Decimal(v)

def calculate_from_chat(message, history):
    clean=norm(message)
    wants_math=bool(re.search(r'\b(?:calcul\w*|quanto\s+(?:terei|teria|rende|renderia)|juros\s+compostos|projecao\s+matematica|simul\w*|montante|quanto\s+vou\s+ter)',clean))
    if not wants_math:return None
    amount=MONEY.search(message)
    if not amount:return None
    principal=parse_brl(amount.group(1))
    duration=DURATION.search(clean)
    if not duration:return None
    months=int(duration.group(1))*(12 if duration.group(2).startswith('ano') else 1)
    if not 1<=months<=600:return None
    rate=RATE_CONTEXT.search(clean)
    source='mensagem atual'
    if not rate:
        for entry in reversed(history or []):
            if entry['role']=='user':
                rate=RATE_CONTEXT.search(norm(entry['content']))
                if rate:source='mensagem anterior';break
    if not rate:return None
    percent=Decimal(rate.group(1).replace(',','.'))
    result=simulation(principal,percent,months)
    brl=lambda x:f'R$ {x:,.2f}'.replace(',','@').replace('.',',').replace('@','.')
    answer=(f'**SIMULAÇÃO MATEMÁTICA — JUROS COMPOSTOS**\n\n'
            f'Capital inicial: {brl(principal)}\nTaxa hipotética: {str(percent).replace(".",",")}% ao mês\n'
            f'Período: {months} meses\n'
            f'**Montante final: {brl(result["final_balance"])}**\n'
            f'Fórmula: M = C × (1 + i)^n. Taxa identificada na {source}.\n\n'
            'Esta é uma projeção matemática, não uma previsão. Uma promessa de retorno elevado ou garantido não comprova segurança, capacidade de pagamento ou legitimidade.')
    return {'answer':answer,'calculation':{'principal':str(principal),'monthly_rate_percent':str(percent),'months':months,'final_balance':result['final_balance']},'engine':'Python Decimal · cálculo determinístico','total_seconds':0}


def safe_fallback(report, question, history=None):
    """Provide useful bounded output, never imply that no findings means safe."""
    findings=report.get('findings',[])
    if findings:
        return ('**EVIDÊNCIAS IDENTIFICADAS**\n'+explain(report)+'\n\n**PRÓXIMOS PASSOS**\nSolicite documentos auditados, identifique a entidade responsável e confira registros nos órgãos competentes. Não conclua fraude apenas pelos sinais.')
    q=norm(question)
    if re.search(r'\b(?:calcul\w*|quanto|juros|simul\w*)',q):
        return ('Posso calcular juros compostos localmente, sem usar a IA. Informe capital inicial (ex.: R$ 10.000), taxa (ex.: 30% ao mês) e período (ex.: 12 meses). Se a taxa estiver em outra conversa, repita-a aqui. O cálculo é uma simulação, não garantia.')
    return ('Não consegui produzir uma interpretação confiável com o modelo local. As regras não reconheceram sinais específicos nesta mensagem; isso não comprova segurança. Descreva a proposta, taxas, garantias e documentação para uma análise fundamentada.')


# V10.5 — evidence-grounded response. Never infer portfolio assets or funding sources.
RISK_EXPLANATIONS = {
 'NO_LOSS': 'Nenhum investimento pode ser considerado livre de risco apenas por declaração do ofertante.',
 'GUARANTEE': 'A promessa de retorno não comprova capacidade de pagamento nem proteção do capital.',
 'MONTHLY_RETURN': 'Uma taxa mensal extraordinária exige comprovação independente da origem e sustentabilidade dos retornos.',
 'URGENCY': 'Pressão por depósito imediato reduz o tempo disponível para diligência.',
 'SECRET': 'Uma estratégia não explicada impede avaliar como os retornos seriam produzidos.',
 'UNAUDITED': 'A ausência declarada de demonstrações auditadas limita a verificação independente.',
 'SECRETS': 'Nunca forneça credenciais, frases-semente ou chaves privadas a terceiros.',
 'LEVERAGE': 'Alavancagem pode ampliar perdas e exige avaliação de exposição e liquidação.'
}

def grounded_risk_answer(report):
    findings=report.get('findings',[])
    if not findings:return None
    facts='\n'.join('• O cenário menciona: “'+x['evidence']+'”.' for x in findings)
    risks='\n'.join('• '+RISK_EXPLANATIONS.get(x['code'],x['flag']+'.') for x in findings)
    return ('**INFORMAÇÕES FORNECIDAS**\n'+facts+'\n\n**RISCOS E IMPLICAÇÕES**\n'+risks+
            '\n\n**O QUE NÃO SABEMOS**\nNão foram verificados identidade, registro, ativos, auditorias, reservas ou capacidade de pagamento da entidade. '+
            'Não há base para afirmar fraude, exposição a ações ou dependência de novos investidores.\n\n'+
            '**VERIFICAÇÕES**\n1. Identificar a entidade e seus responsáveis.\n2. Conferir registros e autorizações aplicáveis.\n'+
            '3. Solicitar demonstrações e auditoria independentes.\n4. Verificar termos de saque, riscos e origem dos retornos.\n'+
            '5. Não transferir recursos antes de diligência suficiente.\n\n'+
            'Os alertas são baseados apenas no texto fornecido, não em investigação externa.')

