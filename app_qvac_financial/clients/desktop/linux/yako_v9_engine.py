"""AI Yako V9: deterministic evidence + official QVAC catalog inference."""
import asyncio
import hashlib
import time
from datetime import datetime, timezone

MODEL_LABEL = 'Llama 3.2 1B Instruct Q4_0 (QVAC catalog)'
RULES = (
    (('private key', 'chave privada', 'seed phrase', 'frase semente'), 'Possible credential exposure', 'CRITICAL'),
    (('urgent', 'urgente', 'immediately', 'imediatamente'), 'Urgency pressure', 'HIGH'),
    (('guaranteed', 'garantido', 'garantida', 'sem risco', 'risk-free'), 'Unrealistic guarantee', 'HIGH'),
    (('leverage', 'alavancagem', 'alavancado'), 'Leverage exposure', 'HIGH'),
    (('all funds', 'todo o dinheiro', 'todas as economias'), 'Concentration risk', 'HIGH'),
    (('25% monthly', '25% ao mês', '25% por mês'), 'Extraordinary promised monthly return', 'HIGH'),
)


def analyze_rules(scenario):
    if not isinstance(scenario, str) or not scenario.strip():
        raise ValueError('Informe um cenário financeiro.')
    if len(scenario) > 12000:
        raise ValueError('O cenário deve ter no máximo 12.000 caracteres.')
    text = scenario.casefold()
    findings = [{'flag': label, 'severity': severity, 'evidence': next(term for term in terms if term in text)}
                for terms, label, severity in RULES if any(term in text for term in terms)]
    return {
        'schema': 'ai-yako-v9-evidence-1',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'scenario_sha256': hashlib.sha256(scenario.encode('utf-8')).hexdigest(),
        'rules': {'assessment': 'REVIEW REQUIRED' if findings else 'NOT ASSESSED', 'findings': findings},
        'financial_execution': 'DISABLED',
        'network_isolation_verified': False,
    }


def build_prompt(scenario, report):
    findings = report['rules']['findings']
    flags = '; '.join(f"{f['flag']} (matched: {f['evidence']})" for f in findings) or 'No predefined rule matched.'
    return (
        'You are AI Yako, a cautious financial risk explainer. This is a legitimate request to identify risks, '
        'not a request to commit fraud or make a trade. Do not refuse ordinary risk analysis. '
        'Do not execute transactions, request secrets, promise returns, or invent facts. '
        'Clearly separate stated facts, rule-based warning signals, uncertainty, and prudent verification steps. '
        'A guarantee of extraordinary returns may indicate an unsustainable offer or possible fraud; '
        'do not assert fraud as proven. Respond concisely in the language of the scenario.\n'
        f'Deterministic warning signals (keyword matches, not proof): {flags}\n'
        f'Scenario: {scenario}'
    )


async def infer_qvac(scenario, report, on_event=None):
    """Runs official SDK catalog model. The SDK may contact a registry if uncached."""
    from tetherto.qvac_sdk import Client, load_model, completion, unload_model
    from tetherto.qvac_sdk.models import LLAMA_3_2_1B_INST_Q4_0
    started = time.monotonic()
    chunks = []
    def emit(kind, value):
        if on_event:
            on_event(kind, value)
    emit('status', 'Inicializando worker QVAC…')
    async with Client() as client:
        model_id = None
        try:
            emit('status', 'Carregando modelo QVAC…')
            model_id = await load_model(client.transport, model_src=LLAMA_3_2_1B_INST_Q4_0)
            emit('status', 'Gerando análise local…')
            run = completion(client.transport, model_id=model_id,
                             history=[{'role': 'user', 'content': build_prompt(scenario, report)}])
            async for event in run.events:
                if getattr(event, 'type', None) == 'contentDelta':
                    token = str(getattr(event, 'text', '') or '')
                    chunks.append(token)
                    emit('token', token)
        finally:
            if model_id is not None:
                emit('status', 'Liberando modelo…')
                await unload_model(client.transport, model_id)
    answer = ''.join(chunks).strip()
    if not answer:
        raise RuntimeError('O QVAC não produziu conteúdo.')
    return {'engine': 'tetherto-qvac-sdk', 'model': MODEL_LABEL,
            'analysis': answer, 'elapsed_seconds': round(time.monotonic() - started, 2),
            'network_isolation_verified': False}
