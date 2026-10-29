'use strict';
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const token=document.querySelector('meta[name="yako-session"]').content;let conversationId=null,busy=false,controller=null;
async function api(path,data){const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json','X-Yako-Token':token},body:JSON.stringify(data)});const v=await r.json();if(!r.ok)throw Error(v.error||'Erro');return v}
async function get(path){const r=await fetch(path,{headers:{'X-Yako-Token':token}});if(!r.ok)throw Error('Erro de histórico');return r.json()}
function el(tag,cls,text){const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e}
function bubble(role,content=''){const box=el('article','bubble '+(role==='user'?'user':'assistant'));if(role!=='user')box.append(el('div','who','✳ Yako'));const body=el('div','text',content);box.append(body);$('#messages').append(box);$('#messages').scrollTop=$('#messages').scrollHeight;return body}
function steps(which){for(const id of ['stepRules','stepModel','stepFinish']){$('#'+id).classList.remove('active','done');$('#'+id).querySelector('b').textContent='—'}if(which==='rules'){$('#stepRules').classList.add('done');$('#stepRules b').textContent='✓'}if(which==='model'){$('#stepRules').classList.add('done');$('#stepRules b').textContent='✓';$('#stepModel').classList.add('active');$('#stepModel b').textContent='●'}if(which==='done'){$$('.step').forEach(e=>{e.classList.add('done');e.querySelector('b').textContent='✓'})}}
function evidence(report){const items=report.findings||[];$('#evidenceBadge').textContent=items.length?items.length:'';$('#riskCount').textContent=items.length;const severity=items.some(x=>x.severity==='CRITICAL')?'CRÍTICO':items.some(x=>x.severity==='HIGH')?'ALTO':items.length?'MODERADO':'SEM SINAIS ESPECÍFICOS';$('#severity').textContent=severity;$('#riskPill').textContent=items.length?'REVISÃO':'SEM SINAIS';$('#riskPill').classList.toggle('danger',!!items.length);const list=$('#findings');list.replaceChildren();if(!items.length)list.append(el('div','empty-small','Nenhum sinal específico identificado nesta mensagem. Isso não equivale a uma avaliação de segurança.'));for(const item of items){const row=el('div','finding '+item.severity.toLowerCase());row.append(el('b','',item.flag),el('small','',`Evidência: “${item.evidence}” · ${item.severity}`));list.append(row)}}
function setBusy(v){busy=v;$('#send').disabled=v;$('#prompt').disabled=v;$('#send').innerHTML=v?'<span class="loader-ring"></span>':svgIcon('send')}
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
     finished=true;steps('done');output.textContent=msg.data.answer||output.textContent; if(msg.data.model_used===false || (msg.data.engine||'').includes('Decimal')){$('#stepModel').classList.remove('done','active');$('#stepModel b').textContent='—';}
     $('#metrics').textContent=`Motor: ${msg.data.engine||'local'}\nTempo total: ${msg.data.total_seconds??'—'} s` + (Object.keys(msg.data.timings||{}).length?'\n'+JSON.stringify(msg.data.timings,null,2):'');
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
function show(name){scheduleDrawerClose();for(const n of ['chat','lab','model'])$('#'+n+'View').classList.toggle('hidden',n!==name);$$('.nav').forEach(b=>b.classList.toggle('active',b.dataset.view===name));document.title=({chat:'AI Yako · Intelligence',lab:'AI Yako · Scenario Lab',model:'AI Yako · Model Center'})[name]}
$$('.nav').forEach(b=>b.addEventListener('click',()=>show(b.dataset.view)));$('#new').addEventListener('click',reset);$('#send').addEventListener('click',send);$('#prompt').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send()}});document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();reset()}});$$('[data-prompt]').forEach(b=>b.addEventListener('click',()=>{$('#prompt').value=b.dataset.prompt;send()}));
$('#calculate').addEventListener('click',async()=>{try{const v=await api('/api/simulate',{principal:$('#principal').value,rate:$('#rate').value,months:$('#months').value,contribution:$('#contribution').value});$('#labResult').textContent=`Saldo hipotético: R$ ${v.final_balance.toLocaleString('pt-BR',{minimumFractionDigits:2})} · Total aportado: R$ ${v.total_contributed.toLocaleString('pt-BR',{minimumFractionDigits:2})}`;const svg=$('#chart');svg.replaceChildren();const pts=v.points;const max=Math.max(...pts.map(p=>p.balance),1),min=Math.min(...pts.map(p=>p.balance));const span=Math.max(1,max-min);const coords=pts.map((p,i)=>`${30+i/(pts.length-1)*740},${215-(p.balance-min)/span*180}`).join(' ');const line=document.createElementNS('http://www.w3.org/2000/svg','polyline');line.setAttribute('points',coords);line.setAttribute('fill','none');line.setAttribute('stroke','#5ce3cf');line.setAttribute('stroke-width','3');svg.append(line)}catch(e){$('#labResult').textContent='Erro: '+e.message}});
refreshHistory();

