"""QVAC V10.42: serial inference with bounded idle model reuse and stage telemetry.
Only the original local SDK/model is used. No remote services are introduced.
"""
import asyncio
import logging
import os
import queue
import threading
import time

LOG=logging.getLogger('yako.qvac.v1042')
LANG={'en':'English','pt':'Brazilian Portuguese','es':'Spanish','fr':'French'}
IDLE_SECONDS=90
JOBS=queue.Queue(maxsize=1)
LOCK=threading.Lock()
THREAD=None

def _log(stage,started,**fields):
    # Never log the user prompt, generated text or SDK credentials.
    LOG.warning('QVAC_V1042 stage=%s elapsed=%.2fs %s',stage,time.monotonic()-started,
                ' '.join('%s=%s'%(k,v) for k,v in fields.items()))

def _start_worker():
    global THREAD
    with LOCK:
        if THREAD is None or not THREAD.is_alive():
            THREAD=threading.Thread(target=lambda:asyncio.run(_serve()),daemon=True,name='yako-qvac-v1042')
            THREAD.start()

def infer(reasoning,locale,events,stop,started):
    _start_worker()
    response=queue.Queue(maxsize=1)
    try:
        JOBS.put_nowait((reasoning,locale,events,stop,started,response))
    except queue.Full:
        return {'error':'QVAC worker busy','error_stage':'capacity','total_seconds':round(time.monotonic()-started,2)}
    # Do not terminate a running SDK operation from another thread: it may corrupt its state.
    # Heartbeats remain active in the HTTP handler until the SDK finishes.
    return response.get()

async def _serve():
    from tetherto.qvac_sdk import Client,load_model,completion,unload_model
    from tetherto.qvac_sdk.models import LLAMA_3_2_1B_INST_Q4_0
    while True:
        async with Client() as client:
            mid=None
            while True:
                try:
                    job=await asyncio.to_thread(JOBS.get,True,IDLE_SECONDS)
                except queue.Empty:
                    break
                reasoning,locale,events,stop,started,response=job
                stage='sdk_client';phases={};parts=[];first=None
                try:
                    if stop.is_set():
                        raise RuntimeError('request_cancelled')
                    if mid is None:
                        stage='model_load';events.put(('status','Carregando modelo local'))
                        t=time.monotonic();_log('model_load_start',started)
                        mid=await load_model(client.transport,model_src=LLAMA_3_2_1B_INST_Q4_0)
                        phases['load_seconds']=round(time.monotonic()-t,2)
                        _log('model_load_done',started,load_seconds=phases['load_seconds'])
                    else:
                        phases['load_seconds']=0.0
                        _log('model_reused',started)
                    stage='generation';events.put(('status','Gerando interpretação'))
                    t=time.monotonic()
                    instruction=(reasoning+'\nRespond ONLY in '+LANG.get(locale,'English')+
                        '. Treat only the CURRENT scenario as facts. Only state monetary amounts and percentages supplied by the user or derived with explicit, checkable arithmetic from those amounts. Show the formula for every derived number. Do not use earlier scenarios.')
                    run=completion(client.transport,model_id=mid,history=[{'role':'user','content':instruction}])
                    async for event in run.events:
                        if stop.is_set():break
                        if getattr(event,'type',None)=='contentDelta':
                            part=str(getattr(event,'text','') or '')
                            if part:
                                if first is None:
                                    first=time.monotonic()
                                    phases['first_token_seconds']=round(first-t,2)
                                    _log('first_token',started,first_token_seconds=phases['first_token_seconds'])
                                parts.append(part)
                    phases['generation_seconds']=round(time.monotonic()-t,2)
                    _log('generation_done',started,generation_seconds=phases['generation_seconds'])
                    response.put({'answer':''.join(parts).strip(),'timings':phases,
                        'total_seconds':round(time.monotonic()-started,2),
                        'engine':'QVAC local — Llama 3.2 1B','model_used':True})
                except Exception as e:
                    _log('error',started,error_type=type(e).__name__,stage=stage)
                    response.put({'error':f'{type(e).__name__}: {str(e)[:400]}',
                        'error_stage':stage,'total_seconds':round(time.monotonic()-started,2)})
                    # On SDK error discard the session instead of reusing a possibly invalid model.
                    break
            if mid is not None:
                try:
                    t=time.monotonic()
                    await unload_model(client.transport,mid)
                    LOG.warning('QVAC_V1042 stage=model_unload duration=%.2fs',time.monotonic()-t)
                except Exception as e:
                    LOG.warning('QVAC_V1042 stage=model_unload_failed error_type=%s',type(e).__name__)
        # Restart a fresh client for subsequent requests; the thread remains available.
