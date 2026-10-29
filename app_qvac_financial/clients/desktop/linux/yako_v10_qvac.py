"""QVAC bridge. Model loading is on demand to fit low-memory Linux systems."""
import asyncio, time
from yako_v10_core import prompt_for

async def infer(report, emit=None):
    from tetherto.qvac_sdk import Client, load_model, completion, unload_model
    from tetherto.qvac_sdk.models import LLAMA_3_2_1B_INST_Q4_0
    def event(kind, value):
        if emit: emit(kind, value)
    started=time.monotonic(); phases={}; tokens=[]
    event('status','Inicializando QVAC…')
    async with Client() as client:
        phases['worker_seconds']=round(time.monotonic()-started,3)
        event('status','Carregando Llama 3.2 1B…')
        t=time.monotonic(); model_id=None
        try:
            model_id=await load_model(client.transport,model_src=LLAMA_3_2_1B_INST_Q4_0)
            phases['load_seconds']=round(time.monotonic()-t,3)
            event('status','Gerando análise…')
            t=time.monotonic(); first=None
            run=completion(client.transport,model_id=model_id,history=[{'role':'user','content':prompt_for(report)}])
            async for chunk in run.events:
                if getattr(chunk,'type',None)=='contentDelta':
                    part=str(getattr(chunk,'text','') or '')
                    if part:
                        if first is None: first=time.monotonic(); phases['first_token_seconds']=round(first-t,3)
                        tokens.append(part); event('token',part)
            phases['generation_seconds']=round(time.monotonic()-t,3)
        finally:
            if model_id is not None:
                event('status','Liberando memória…')
                await unload_model(client.transport,model_id)
    response=''.join(tokens).strip()
    if not response: raise RuntimeError('QVAC não gerou texto.')
    return {'answer':response,'timings':phases,'total_seconds':round(time.monotonic()-started,3),'engine':'tetherto-qvac-sdk','model':'Llama 3.2 1B Q4_0','offline_verified_by_this_run':False}