// V10.5: Floating panels. Peek is temporary; explicit click pins panel.
const appRoot=$('.app');
let insightTimer=null, sidebarTimer=null, insightPinned=false, sidebarPinned=true;
function setInsight(open,{pin=false,peek=false}={}){
  clearTimeout(insightTimer);
  insightPinned=pin;
  appRoot.classList.toggle('insights-open',open);
  $('#toggleInsights').setAttribute('aria-expanded',String(open));
  if(open&&peek&&!pin) insightTimer=setTimeout(()=>{if(!insightPinned)setInsight(false)},1700);
}
function setSidebar(open,{pin=false}={}){
  clearTimeout(sidebarTimer);
  sidebarPinned=pin;
  appRoot.classList.toggle('sidebar-collapsed',!open);
  $('#toggleSidebar').setAttribute('aria-expanded',String(open));
}
function scheduleDrawerClose(){ /* V10.8: navegação nunca fecha a sidebar automaticamente */ }
$('#toggleSidebar').addEventListener('click',()=>{
 const opening=appRoot.classList.contains('sidebar-collapsed');setSidebar(opening,{pin:opening});
});
$('#toggleInsights').addEventListener('click',()=>{
 const opening=!appRoot.classList.contains('insights-open');setInsight(opening,{pin:opening});
});
$('#closeInsights').addEventListener('click',()=>setInsight(false));
$('#insights').addEventListener('pointerenter',()=>clearTimeout(insightTimer));

$('#sidebar').addEventListener('pointerenter',()=>clearTimeout(sidebarTimer));
$('#sidebar').addEventListener('pointerleave',scheduleDrawerClose);


// Show the Evidence Engine briefly on first analysis to make discoverability explicit.
const originalEvidence=evidence;
evidence=function(report){originalEvidence(report);const items=Array.isArray(report?.findings)?report.findings:[];const btn=$('#toggleInsights');btn.classList.toggle('has-evidence',items.length>0);btn.classList.toggle('high-evidence',items.some(x=>x.severity==='HIGH'||x.severity==='CRITICAL'));btn.title=items.length?`${items.length} evidência(s) disponível(is)`:'Abrir Evidence Engine';if(items.length){btn.classList.remove('evidence-pulse');void btn.offsetWidth;btn.classList.add('evidence-pulse')}};
document.addEventListener('keydown',e=>{
 if(e.key==='Escape'){setInsight(false);if(matchMedia('(max-width: 850px)').matches)setSidebar(false)}
 if((e.ctrlKey||e.metaKey)&&e.key==='\\'){e.preventDefault();const opening=appRoot.classList.contains('sidebar-collapsed');setSidebar(opening,{pin:opening})}
});
// Desktop starts open and pinned; narrow viewports start collapsed.
setSidebar(!matchMedia('(max-width: 850px)').matches,{pin:!matchMedia('(max-width: 850px)').matches});
// Icons: local inline SVG sprites, no external requests or icon fonts.
const icons={menu:'<path d="M4 7h16M4 12h16M4 17h16"/>',insights:'<path d="m12 2 2.6 6.8L21 12l-6.4 3.2L12 22l-2.6-6.8L3 12l6.4-3.2L12 2Z"/>',send:'<path d="m5 12 7-7 7 7M12 5v14"/>',plus:'<path d="M12 5v14M5 12h14"/>',chat:'<path d="M4 5h16v11H8l-4 4V5Z"/>',chart:'<path d="M4 20V4M4 20h16M7 16l4-5 4 2 5-7"/>',settings:'<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/>'};
function svgIcon(name){return `<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${icons[name]}</svg>`}
$('#toggleSidebar').innerHTML=svgIcon('menu');
$('#toggleInsights').innerHTML=svgIcon('insights')+'<span id="evidenceBadge"></span>';
$('#send').innerHTML=svgIcon('send');
$$('.nav').forEach((b,i)=>{const first=b.querySelector('span');if(first)first.innerHTML=svgIcon(['chat','chart','settings'][i]);});

// V10.6: avoid viewport displacement when the virtual keyboard opens.
if(window.visualViewport){window.visualViewport.addEventListener('resize',()=>{document.documentElement.style.setProperty('--visible-vh',window.visualViewport.height+'px')},{passive:true});}

// V10.8: ao reduzir para mobile, fechar painéis sem roubar foco do chat.
const mobileLayout=matchMedia('(max-width: 850px)');
mobileLayout.addEventListener?.('change',e=>{if(e.matches){setSidebar(false);setInsight(false)}else{setSidebar(true,{pin:true});setInsight(false)}});
$('#toggleInsights').addEventListener('animationend',e=>{if(e.animationName==='yakoPulse')e.currentTarget.classList.remove('evidence-pulse')});

// Mobile starts with the drawer closed, desktop with it open.
if(matchMedia("(max-width: 800px)").matches) setSidebar(false);
