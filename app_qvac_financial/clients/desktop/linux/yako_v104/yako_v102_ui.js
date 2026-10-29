'use strict';
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const token=document.querySelector('meta[name="yako-session"]').content;let conversationId=null,busy=false,controller=null;
async function api(path,data){const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json','X-Yako-Token':token},body:JSON.stringify(data)});const v=await r.json();if(!r.ok)throw Error(v.error||'Erro');return v}
async function get(path){const r=await fetch(path,{headers:{'X-Yako-Token':token}});if(!r.ok)throw Error('Erro de histórico');return r.json()}
function el(tag,cls,text){const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e}
function bubble(role,content=''){const box=el('article','bubble '+(role==='user'?'user':'assistant'));if(role!=='user')box.append(el('div','who','✳ Yako'));const body=el('div','text',content);box.append(body);$('#messages').append(box);$('#messages').scrollTop=$('#messages').scrollHeight;return body}
function steps(which){for(const id of ['stepRules','stepModel','stepFinish']){$('#'+id).classList.remove('active','done');$('#'+id).querySelector('b').textContent='—'}if(which==='rules'){$('#stepRules').classList.add('done');$('#stepRules b').textContent='✓'}if(which==='model'){$('#stepRules').classList.add('done');$('#stepRules b').textContent='✓';$('#stepModel').classList.add('active');$('#stepModel b').textContent='●'}if(which==='done'){$$('.step').forEach(e=>{e.classList.add('done');e.querySelector('b').textContent='✓'})}}
function evidence(report){const items=report.findings||[];$('#evidenceBadge').textContent=items.length?items.length:'';$('#riskCount').textContent=items.length;const severity=items.some(x=>x.severity==='CRITICAL')?'CRÍTICO':items.some(x=>x.severity==='HIGH')?'ALTO':items.length?'MODERADO':'NÃO AVALIADO';$('#severity').textContent=severity;$('#riskPill').textContent=items.length?'REVISÃO':'NÃO AVALIADO';$('#riskPill').classList.toggle('danger',!!items.length);const list=$('#findings');list.replaceChildren();if(!items.length)list.append(el('div','empty-small','Nenhum padrão reconhecido. Isso não demonstra segurança.'));for(const item of items){const row=el('div','finding '+item.severity.toLowerCase());row.append(el('b','',item.flag),el('small','',`Evidência: “${item.evidence}” · ${item.severity}`));list.append(row)}}
function setBusy(v){busy=v;$('#send').disabled=v;$('#prompt').disabled=v;$('#send').textContent=v?'◌':'↑'}
async function send(){
 if(busy)return;
 const text=$('#prompt').value.trim();if(!text)return;
 $('#prompt').value='';$('#hero')?.remove();bubble('user',text);
 const output=bubble('assistant','');setBusy(true);steps('rules');
 $('#metrics').textContent='Iniciando análise...';
 let resultText='',finished=false;const mode=$('#mode').value;
 try{
  controller=new AbortController();
  const r=await fetch('/api/analyze',{
   method:'POST',headers:{'Content-Type':'application/json','X-Yako-Token':token},
   body:JSON.stringify({text,mode,conversation_id:conversationId}),signal:controller.signal
  });
  if(!r.ok){const e=await r.json();throw Error(e.error||'Falha de análise')}
  const reader=r.body.getReader(),decoder=new TextDecoder();let pending='';
  while(true){
   const {value,done}=await reader.read();if(done)break;
   pending+=decoder.decode(value,{stream:true});let i;
   while((i=pending.indexOf('\n'))>=0){
    const line=pending.slice(0,i);pending=pending.slice(i+1);
    if(!line.trim())continue;
    const msg=JSON.parse(line);
    if(msg.type==='start'){
     conversationId=msg.data.conversation_id;evidence(msg.data.report);
     steps(mode==='qvac'?'model':'rules');
     output.textContent=mode==='rules'?msg.data.explanation:'Evidências verificadas. Inicializando interpretação QVAC…';
    }else if(msg.type==='status'){
     $('#metrics').textContent=msg.data;
    }else if(msg.type==='token'){
     if(!resultText)output.textContent='';
     resultText+=msg.data;output.textContent=resultText;
     $('#messages').scrollTop=$('#messages').scrollHeight;
    }else if(msg.type==='done'){
     finished=true;steps('done');output.textContent=msg.data.answer||output.textContent;
     $('#metrics').textContent=`Motor: ${msg.data.engine||'local'}\nTempo total: ${msg.data.total_seconds??'—'} s\n${JSON.stringify(msg.data.timings||{},null,2)}`;
     output.parentElement.append(el('div','meta','Resposta gerada localmente. Verifique conclusões e fontes.'));
    }else if(msg.type==='error'){
     finished=true;steps('done');output.textContent='QVAC indisponível. Análise determinística:\n'+msg.data.fallback;
     $('#metrics').textContent=msg.data.message;
    }
   }
  }
  if(!finished)throw Error('A análise terminou sem confirmação.');
  await refreshHistory();
 }catch(e){
  output.textContent+='\n\n⚠ '+e.message;$('#metrics').textContent='Falha: '+e.message;
 }finally{setBusy(false);controller=null}
}
async function refreshHistory(){try{const rows=await get('/api/conversations');const container=$('#history');container.replaceChildren();for(const row of rows){const b=el('button',row.id===conversationId?'selected':'',row.title);b.title=row.title;b.addEventListener('click',()=>loadConversation(row.id));container.append(b)}}catch(e){$('#history').textContent='Histórico indisponível'}}
async function loadConversation(id){if(busy)return;const rows=await get('/api/messages?id='+encodeURIComponent(id));conversationId=id;$('#hero')?.remove();$('#messages').replaceChildren();for(const row of rows)bubble(row.role,row.content);evidence({findings:[]});steps('rules');$('#metrics').textContent='Histórico carregado · evidências não recalculadas';show('chat');refreshHistory()}
function reset(){if(busy)return;conversationId=null;$('#messages').replaceChildren();const h=el('div','hero');h.id='hero';h.append(el('div','hero-orbit','✳'),el('div','eyebrow','FINANCIAL INTELLIGENCE · PRIVATE BY DESIGN'));const title=el('h1');title.textContent='Uma nova investigação começa aqui.';h.append(title,el('p','','Faça uma pergunta sobre riscos ou cenários financeiros.'));$('#messages').append(h);evidence({findings:[]});steps('rules');$('#metrics').textContent='Aguardando análise.';show('chat');$('#prompt').focus();refreshHistory()}
function show(name){scheduleDrawerClose();for(const n of ['chat','lab','model'])$('#'+n+'View').classList.toggle('hidden',n!==name);$$('.nav').forEach(b=>b.classList.toggle('active',b.dataset.view===name));$('#pageName').textContent=({chat:'AI Intelligence',lab:'Scenario Lab',model:'Model Center'})[name]}
$$('.nav').forEach(b=>b.addEventListener('click',()=>show(b.dataset.view)));$('#new').addEventListener('click',reset);$('#send').addEventListener('click',send);$('#prompt').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send()}});document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();reset()}});$$('[data-prompt]').forEach(b=>b.addEventListener('click',()=>{$('#prompt').value=b.dataset.prompt;send()}));
$('#calculate').addEventListener('click',async()=>{try{const v=await api('/api/simulate',{principal:$('#principal').value,rate:$('#rate').value,months:$('#months').value,contribution:$('#contribution').value});$('#labResult').textContent=`Saldo hipotético: R$ ${v.final_balance.toLocaleString('pt-BR',{minimumFractionDigits:2})} · Total aportado: R$ ${v.total_contributed.toLocaleString('pt-BR',{minimumFractionDigits:2})}`;const svg=$('#chart');svg.replaceChildren();const pts=v.points;const max=Math.max(...pts.map(p=>p.balance),1),min=Math.min(...pts.map(p=>p.balance));const span=Math.max(1,max-min);const coords=pts.map((p,i)=>`${30+i/(pts.length-1)*740},${215-(p.balance-min)/span*180}`).join(' ');const line=document.createElementNS('http://www.w3.org/2000/svg','polyline');line.setAttribute('points',coords);line.setAttribute('fill','none');line.setAttribute('stroke','#5ce3cf');line.setAttribute('stroke-width','3');svg.append(line)}catch(e){$('#labResult').textContent='Erro: '+e.message}});
refreshHistory();

