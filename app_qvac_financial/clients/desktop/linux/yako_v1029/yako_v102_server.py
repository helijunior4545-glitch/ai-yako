"""Loopback-only UI/API server. No cloud services, wallet access, or Django required."""
import asyncio, json, os, secrets, sqlite3, threading, queue, time, webbrowser, sys, importlib.util
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse,parse_qs
from yako_v102_engine import analyze, explain, prompt, simulation, calculate_from_chat, safe_fallback, grounded_risk_answer
from yako_v1019_finance import business_analysis, LANGS
from yako_v1020_finance import smart_analysis
from yako_v1023_portfolio import analyze_portfolio
from yako_v1029_solver import solve as solve_investments
from yako_v1019_risks import localized_report, localized_findings
from yako_v1025_reasoning import build_reasoning_context, classify_request
from yako_v1027_validation import validate_financial_response
from yako_v1028_consistency import review_financial_consistency
ROOT=Path(__file__).resolve().parent
DATA=Path.home()/'.local/share/ai-yako-v102'
DB=DATA/'history.sqlite3'
TOKEN=secrets.token_urlsafe(32)
ASSETS={'/':'yako_v102_ui.html','/app.css':'yako_v102_ui.css','/app.js':'yako_v102_ui.js'}
MIME={'/':'text/html; charset=utf-8','/app.css':'text/css; charset=utf-8','/app.js':'application/javascript; charset=utf-8'}
LOCK=threading.Lock()

def init_db():
    DATA.mkdir(parents=True,exist_ok=True,mode=0o700)
    os.chmod(DATA,0o700)
    with sqlite3.connect(DB) as db:
        db.execute('CREATE TABLE IF NOT EXISTS conversations(id INTEGER PRIMARY KEY, title TEXT NOT NULL, created TEXT DEFAULT CURRENT_TIMESTAMP)')
        db.execute('CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, conversation_id INTEGER NOT NULL, role TEXT NOT NULL, content TEXT NOT NULL, created TEXT DEFAULT CURRENT_TIMESTAMP)')
        db.commit()
    os.chmod(DB,0o600)

def db_query(sql,args=(),fetch=False):
    with LOCK,sqlite3.connect(DB,timeout=10) as db:
        cur=db.execute(sql,args)
        result=cur.fetchall() if fetch else cur.lastrowid
        db.commit();return result

