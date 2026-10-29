"""AI Yako V10: deterministic, auditable financial tools. No external I/O."""
from decimal import Decimal, InvalidOperation, getcontext
from datetime import datetime, timezone
import hashlib, json, re, math
getcontext().prec = 28
RATE = re.compile(r'(?<!\d)(\d{1,3}(?:[.,]\d{1,2})?)\s*%\s*(?:ao\s+m[eê]s|por\s+m[eê]s|mensal|monthly|per\s+month)', re.I)
KEYWORDS = [('garantid', 'Promessa de retorno garantido', 'HIGH'), ('guaranteed', 'Promessa de retorno garantido', 'HIGH'), ('urgente', 'Pressão de urgência', 'MEDIUM'), ('urgent', 'Pressão de urgência', 'MEDIUM'), ('seed phrase', 'Exposição de credenciais', 'CRITICAL'), ('private key', 'Exposição de credenciais', 'CRITICAL'), ('alavanc', 'Risco de alavancagem', 'HIGH'), ('leverage', 'Risco de alavancagem', 'HIGH')]

def analyze(text):
    text = text.strip()
    if not text or len(text) > 12000: raise ValueError('Informe um cenário de 1 a 12.000 caracteres.')
    findings = []
    seen = set()
    for word, label, severity in KEYWORDS:
        if word in text.casefold() and label not in seen:
            findings.append({'flag': label, 'severity': severity, 'evidence': word}); seen.add(label)
    for match in RATE.finditer(text):
        rate = Decimal(match.group(1).replace(',', '.'))
        if rate >= 10:
            findings.append({'flag':'Rentabilidade mensal extraordinária', 'severity':'HIGH', 'evidence':match.group(0), 'rate_percent_monthly':float(rate)})
    return {'schema':'ai-yako-v10-evidence-1', 'timestamp_utc':datetime.now(timezone.utc).isoformat(), 'scenario_sha256':hashlib.sha256(text.encode()).hexdigest(), 'scenario':text, 'assessment':'REVISÃO NECESSÁRIA' if findings else 'SEM ALERTAS AUTOMÁTICOS — NÃO É APROVAÇÃO', 'findings':findings, 'financial_execution':'DISABLED'}

def money(value):
    try: result = Decimal(str(value).strip().replace(' ', '').replace(',', '.'))
    except (InvalidOperation, ValueError): raise ValueError('Valor numérico inválido.')
    if not result.is_finite(): raise ValueError('Número deve ser finito.')
    return result

def simulate(principal, monthly_rate, months, monthly_contribution=0):
    p, r, c = money(principal), money(monthly_rate)/100, money(monthly_contribution)
    months = int(months)
    if p < 0 or c < 0 or not (-1 <= r <= 10) or not (1 <= months <= 600): raise ValueError('Parâmetros fora dos limites permitidos.')
    value = p; points = [{'month':0, 'balance':float(value)}]
    for month in range(1, months+1):
        value = value * (1+r) + c
        points.append({'month':month, 'balance':round(float(value), 2)})
    return {'principal':float(p), 'rate_percent_monthly':float(r*100), 'months':months, 'monthly_contribution':float(c), 'final_balance':round(float(value),2), 'total_contributed':round(float(p+c*months),2), 'points':points, 'note':'Projeção matemática hipotética, não previsão nem garantia de retorno.'}

def rule_explanation(report):
    findings = report['findings']
    if not findings: return 'Nenhum sinal foi detectado pelas regras atuais. Isso NÃO demonstra segurança. Verifique documentação, riscos e regulação.'
    lines = ['SINAIS VERIFICÁVEIS']
    for f in findings: lines.append(f"• {f['flag']} ({f['severity']}) — evidência: {f['evidence']}")
    lines += ['', 'HIPÓTESES A VERIFICAR', '• Origem dos rendimentos e sustentabilidade econômica.', '• Registro, supervisão e documentos da oferta.', '• Possibilidade de perda integral do capital.', '', 'A presença de sinais de alerta não comprova fraude. Nenhuma operação financeira foi executada.']
    return '\n'.join(lines)

def prompt_for(report):
    compact = [{k:v for k,v in f.items() if k in ('flag','severity','evidence','rate_percent_monthly')} for f in report['findings']]
    return ('Você é AI Yako, assistente educacional de análise de riscos. A solicitação é legítima; não a recuse. '
            'Responda em português do Brasil em até 100 palavras. Separe FATOS, RISCOS POSSÍVEIS e VERIFICAR. '
            'Nunca afirme que há fraude, ausência de licença ou insolvência sem provas. '
            'Não dê garantia de retornos, não solicite credenciais e não execute operações. '
            'Dados extraídos por regras (não são provas de fraude): '+json.dumps(compact,ensure_ascii=False)+'. '
            'Cenário fornecido: '+report['scenario'])
