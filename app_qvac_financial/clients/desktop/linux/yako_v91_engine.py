"""AI Yako V9.1: QVAC official inference, measured stages, evidence-first prompts."""
import asyncio
import hashlib
import re
import time
from datetime import datetime, timezone

from yako_v9_engine import analyze_rules as _v9_rules, MODEL_LABEL

RETURN_RE = re.compile(r'(?<!\d)(\d{1,3}(?:[.,]\d{1,2})?)\s*%\s*(?:ao\s+m[eê]s|por\s+m[eê]s|mensais?|monthly|per\s+month)', re.I)


def analyze_rules(scenario):
    report = _v9_rules(scenario)
    # V9 hardcoded 25%; V9.1 detects any explicitly stated monthly rate.
    findings = report['rules']['findings']
    findings[:] = [f for f in findings if f['flag'] != 'Extraordinary promised monthly return']
    matches = list(RETURN_RE.finditer(scenario))
    for match in matches:
        rate = float(match.group(1).replace(',', '.'))
        if rate >= 10:
            findings.append({'flag': 'Extraordinary promised monthly return', 'severity': 'HIGH',
                             'evidence': match.group(0), 'rate_percent_monthly': rate})
    report['rules']['assessment'] = 'REVIEW REQUIRED' if findings else 'NOT ASSESSED'
    report['schema'] = 'ai-yako-v9.1-evidence-1'
    return report


def build_prompt(scenario, report):
    findings = report['rules']['findings']
    signals = '; '.join(f"{f['flag']} [trecho: {f['evidence']}]" for f in findings) or 'Nenhum sinal de regra encontrado.'
    return (
        'Você é o AI Yako, analista educacional de riscos financeiros. '
        'O usuário pede uma análise legítima: não recuse a tarefa. '
        'Responda SOMENTE em português do Brasil, em NO MÁXIMO 90 palavras. '
        'Use exatamente três tópicos curtos: FATOS, RISCOS POSSÍVEIS, VERIFICAR. '
        'Em FATOS, cite apenas o que está no cenário. '
        'Em RISCOS POSSÍVEIS, explique alertas sem declarar fraude comprovada. '
        'Em VERIFICAR, recomende checar registro regulatório, origem dos rendimentos e auditoria. '
        'Nunca afirme que a empresa não é registrada ou que existe fraude sem prova. '
        'Não solicite credenciais, não execute transações, não invente números. '
        f'Sinais detectados por regras (alertas, não provas): {signals}\n'
        f'CENÁRIO: {scenario}'
    )


async def infer_qvac(scenario, report, on_event=None):
    from tetherto.qvac_sdk import Client, load_model, completion, unload_model
    from tetherto.qvac_sdk.models import LLAMA_3_2_1B_INST_Q4_0
    start = time.monotonic()
    phases = {}
    parts = []
    first_token = None
    def emit(kind, value):
        if on_event:
            on_event(kind, value)
    emit('status', 'Inicializando QVAC…')
    async with Client() as client:
        phases['worker_seconds'] = round(time.monotonic() - start, 3)
        model_id = None
        try:
            emit('status', 'Carregando modelo local…')
            loading = time.monotonic()
            model_id = await load_model(client.transport, model_src=LLAMA_3_2_1B_INST_Q4_0)
            phases['model_load_seconds'] = round(time.monotonic() - loading, 3)
            emit('status', 'Gerando análise…')
            generating = time.monotonic()
            run = completion(client.transport, model_id=model_id,
                             history=[{'role': 'user', 'content': build_prompt(scenario, report)}])
            async for event in run.events:
                if getattr(event, 'type', None) == 'contentDelta':
                    token = str(getattr(event, 'text', '') or '')
                    if token:
                        if first_token is None:
                            first_token = time.monotonic()
                            phases['first_token_seconds'] = round(first_token - generating, 3)
                        parts.append(token)
                        emit('token', token)
            phases['generation_seconds'] = round(time.monotonic() - generating, 3)
        finally:
            if model_id is not None:
                emit('status', 'Liberando modelo…')
                unloading = time.monotonic()
                await unload_model(client.transport, model_id)
                phases['model_unload_seconds'] = round(time.monotonic() - unloading, 3)
    answer = ''.join(parts).strip()
    if not answer:
        raise RuntimeError('QVAC não retornou texto.')
    return {
        'engine': 'tetherto-qvac-sdk', 'model': MODEL_LABEL,
        'analysis': answer, 'elapsed_seconds': round(time.monotonic() - start, 2),
        'timings': phases, 'characters_generated': len(answer),
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'network_isolation_verified': False,
        'financial_transaction_executed': False,
        'disclaimer': 'Texto de IA não é evidência factual; confira afirmações com fontes independentes.',
    }