// Single navigation drawer, optional contextual evidence overlay.
const appRoot=$('.app');
$('#toggleSidebar').addEventListener('click',()=>appRoot.classList.toggle('sidebar-collapsed'));
$('#toggleInsights').addEventListener('click',()=>appRoot.classList.toggle('insights-open'));
$('#closeInsights').addEventListener('click',()=>appRoot.classList.remove('insights-open'));
document.addEventListener('keydown',e=>{if(e.key==='Escape')appRoot.classList.remove('insights-open');if((e.ctrlKey||e.metaKey)&&e.key==='\\'){e.preventDefault();appRoot.classList.toggle('sidebar-collapsed')}});
if(matchMedia('(max-width: 850px)').matches)appRoot.classList.add('sidebar-collapsed');

// V10.4: sidebar initially open; when a workspace topic is opened, close it after 1.65s.
let drawerTimer=null;
function scheduleDrawerClose(){
  clearTimeout(drawerTimer);
  if(!appRoot.classList.contains('sidebar-collapsed')){
    drawerTimer=setTimeout(()=>{
      if(!document.activeElement?.closest('.sidebar')) appRoot.classList.add('sidebar-collapsed');
    },1650);
  }
}
const originalSidebarToggle=$('#toggleSidebar');
originalSidebarToggle.addEventListener('click',()=>{clearTimeout(drawerTimer);});
$('#sidebar').addEventListener('pointerenter',()=>clearTimeout(drawerTimer));
$('#sidebar').addEventListener('pointerleave',()=>{if(!appRoot.classList.contains('sidebar-collapsed'))scheduleDrawerClose()});
$('#toggleInsights').addEventListener('click',()=>{
  const opened=appRoot.classList.contains('insights-open');
  $('#toggleInsights').setAttribute('aria-expanded',String(opened));
});
$('#toggleSidebar').setAttribute('aria-expanded','true');
const watchSidebar=new MutationObserver(()=>$('#toggleSidebar').setAttribute('aria-expanded',String(!appRoot.classList.contains('sidebar-collapsed'))));
watchSidebar.observe(appRoot,{attributes:true,attributeFilter:['class']});
// User can keep the drawer open by focusing a control or clicking its toggle.
