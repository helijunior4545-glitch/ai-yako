"""AI Yako V10.36. Hosted, authenticated, private-by-account inference.
No wallet, signing, transfer, or browser-side SDK access.
"""
from app_qvac_financial.offline.yako_v1060_verified import solve as verified_solve
import asyncio, importlib.util, json, queue, sys, threading, time
from pathlib import Path
from app_qvac_financial.offline.yako_v1049_engine import solve as hybrid_solve, enrich as hybrid_enrich
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_protect
from app_qvac_financial.server.security.authentication.yako_csrf import yako_csrf_protect
from django.views.decorators.http import require_GET, require_POST
from app_qvac_financial.server.security.authentication.web import current_identity
from app_qvac_financial.server.django.models.authentication import QVACWebCredential
from app_qvac_financial.server.django.models.yako_chat_v1036 import YakoWebConversation, YakoWebMessage

DESKTOP=Path(__file__).resolve().parents[3]/'clients/desktop/linux/yako_v1034'
GATE=threading.BoundedSemaphore(1)

def auth(request):
    identity=current_identity(request)
    if not identity:return None
    return QVACWebCredential.objects.filter(identity=identity,disabled_at__isnull=True).first()

def fail(message,status=400):
    r=JsonResponse({'error':message},status=status);r['Cache-Control']='no-store';return r

def body_json(request):
    if len(request.body)>25000:raise ValueError('Request too large')
    value=json.loads(request.body)
    if not isinstance(value,dict):raise ValueError('Object required')
    return value

def desktop_import(module):
    directory=str(DESKTOP)
    if directory not in sys.path:sys.path.insert(0,directory)
    return __import__(module)

def event(kind,data):return (json.dumps({'type':kind,'data':data},ensure_ascii=False)+'\n').encode('utf-8')

@require_GET
def conversations(request):
    owner=auth(request)
    if not owner:return fail('Authentication required',401)
    rows=YakoWebConversation.objects.filter(owner=owner).values('id','title','created_at')[:100]
    return JsonResponse([{'id':x['id'],'title':x['title'],'created':x['created_at'].isoformat()} for x in rows],safe=False,headers={'Cache-Control':'no-store'})

@require_GET
def messages(request):
    owner=auth(request)
    if not owner:return fail('Authentication required',401)
    try:cid=int(request.GET['id'])
    except (KeyError,ValueError,TypeError):return fail('Invalid conversation')
    convo=YakoWebConversation.objects.filter(owner=owner,id=cid).first()
    if not convo:return fail('Conversation not found',404)
    rows=convo.messages.values('role','content','created_at')[:100]
    return JsonResponse([{'role':x['role'],'content':x['content'],'created':x['created_at'].isoformat()} for x in rows],safe=False,headers={'Cache-Control':'no-store'})

@yako_csrf_protect
@require_POST
def simulate(request):
    if not auth(request):return fail('Authentication required',401)
    try:
        data=body_json(request)
        result=desktop_import('yako_v102_engine').simulation(data.get('principal'),data.get('rate'),data.get('months'),data.get('contribution',0))
        return JsonResponse(result,headers={'Cache-Control':'no-store'})
    except (ValueError,TypeError,ArithmeticError) as e:return fail(str(e)[:180])

@require_GET
def model_capabilities(request):
    if not auth(request):return fail('Authentication required',401)
    available=importlib.util.find_spec('tetherto') is not None
    return JsonResponse({'qvac_sdk_importable':available,'inference_verified':False,'note':'SDK presence does not prove model load or generation.'},headers={'Cache-Control':'no-store'})

@require_GET
def offline_status(request):
    if not auth(request):return fail('Authentication required',401)
    return JsonResponse({'interface':'hosted Django','external_http_calls_in_app':None,'qvac_sdk_importable':importlib.util.find_spec('tetherto') is not None,'model_cache_verified':False,'qvac_inference_verified':False},headers={'Cache-Control':'no-store'})


# YAKO_V1039_THINKING_1B: correct npm-hoisted Bare Runtime without downloads.
def _yako_ensure_bare_worker():
    import os
    from pathlib import Path
    cache = Path.home() / '.cache/qvac/worker/0.22.0/node_modules'
    source = cache / 'bare-runtime-linux-arm64'
    target = cache / '@qvac/sdk/node_modules/bare-runtime-linux-arm64'
    binary = source / 'bin/bare'
    if not (binary.is_file() and os.access(binary, os.X_OK)):
        return  # SDK will report its original error if runtime is unavailable.
    if target.is_symlink():
        if target.resolve() != source.resolve():
            raise RuntimeError('Unexpected Bare Runtime symlink; refusing to change it')
        return
    if target.exists():
        return
    if not (cache / '@qvac/sdk').is_dir():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        target.symlink_to(source, target_is_directory=True)
    except FileExistsError:
        if not (target.is_symlink() and target.resolve() == source.resolve()):
            raise

async def qvac_generate(prompt,locale,out):
    from tetherto.qvac_sdk import Client,load_model,completion,unload_model
    from tetherto.qvac_sdk.models import LLAMA_3_2_1B_INST_Q4_0
    _yako_ensure_bare_worker()
    pieces=[];mid=None
    async with Client() as client:
        out.put(('status','Carregando modelo QVAC no servidor'))
        mid=await load_model(client.transport,model_src=LLAMA_3_2_1B_INST_Q4_0)
        try:
            out.put(('status','Gerando interpretação QVAC'))
            stream=completion(client.transport,model_id=mid,history=[{'role':'user','content':prompt}])
            async for e in stream.events:
                if getattr(e,'type',None)=='contentDelta':
                    chunk=str(getattr(e,'text','') or '')
                    if chunk:pieces.append(chunk);out.put(('token',chunk))
        finally:
            if mid is not None:
                try:
                    await unload_model(client.transport,mid)
                except Exception as exc:
                    # A failed cleanup must not discard already generated text.
                    out.put(('cleanup_warning',type(exc).__name__))
                    if not ''.join(pieces).strip():
                        raise
    return ''.join(pieces).strip()

