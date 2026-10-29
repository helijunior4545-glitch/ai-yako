"""General-purpose offline reasoning context; no hardcoded response templates for model."""
import re
from decimal import Decimal

def classify_request(text):
    t=text.casefold()
    signals={
      'liquidity': ('liquidity','cash flow','receivable','overdue','liquidez','fluxo de caixa','inadimpl','contas a receber'),
      'investment': ('investment','investimento','portfolio','portfólio','capital allocation'),
      'credit': ('loan','financing','debt','empréstimo','dívida','financiamento'),
      'strategy': ('recommend','strategy','decision','risk','recomend','estratégia','risco'),
      'explanation': ('explain','why','how','explique','por que','como'),
    }
    return [k for k,terms in signals.items() if any(term in t for term in terms)] or ['general']

def build_reasoning_context(text,locale='en',history=()):
    if not isinstance(text,str) or not text.strip():raise ValueError('Empty question')
    lang={'en':'English','pt':'Brazilian Portuguese','es':'Spanish','fr':'French'}.get(locale,'English')
    context=[]
    for item in list(history)[-6:]:
        role=item.get('role','')
        if role in ('user','assistant'):
            context.append(role.upper()+': '+str(item.get('content',''))[:700])
    return ("You are Yako, a private offline financial reasoning assistant. Answer the user's ACTUAL question, not a predefined template. "
        "Understand paraphrases and unstructured descriptions. Distinguish evidence, arithmetic, assumptions, unknowns and recommendations. "
        "Do not invent facts, numbers, external sources, market data, or financial certainty. "
        "When numbers are given, show formulas and calculations only when justified; never guess missing variables. "
        "Do not confuse recognized revenue with cash collected. Identify risks and practical options. "
        "When the user asks several questions, address each one explicitly. "
        "If the question is conceptual, explain conceptually instead of returning a generic finance report. "
        "If a portfolio is supplied, respect every stated dependency, exclusion and reserve requirement. "
        "Do not claim external internet access or real-time data. "
        "Reply in "+lang+".\n"
        "PREVIOUS CONVERSATION (context only, not verified current financial facts):\n"+'\n'.join(context)+"\n"
        "CURRENT USER REQUEST (authoritative current facts):\n"+text)

def verified_fallback(text,locale='en',report=None):
    # Honest fallback; never pretend a generic deterministic template is LLM reasoning.
    is_pt=locale=='pt'
    intro=('O modelo QVAC local não produziu uma resposta verificável. ' if is_pt else 'The local QVAC model did not produce a verifiable response. ')
    intro+=('A análise automática de texto livre está indisponível nesta execução.' if is_pt else 'Free-form reasoning is unavailable in this run.')
    if report and report.get('findings'):
        from yako_v1019_risks import localized_report
        return intro+'\n\n'+localized_report(report,locale)
    return intro+'\n'+('Verifique o modelo instalado e o log de inferência.' if is_pt else 'Check the installed model and inference logs.')