class Handler(BaseHTTPRequestHandler):
    protocol_version='HTTP/1.1'
    def log_message(self,format,*args):pass
    def send(self,code,data,kind='application/json; charset=utf-8'):
        body=data if isinstance(data,bytes) else json.dumps(data,ensure_ascii=False).encode()
        self.send_response(code);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(body)))
        self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('X-Frame-Options','DENY');self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Content-Security-Policy',"default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers();self.wfile.write(body)
    def check(self):
        host=self.headers.get('Host','').split(':')[0]
        if host not in ('127.0.0.1','localhost'):return False
        origin=self.headers.get('Origin')
        if origin and origin!=f'http://{self.headers.get("Host")}':return False
        return self.headers.get('X-Yako-Token')==TOKEN
    def do_GET(self):
        url=urlparse(self.path)
        if url.path in ASSETS:
            data=(ROOT/ASSETS[url.path]).read_bytes()
            if url.path=='/':data=data.replace(b'__SESSION_TOKEN__',TOKEN.encode())
            return self.send(200,data,MIME[url.path])
        if not self.check():return self.send(403,{'error':'Acesso negado'})
        if url.path=='/api/offline-status':
            spec=importlib.util.find_spec('tetherto')
            return self.send(200,{'interface':'loopback-only','external_http_calls_in_app':False,'qvac_sdk_importable':bool(spec),'model_cache_verified':False,'qvac_inference_verified':False,'note':'This diagnostic does not prove offline QVAC inference. Disconnect network and run a prompt that actually invokes QVAC to verify the model cache.'})
        if url.path=='/api/conversations':
            rows=db_query('SELECT id,title,created FROM conversations ORDER BY id DESC LIMIT 100',fetch=True)
            return self.send(200,[{'id':r[0],'title':r[1],'created':r[2]} for r in rows])
        if url.path=='/api/messages':
            try:cid=int(parse_qs(url.query)['id'][0])
            except (KeyError,ValueError,IndexError):return self.send(400,{'error':'ID inválido'})
            rows=db_query('SELECT role,content,created FROM messages WHERE conversation_id=? ORDER BY id LIMIT 100',(cid,),True)
            return self.send(200,[{'role':r[0],'content':r[1],'created':r[2]} for r in rows])
        return self.send(404,{'error':'Não encontrado'})
    def read_json(self):
        try:n=int(self.headers.get('Content-Length','0'))
        except ValueError:raise ValueError('Tamanho inválido')
        if n<1 or n>25000:raise ValueError('Corpo excede limite')
        return json.loads(self.rfile.read(n))
    def do_POST(self):
        if not self.check():return self.send(403,{'error':'Acesso negado'})
        try:body=self.read_json()
        except (ValueError,json.JSONDecodeError) as e:return self.send(400,{'error':str(e)})
        path=urlparse(self.path).path
        if path=='/api/simulate':
            try:return self.send(200,simulation(body.get('principal'),body.get('rate'),body.get('months'),body.get('contribution',0)))
            except ValueError as e:return self.send(400,{'error':str(e)})
        if path=='/api/analyze':return self.analyze_stream(body)
        return self.send(404,{'error':'Não encontrado'})
    def analyze_stream(self,body):
        scenario=body.get('text','');mode=body.get('mode','qvac')
        locale=body.get('locale','en')
        if locale not in LANGS:locale='en'
        try:report=analyze(scenario)
        except ValueError as e:return self.send(400,{'error':str(e)})
        if mode not in ('qvac','rules'):return self.send(400,{'error':'Modo inválido'})
        cid=body.get('conversation_id')
        if cid is not None:
            try:cid=int(cid)
            except (TypeError,ValueError):return self.send(400,{'error':'Conversa inválida'})
            if not db_query('SELECT id FROM conversations WHERE id=?',(cid,),True):return self.send(404,{'error':'Conversa não encontrada'})
        else:cid=db_query('INSERT INTO conversations(title) VALUES (?)',(scenario[:65],))
        history=db_query('SELECT role,content FROM messages WHERE conversation_id=? ORDER BY id DESC LIMIT 24',(cid,),True)
        history=[{'role':r[0],'content':r[1]} for r in reversed(history)]
        # Financial arithmetic is a trusted tool, not an LLM task.
        try:
            computed=(solve_investments(scenario,locale) or analyze_portfolio(scenario,locale)) if mode=='qvac' else (solve_investments(scenario,locale) or analyze_portfolio(scenario,locale) or smart_analysis(scenario,locale))
            if computed is None and locale=='pt':computed=calculate_from_chat(scenario,[])
        except (ValueError,ArithmeticError):computed=None
        db_query('INSERT INTO messages(conversation_id,role,content) VALUES (?,?,?)',(cid,'user',scenario))
        self.send_response(200);self.send_header('Content-Type','application/x-ndjson; charset=utf-8')
        self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Connection','close');self.end_headers();self.close_connection=True
        def emit(kind,data):
            try:self.wfile.write((json.dumps({'type':kind,'data':data},ensure_ascii=False)+'\n').encode());self.wfile.flush();return True
            except (BrokenPipeError,ConnectionResetError,OSError):return False
        emit('start',{'conversation_id':cid,'report':localized_findings(report,locale),'explanation':explain(report)})
        if computed:
            emit('done',computed)
            db_query('INSERT INTO messages(conversation_id,role,content) VALUES (?,?,?)',(cid,'assistant',computed['answer']))
            return
        if mode=='rules':
            answer=(localized_report(report,locale) or ({'en':'No specific signals detected. This does not establish safety.','pt':'Nenhum sinal específico detectado. Isso não comprova segurança.','es':'No se detectaron señales específicas. Esto no garantiza seguridad.','fr':'Aucun signal spécifique détecté. Cela ne garantit pas la sécurité.'}[locale]));emit('done',{'answer':answer,'engine':'deterministic','total_seconds':0})
            db_query('INSERT INTO messages(conversation_id,role,content) VALUES (?,?,?)',(cid,'assistant',answer));return
        q=queue.Queue();result={};stop=threading.Event()
        reasoning=build_reasoning_context(scenario,locale,history)
        def work():
            async def run():
                from tetherto.qvac_sdk import Client,load_model,completion,unload_model
                from tetherto.qvac_sdk.models import LLAMA_3_2_1B_INST_Q4_0
                started=time.monotonic();phases={};parts=[]
                q.put(('status','Inicializando QVAC'))
                async with Client() as client:
                    phases['worker_seconds']=round(time.monotonic()-started,2)
                    q.put(('status','Carregando modelo local'))
                    t=time.monotonic();mid=None
                    try:
                        mid=await load_model(client.transport,model_src=LLAMA_3_2_1B_INST_Q4_0)
                        phases['load_seconds']=round(time.monotonic()-t,2)
                        q.put(('status','Gerando interpretação'))
                        t=time.monotonic();first=None
                        run=completion(client.transport,model_id=mid,history=[{'role':'user','content':(reasoning+'\nRespond ONLY in '+{'en':'English','pt':'Brazilian Portuguese','es':'Spanish','fr':'French'}[locale]+'. Treat only the CURRENT scenario as facts. Only state monetary amounts and percentages supplied by the user or derived with explicit, checkable arithmetic from those amounts. Show the formula for every derived number. Do not use earlier scenarios.')}])
                        async for event in run.events:
                            if stop.is_set():break
                            if getattr(event,'type',None)=='contentDelta':
                                part=str(getattr(event,'text','') or '')
                                if part:
                                    if first is None:first=time.monotonic();phases['first_token_seconds']=round(first-t,2)
                                    parts.append(part)
                        phases['generation_seconds']=round(time.monotonic()-t,2)
                    finally:
                        if mid is not None:
                            q.put(('status','Liberando modelo'))
                            await unload_model(client.transport,mid)
                return {'answer':''.join(parts).strip(),'timings':phases,'total_seconds':round(time.monotonic()-started,2),'engine':'QVAC local — Llama 3.2 1B','model_used':True}
            try:result.update(asyncio.run(run()))
            except Exception as e:result['error']=f'{type(e).__name__}: {e}'
            finally:q.put(('finished',None))
        threading.Thread(target=work,daemon=True).start()
        while True:
            try:kind,data=q.get(timeout=1)
            except queue.Empty:
                if not emit('heartbeat',None):stop.set();break
                continue
            if kind=='finished':break
            if not emit(kind,data):stop.set();break
        if not stop.is_set():
            if result.get('error'):
                answer=reasoning_fallback(scenario,locale,report)
                emit('done',{'answer':answer,'engine':'Verified local fallback — QVAC unavailable',
                    'model_used':False,'inference_executed':False,'response_accepted':False,
                    'rejection_reason':'qvac_runtime_error','qvac_error':result['error'],'total_seconds':0})
            else:
                original=result.get('answer','')
                review=review_financial_consistency(original,scenario,locale)
                original=review['answer']
                verdict=validate_financial_response(original,scenario)
                result['consistency_review']={'flags':review['flags'],'repaired':review['repaired']}
                refusal=any(x in original.casefold() for x in ('não posso fornecer','nao posso fornecer','não consigo calcular','nao consigo calcular'))
                reason=('empty_model_response' if not original else
                        'model_refusal' if refusal else
                        verdict['reason'] if not verdict['accepted'] else None)
                result['inference_executed']=True
                result['response_accepted']=reason is None
                result['rejection_reason']=reason
                result['financial_validation']=verdict
                if reason:
                    answer=reasoning_fallback(scenario,locale,report)
                    result['answer']=answer
                    result['engine']='Verified local fallback — model response rejected'
                    result['model_used']=True  # The QVAC model ran, but its output was rejected.
                else:
                    answer=original
                emit('done',result)
            db_query('INSERT INTO messages(conversation_id,role,content) VALUES (?,?,?)',(cid,'assistant',answer))

def reasoning_fallback(scenario,locale,report):
    from yako_v1025_reasoning import verified_fallback
    return verified_fallback(scenario,locale,report)

def untrusted_numbers(answer,scenario):
    """Compatibility wrapper for older modules; new validation provides detailed diagnostics."""
    return not validate_financial_response(answer,scenario)['accepted']

def main():
    init_db()
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    url=f'http://127.0.0.1:{server.server_port}/'
    print('AI Yako V10.29 — local interface:',url,flush=True)
    webbrowser.open(url)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':main()