@yako_csrf_protect
@require_POST
def analyze_stream(request):
    owner=auth(request)
    if not owner:return fail('Authentication required',401)
    try:
        data=body_json(request);scenario=data.get('text');mode=data.get('mode','qvac');locale=data.get('locale','en')
        if not isinstance(scenario,str) or not 1<=len(scenario.strip())<=12000:raise ValueError('Invalid scenario')
        if mode not in ('qvac','rules'):raise ValueError('Invalid mode')
        if locale not in ('en','pt','es','fr'):locale='en'
        cid=data.get('conversation_id')
        if cid is None:
            convo=YakoWebConversation.objects.create(owner=owner,title=scenario.strip()[:65])
        else:
            convo=YakoWebConversation.objects.filter(owner=owner,id=int(cid)).first()
            if convo is None:return fail('Conversation not found',404)
        engine=desktop_import('yako_v102_engine')
        report=engine.analyze(scenario)
        risks=desktop_import('yako_v1019_risks')
        localized=risks.localized_findings(report,locale)
        YakoWebMessage.objects.create(conversation=convo,role='user',content=scenario)
    except (ValueError,TypeError,KeyError,json.JSONDecodeError) as e:return fail(str(e)[:150])
    started=time.monotonic()
    def produce():
        yield event('start',{'conversation_id':convo.id,'report':localized,'explanation':engine.explain(report)})
        answer='';metadata={};stream_q=queue.Queue()
        try:
            # All calculations and risk rules originate from the original V10.34 modules.
            def calc():
                solve=desktop_import('yako_v1030_reasoning').reason
                portfolio=desktop_import('yako_v1023_portfolio').analyze_portfolio
                finance=desktop_import('yako_v1033_finance')
                if mode=='qvac':
                    return (verified_solve(scenario,locale) or hybrid_solve(scenario,locale)) or solve(scenario,locale) or portfolio(scenario,locale) or finance.analyze_natural_finance(scenario,locale) or finance.explain_concept(scenario,locale)
                return (verified_solve(scenario,locale) or hybrid_solve(scenario,locale)) or solve(scenario,locale) or portfolio(scenario,locale) or finance.analyze_natural_finance(scenario,locale) or desktop_import('yako_v1020_finance').smart_analysis(scenario,locale)
            try:computed=calc()
            except (ValueError,ArithmeticError):computed=None
            if computed:
                answer=computed['answer'];metadata=dict(computed);metadata['model_used']=False
            elif mode=='rules':
                answer=risks.localized_report(report,locale) or 'No specific signals detected. This does not establish safety.'
                metadata={'engine':'Deterministic evidence','model_used':False}
            else:
                if not GATE.acquire(blocking=False):
                    yield event('error',{'message':'QVAC busy','fallback':'Model is processing another request. Try again.'});return
                try:
                    def worker():
                        try:
                            context=desktop_import('yako_v1025_reasoning').build_reasoning_context(scenario,locale,[])
                            language={'en':'English','pt':'Brazilian Portuguese','es':'Spanish','fr':'French'}[locale]
                            prompt=context+hybrid_enrich(scenario,locale)+'\nRespond ONLY in '+language+'. Do not invent figures. Show checkable formulas for all derived monetary values.'
                            stream_q.put(('result',asyncio.run(qvac_generate(prompt,locale,stream_q))))
                        except Exception as exc:stream_q.put(('exception',type(exc).__name__+': '+str(exc)[:200]))
                        finally:stream_q.put(('finished',None))
                    threading.Thread(target=worker,daemon=True).start()
                    generated='';failure=None
                    while True:
                        try:kind,value=stream_q.get(timeout=2)
                        except queue.Empty:
                            yield event('heartbeat',None);continue
                        if kind=='finished':break
                        if kind=='token':generated+=value;yield event('token',value)
                        elif kind=='status':yield event('status',value)
                        elif kind=='exception':failure=value
                        elif kind=='result':generated=value
                    if failure:
                        answer=desktop_import('yako_v1025_reasoning').verified_fallback(scenario,locale,report)
                        metadata={'engine':'Verified deterministic fallback — QVAC unavailable','model_used':False,'qvac_error':failure,'error_stage':'inference'}
                    else:
                        review=desktop_import('yako_v1028_consistency').review_financial_consistency(generated,scenario,locale)
                        revised=review['answer'];verdict=desktop_import('yako_v1027_validation').validate_financial_response(revised,scenario)
                        if not revised or not verdict['accepted']:
                            answer=desktop_import('yako_v1025_reasoning').verified_fallback(scenario,locale,report)
                            metadata={'engine':'Verified fallback — QVAC answer rejected','model_used':True,'response_accepted':False,'rejection_reason':verdict.get('reason','empty')}
                        else:
                            answer=revised;metadata={'engine':'QVAC hosted — Llama 3.2 1B','model_used':True,'response_accepted':True}
                finally:GATE.release()
            YakoWebMessage.objects.create(conversation_id=convo.id,role='assistant',content=answer)
            metadata.update(answer=answer,total_seconds=round(time.monotonic()-started,2))
            yield event('done',metadata)
        except Exception as exc:
            yield event('error',{'message':'Processing error: '+type(exc).__name__,'fallback':'The analysis could not be completed.'})
    response=StreamingHttpResponse(produce(),content_type='application/x-ndjson; charset=utf-8')
    response['Cache-Control']='no-store, no-transform';response['X-Content-Type-Options']='nosniff';response['X-Accel-Buffering']='no'
    return response