/* YAKO_V1036_FULL_RUNTIME — original V10.34 JS, adapted network only */
function yakoDesktopToken(){return document.querySelector('meta[name="yako-session"]')?.content||''}
'use strict';
// V10.37: Do not parse redirected HTML or non-JSON responses as API data.
async function yakoReadJsonResponse(r){
  if(r.redirected)throw Error('A requisição foi redirecionada. Atualize a página e entre novamente.');
  const ct=(r.headers.get('content-type')||'').toLowerCase();
  if(!ct.includes('application/json'))throw Error('A API retornou um formato inesperado (HTTP '+r.status+').');
  let data;
  try{data=await r.json()}catch(_){throw Error('Resposta JSON inválida da API.');}
  if(!r.ok)throw Error((data&&data.error)||'Falha na API (HTTP '+r.status+').');
  return data;
}
function yakoAssertStreamResponse(r){
  if(r.redirected)throw Error('A requisição foi redirecionada. Atualize a página e entre novamente.');
  const ct=(r.headers.get('content-type')||'').toLowerCase();
  if(!r.ok)throw Error('Falha na análise (HTTP '+r.status+').');
  if(!ct.includes('application/x-ndjson'))throw Error('A API não retornou o fluxo NDJSON esperado.');
  if(!r.body)throw Error('O navegador não recebeu o fluxo de resposta.');
}

const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const token='';let conversationId=null,busy=false,controller=null;
async function api(path,data){const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json','X-Yako-Token':yakoDesktopToken()},body:JSON.stringify(data)});return await yakoReadJsonResponse(r)}
async function get(path){const r=await fetch(path,{headers:{'X-Yako-Token':yakoDesktopToken()}});return yakoReadJsonResponse(r)}
function el(tag,cls,text){const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e}
// V10.22: copy exact message text, including historical messages and streamed answers.
const YAKO_COPY_I18N={
 en:{copy:'Copy message',copied:'Copied',failed:'Could not copy',empty:'Nothing to copy'},
 pt:{copy:'Copiar mensagem',copied:'Copiado',failed:'Não foi possível copiar',empty:'Nada para copiar'},
 es:{copy:'Copiar mensaje',copied:'Copiado',failed:'No se pudo copiar',empty:'Nada para copiar'},
 fr:{copy:'Copier le message',copied:'Copié',failed:'Copie impossible',empty:'Rien à copier'}
};
function copyWords(){return YAKO_COPY_I18N[typeof language==='string'?language:'en']||YAKO_COPY_I18N.en}
async function yakoCopyText(value){
 if(navigator.clipboard&&window.isSecureContext){try{await navigator.clipboard.writeText(value);return true}catch(_){/* fallback below */}}
 // Local-only fallback: no server request, no external service.
 const field=document.createElement('textarea');field.value=value;field.setAttribute('readonly','');
 field.style.cssText='position:fixed;left:-9999px;top:0;opacity:0;pointer-events:none';
 document.body.append(field);field.focus();field.select();
 let ok=false;try{ok=document.execCommand('copy')}catch(_){}finally{field.remove()}
 return ok;
}
function bubble(role,content=''){
 const box=el('article','bubble '+(role==='user'?'user':'assistant'));
 if(role!=='user')box.append(el('div','who','✳ Yako'));
 const body=el('div','text',content);box.append(body);
 const actions=el('div','yako-message-actions');
 const button=el('button','yako-copy-action');button.type='button';
 button.setAttribute('aria-label',copyWords().copy);button.title=copyWords().copy;
 button.innerHTML='<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/></svg>';
 const label=el('span','yako-copy-label',copyWords().copy);button.append(label);
 const live=el('span','yako-copy-live');live.setAttribute('role','status');live.setAttribute('aria-live','polite');
 let timer;
 button.addEventListener('click',async()=>{
  if(button.disabled)return;
  const words=copyWords();const value=body.textContent;
  if(!value.trim()){live.textContent=words.empty;return}
  button.disabled=true;
  const ok=await yakoCopyText(value);
  button.disabled=false;
  clearTimeout(timer);
  label.textContent=ok?words.copied:words.failed;
  live.textContent=ok?words.copied:words.failed;
  button.classList.toggle('is-copied',ok);
  timer=setTimeout(()=>{label.textContent=copyWords().copy;button.classList.remove('is-copied');live.textContent=''},1900);
 });
 actions.append(button,live);box.append(actions);
 $('#messages').append(box);$('#messages').scrollTop=$('#messages').scrollHeight;
 return body;
}
function yakoProgressiveReveal(target,answer){
 const reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
 target.textContent='';target.classList.add('yako-structured-response');
 const segments=String(answer||'').split(/\n\n+/).filter(Boolean);
 if(reduce||segments.length<2){target.textContent=answer||'';return}
 const fragment=document.createDocumentFragment();
 for(let i=0;i<segments.length;i++){
  const block=document.createElement('div');block.className='yako-reveal-block';
  block.textContent=segments[i];block.style.setProperty('--reveal-index',String(Math.min(i,9)));
  fragment.append(block);
 }
 target.append(fragment);
 // All text is in DOM immediately; animations only affect presentation.
 $('#messages').scrollTop=$('#messages').scrollHeight;
}
function steps(which){for(const id of ['stepRules','stepModel','stepFinish']){$('#'+id).classList.remove('active','done');$('#'+id).querySelector('b').textContent='—'}if(which==='rules'){$('#stepRules').classList.add('done');$('#stepRules b').textContent='✓'}if(which==='model'){$('#stepRules').classList.add('done');$('#stepRules b').textContent='✓';$('#stepModel').classList.add('active');$('#stepModel b').textContent='●'}if(which==='done'){$$('.step').forEach(e=>{e.classList.add('done');e.querySelector('b').textContent='✓'})}}
function evidence(report){const items=report.findings||[];$('#evidenceBadge').textContent=items.length?items.length:'';$('#riskCount').textContent=items.length;const severity=items.some(x=>x.severity==='CRITICAL')?t('critical'):items.some(x=>x.severity==='HIGH')?t('high'):items.length?t('medium'):t('noSignalsShort');$('#severity').textContent=severity;$('#riskPill').textContent=items.length?t('review'):t('noSignalsShort');$('#riskPill').classList.toggle('danger',!!items.length);const list=$('#findings');list.replaceChildren();if(!items.length)list.append(el('div','empty-small',t('noSignals')));for(const item of items){const row=el('div','finding '+item.severity.toLowerCase());row.append(el('b','',item.flag),el('small','',`${t('evidence')}: “${item.evidence}” · ${item.severity}`));list.append(row)}}
function setBusy(v){busy=v;$('#send').disabled=v;$('#prompt').disabled=v;$('#send').innerHTML=v?'<span class="loader-ring"></span>':svgIcon('send');yakoV1040HeaderActivity(v)}
async function send(){
 if(busy)return;
 const text=$('#prompt').value.trim();if(!text)return;
 $('#prompt').value='';window.yakoResizeComposer?.();$('#hero')?.remove();bubble('user',text);
 const output=bubble('assistant','');setBusy(true);steps('rules');
 $('#metrics').textContent=t('working');
 let resultText='',finished=false;const mode=$('#mode').value;
 try{
  controller=new AbortController();
  const r=await fetch('/api/analyze',{
   method:'POST',headers:{'Content-Type':'application/json','X-Yako-Token':yakoDesktopToken()},
   body:JSON.stringify({text,mode,conversation_id:conversationId,locale:language}),signal:controller.signal
  });
  if(!r.ok){await yakoReadJsonResponse(r);throw Error('Falha de análise')}yakoAssertStreamResponse(r)
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
     output.textContent=t('working');output.parentElement.classList.add('yako-processing');
    }else if(msg.type==='status'){
     $('#metrics').textContent=msg.data;
    }else if(msg.type==='token'){
     if(!resultText)output.textContent='';
     resultText+=msg.data;output.textContent=resultText;
     $('#messages').scrollTop=$('#messages').scrollHeight;
    }else if(msg.type==='done'){
     finished=true;steps('done');output.parentElement.classList.remove('yako-processing');yakoProgressiveReveal(output,msg.data.answer||output.textContent); if(msg.data.model_used===false || (msg.data.engine||'').includes('Decimal')){$('#stepModel').classList.remove('done','active');$('#stepModel b').textContent='—';}
     $('#metrics').textContent=`Motor: ${msg.data.engine||'local'}\nTempo total: ${msg.data.total_seconds??'—'} s` + (msg.data.rejection_reason?'\nMotivo: '+msg.data.rejection_reason:'') + (msg.data.error_stage?'\nEtapa: '+msg.data.error_stage:'') + (msg.data.qvac_error?'\nErro QVAC: '+msg.data.qvac_error:'') + (msg.data.model_output_characters!==undefined?'\nCaracteres gerados: '+msg.data.model_output_characters:'') + (Object.keys(msg.data.timings||{}).length?'\n'+JSON.stringify(msg.data.timings,null,2):'');
     output.parentElement.append(el('div','meta',t('localDisclaimer')));
    }else if(msg.type==='error'){
     finished=true;steps('done');output.parentElement.classList.remove('yako-processing');output.textContent=t('modelUnavailable')+'\n'+msg.data.fallback;
     $('#metrics').textContent=msg.data.message;
    }
   }
  }
  if(!finished)throw Error(t('unfinished'));
  await refreshHistory();
 }catch(e){
  output.textContent+='\n\n⚠ '+e.message;$('#metrics').textContent=t('error')+': '+e.message;
 }finally{setBusy(false);controller=null}
}
async function refreshHistory(){try{const rows=await get('/api/conversations');const container=$('#history');container.replaceChildren();for(const row of rows){const b=el('button',row.id===conversationId?'selected':'',row.title);b.title=row.title;b.setAttribute('aria-label',row.title);b.dataset.historyTitle=row.title;b.addEventListener('click',()=>loadConversation(row.id));container.append(b)}}catch(e){$('#history').textContent=t('historyUnavailable')}}
async function loadConversation(id){if(busy)return;const rows=await get('/api/messages?id='+encodeURIComponent(id));conversationId=id;$('#hero')?.remove();$('#messages').replaceChildren();for(const row of rows)bubble(row.role,row.content);evidence({findings:[]});steps('rules');$('#metrics').textContent=t('historyLoaded');show('chat');refreshHistory()}
function reset(){if(busy)return;conversationId=null;$('#messages').replaceChildren();const h=el('div','hero');h.id='hero';h.append(el('div','hero-orbit','✳'),el('div','eyebrow','FINANCIAL INTELLIGENCE · PRIVATE BY DESIGN'));const title=el('h1');title.textContent=t('resetTitle');h.append(title,el('p','',t('resetDescription')));$('#messages').append(h);evidence({findings:[]});steps('rules');$('#metrics').textContent=t('waiting');show('chat');$('#prompt').focus();refreshHistory()}
function show(name){document.querySelector('.main').classList.toggle('non-chat',name!=='chat');scheduleDrawerClose();for(const n of ['chat','lab','model'])$('#'+n+'View').classList.toggle('hidden',n!==name);$$('.nav').forEach(b=>b.classList.toggle('active',b.dataset.view===name));document.title=({chat:'AI Yako · Intelligence',lab:'AI Yako · Scenario Lab',model:'AI Yako · Model Center'})[name]}
$$('.nav').forEach(b=>b.addEventListener('click',()=>show(b.dataset.view)));$('#new').addEventListener('click',reset);$('#send').addEventListener('click',send);$('#prompt').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.isComposing&&e.keyCode!==229){e.preventDefault();send()}});document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();reset()}});$$('[data-prompt]').forEach(b=>b.addEventListener('click',()=>{if(busy)return;$('#prompt').value=b.dataset.prompt;$('#mode').value='rules';window.yakoResizeComposer?.();send()}));
$('#calculate').addEventListener('click',async()=>{try{const v=await api('/api/simulate',{principal:$('#principal').value,rate:$('#rate').value,months:$('#months').value,contribution:$('#contribution').value});$('#labResult').textContent=`Saldo hipotético: R$ ${v.final_balance.toLocaleString('pt-BR',{minimumFractionDigits:2})} · Total aportado: R$ ${v.total_contributed.toLocaleString('pt-BR',{minimumFractionDigits:2})}`;const svg=$('#chart');svg.replaceChildren();const pts=v.points;const max=Math.max(...pts.map(p=>p.balance),1),min=Math.min(...pts.map(p=>p.balance));const span=Math.max(1,max-min);const coords=pts.map((p,i)=>`${30+i/(pts.length-1)*740},${215-(p.balance-min)/span*180}`).join(' ');const line=document.createElementNS('http://www.w3.org/2000/svg','polyline');line.setAttribute('points',coords);line.setAttribute('fill','none');line.setAttribute('stroke','#5ce3cf');line.setAttribute('stroke-width','3');svg.append(line)}catch(e){$('#labResult').textContent=t('error')+': '+e.message}});
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
  const rail=$('#railToggle');if(rail){rail.setAttribute('aria-expanded',String(open));rail.setAttribute('aria-label',open?'Recolher menu':'Expandir menu');rail.title=open?'Recolher menu':'Expandir menu';}
  try{localStorage.setItem('yako-sidebar-open',String(open))}catch(_){}
}
function scheduleDrawerClose(){ /* V10.8: navegação nunca fecha a sidebar automaticamente */ }
$('#railToggle')?.addEventListener('click',()=>{const opening=appRoot.classList.contains('sidebar-collapsed');setSidebar(opening,{pin:opening})});
$('#toggleInsights').addEventListener('click',()=>{
 const opening=!appRoot.classList.contains('insights-open');setInsight(opening,{pin:opening});
});
$('#closeInsights').addEventListener('click',()=>setInsight(false));
$('#insights').addEventListener('pointerenter',()=>clearTimeout(insightTimer));

$('#sidebar').addEventListener('pointerenter',()=>clearTimeout(sidebarTimer));
$('#sidebar').addEventListener('pointerleave',scheduleDrawerClose);


// Show the Evidence Engine briefly on first analysis to make discoverability explicit.
const originalEvidence=evidence;
evidence=function(report){originalEvidence(report);const items=Array.isArray(report?.findings)?report.findings:[];const btn=$('#toggleInsights');btn.classList.toggle('has-evidence',items.length>0);btn.classList.toggle('high-evidence',items.some(x=>x.severity==='HIGH'||x.severity==='CRITICAL'));btn.title=items.length?`${items.length} evidência(s) disponível(is)`:t('openEvidence');if(items.length){btn.classList.remove('evidence-pulse');void btn.offsetWidth;btn.classList.add('evidence-pulse')}};
document.addEventListener('keydown',e=>{
 if(e.key==='Escape'){setInsight(false);if(matchMedia('(max-width: 850px)').matches)setSidebar(false)}
 if((e.ctrlKey||e.metaKey)&&e.key==='\\'){e.preventDefault();const opening=appRoot.classList.contains('sidebar-collapsed');setSidebar(opening,{pin:opening})}
});
// Desktop starts open and pinned; narrow viewports start collapsed.
let savedSidebar=null;try{savedSidebar=localStorage.getItem('yako-sidebar-open')}catch(_){}
setSidebar(!matchMedia('(max-width: 850px)').matches && savedSidebar!=='false',{pin:true});
// Icons: local inline SVG sprites, no external requests or icon fonts.
const icons={panel:'<rect x="3" y="4" width="18" height="16" rx="3"/><path d="M9 4v16"/>',menu:'<path d="M4 7h16M4 12h16M4 17h16"/>',insights:'<path d="m12 2 2.6 6.8L21 12l-6.4 3.2L12 22l-2.6-6.8L3 12l6.4-3.2L12 2Z"/>',send:'<path d="m5 12 7-7 7 7M12 5v14"/>',plus:'<path d="M12 5v14M5 12h14"/>',chat:'<path d="M4 5h16v11H8l-4 4V5Z"/>',chart:'<path d="M4 20V4M4 20h16M7 16l4-5 4 2 5-7"/>',settings:'<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/>'};
function svgIcon(name){return `<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${icons[name]}</svg>`}
$('#toggleInsights').innerHTML=svgIcon('insights')+'<span id="evidenceBadge"></span>';
$('#send').innerHTML=svgIcon('send');
$$('.nav').forEach((b,i)=>{const first=b.querySelector('span');if(first)first.innerHTML=svgIcon(['chat','chart','settings'][i]);const labels=['Intelligence','Scenario Lab','Model Center'];b.setAttribute('aria-label',labels[i]);b.title=labels[i];for(const node of [...b.childNodes])if(node.nodeType===Node.TEXT_NODE&&node.textContent.trim()){const label=document.createElement('span');label.className='nav-label';label.textContent=node.textContent.trim();node.replaceWith(label)}});
const newButton=$('#new');newButton.title='New analysis';newButton.setAttribute('aria-label','New analysis');newButton.innerHTML=svgIcon('plus')+'<span class="new-label">New analysis</span><span class="new-shortcut">⌘ K</span>';
const historyLabel=$('.history-label');if(historyLabel)historyLabel.title='Private web history';

// V10.6: avoid viewport displacement when the virtual keyboard opens.
if(window.visualViewport){window.visualViewport.addEventListener('resize',()=>{document.documentElement.style.setProperty('--visible-vh',window.visualViewport.height+'px')},{passive:true});}

// V10.8: ao reduzir para mobile, fechar painéis sem roubar foco do chat.
const mobileLayout=matchMedia('(max-width: 850px)');
mobileLayout.addEventListener?.('change',e=>{if(e.matches){setSidebar(false);setInsight(false)}else{setSidebar(true,{pin:true});setInsight(false)}});
$('#toggleInsights').addEventListener('animationend',e=>{if(e.animationName==='yakoPulse')e.currentTarget.classList.remove('evidence-pulse')});

// Mobile starts with the drawer closed, desktop with it open.
if(matchMedia("(max-width: 850px)").matches) setSidebar(false);

// V10.13: independent layers, clean CSS, scroll starts at y=0.
// A altura real é observada para evitar que a última mensagem fique escondida.
(function(){
 const pane=document.querySelector('#messages');
 const composer=document.querySelector('.main > .composer-area');
 if(!pane||!composer)return;
 let previous=0;
 const sync=()=>{
   const nearBottom=pane.scrollHeight-pane.scrollTop-pane.clientHeight<Math.max(64,previous+30);
   const height=Math.ceil(composer.getBoundingClientRect().height);
   pane.style.setProperty('--composer-clearance',(height+8)+'px');
   if(nearBottom)pane.scrollTop=pane.scrollHeight;
   previous=height;
 };
 if(typeof ResizeObserver!=='undefined')new ResizeObserver(sync).observe(composer);
 window.addEventListener('resize',sync,{passive:true});
 requestAnimationFrame(sync);
})();


// V10.19: fully local interface dictionaries. English is default on first run.
const DICT={
 en:{new:'New analysis',history:'HISTORY',local:'LOCAL',private:'Private workspace',stored:'Data stays on this device',heroTitle:'Ask Yako about your finances.',heroDesc:'Ask a question, analyze cash flow or compare financial scenarios. Processing runs locally.',suggest1:'Investigate a suspicious offer',suggest2:'Check a return promise',placeholder:'Ask about risks, investments or financial scenarios...',modeQ:'QVAC + Evidence',modeR:'Evidence only',hint:'Enter to send · Shift+Enter for a new line',disclaimer:'Educational analysis. Not financial advice. No transactions.',panel:'Analysis panel',signals:'DETECTED SIGNALS',severity:'HIGHEST SEVERITY',findings:'IDENTIFIED EVIDENCE',steps:'PROCESSING STEPS',step1:'Evidence extraction',step2:'QVAC interpretation',step3:'Local report',diagnostic:'DIAGNOSTICS',labDesc:'Mathematical projections calculated by code, not by a language model.',principal:'Initial capital (BRL)',rate:'Monthly rate (%)',months:'Months',contribution:'Monthly contribution (BRL)',calculate:'Calculate projection →',labHint:'Set parameters and calculate.',modelDesc:'Operational transparency, privacy and system limits.',privacy:'PRIVACY',controls:'CONTROLS',localDisclaimer:'Generated locally. Verify conclusions and sources.',historyUnavailable:'History unavailable',historyLoaded:'History loaded · evidence not recalculated',resetTitle:'What would you like to analyze?' ,resetDescription:'Ask a financial question to start a conversation.',waiting:'Waiting for analysis.',working:'Checking evidence and preparing an answer…',openEvidence:'Open Evidence Engine',noSignals:'No specific signals detected in this message. This does not establish safety.',noSignalsShort:'NO SIGNALS',critical:'CRITICAL',high:'HIGH',medium:'MODERATE',review:'REVIEW',evidence:'Evidence',modelUnavailable:'QVAC unavailable. Deterministic analysis:',unfinished:'Analysis ended without confirmation.',error:'Error',status:'Engine'},
 pt:{new:'Nova análise',history:'HISTÓRICO',local:'LOCAL',private:'Área privada',stored:'Dados neste dispositivo',heroTitle:'Pergunte ao Yako sobre suas finanças.',heroDesc:'Faça perguntas, analise seu fluxo de caixa ou compare cenários. O processamento é local.',suggest1:'Investigar oferta suspeita',suggest2:'Verificar promessa de retorno',placeholder:'Pergunte sobre riscos, investimentos ou cenários...',modeQ:'QVAC + Evidências',modeR:'Somente evidências',hint:'Enter para enviar · Shift+Enter para nova linha',disclaimer:'Análise educacional. Não é aconselhamento financeiro nem executa transações.',panel:'Painel de análise',signals:'SINAIS DETECTADOS',severity:'MAIOR SEVERIDADE',findings:'EVIDÊNCIAS IDENTIFICADAS',steps:'ETAPAS DE PROCESSAMENTO',step1:'Extração de evidências',step2:'Interpretação QVAC',step3:'Relatório local',diagnostic:'DIAGNÓSTICO',labDesc:'Projeções matemáticas calculadas por código, não pelo modelo.',principal:'Capital inicial (BRL)',rate:'Taxa mensal (%)',months:'Meses',contribution:'Aporte mensal (BRL)',calculate:'Calcular projeção →',labHint:'Configure os parâmetros e calcule.',modelDesc:'Transparência operacional, privacidade e limites do sistema.',privacy:'PRIVACIDADE',controls:'CONTROLES',localDisclaimer:'Resposta gerada localmente. Verifique conclusões e fontes.',historyUnavailable:'Histórico indisponível',historyLoaded:'Histórico carregado · evidências não recalculadas',resetTitle:'O que você gostaria de analisar?' ,resetDescription:'Digite uma pergunta financeira para começar.',waiting:'Aguardando análise.',working:'Verificando evidências e preparando resposta…',openEvidence:'Abrir Evidence Engine',noSignals:'Nenhum sinal específico detectado. Isso não comprova segurança.',noSignalsShort:'SEM SINAIS',critical:'CRÍTICO',high:'ALTO',medium:'MODERADO',review:'REVISÃO',evidence:'Evidência',modelUnavailable:'QVAC indisponível. Análise determinística:',unfinished:'Análise encerrada sem confirmação.',error:'Erro',status:'Motor'},
 es:{new:'Nuevo análisis',history:'HISTORIAL',local:'LOCAL',private:'Espacio privado',stored:'Datos en este dispositivo',heroTitle:'Claridad para mejores decisiones.',heroDesc:'Investiga riesgos, compara escenarios y examina evidencias sin conexión.',suggest1:'Investigar una oferta sospechosa',suggest2:'Verificar rentabilidad prometida',placeholder:'Pregunta sobre riesgos, inversiones o escenarios...',modeQ:'QVAC + Evidencias',modeR:'Solo evidencias',hint:'Enter para enviar · Shift+Enter nueva línea',disclaimer:'Análisis educativo. No es asesoramiento financiero.',panel:'Panel de análisis',signals:'SEÑALES DETECTADAS',severity:'MÁXIMA GRAVEDAD',findings:'EVIDENCIAS IDENTIFICADAS',steps:'ETAPAS',step1:'Extracción de evidencias',step2:'Interpretación QVAC',step3:'Informe local',diagnostic:'DIAGNÓSTICO',labDesc:'Proyecciones calculadas por código, no por IA.',principal:'Capital inicial (BRL)',rate:'Tasa mensual (%)',months:'Meses',contribution:'Aporte mensual (BRL)',calculate:'Calcular proyección →',labHint:'Configure parámetros y calcule.',modelDesc:'Privacidad y límites operativos.',privacy:'PRIVACIDAD',controls:'CONTROLES',localDisclaimer:'Respuesta local. Verifique resultados y fuentes.',historyUnavailable:'Historial no disponible',historyLoaded:'Historial cargado',resetTitle:'Una nueva investigación comienza aquí.',resetDescription:'Pregunte sobre riesgos o escenarios financieros.',waiting:'Esperando análisis.',working:'Verificando evidencias…',openEvidence:'Abrir panel de evidencias',noSignals:'Sin señales específicas. No demuestra seguridad.',noSignalsShort:'SIN SEÑALES',critical:'CRÍTICO',high:'ALTO',medium:'MODERADO',review:'REVISIÓN',evidence:'Evidencia',modelUnavailable:'QVAC no disponible:',unfinished:'Análisis incompleto.',error:'Error',status:'Motor'},
 fr:{new:'Nouvelle analyse',history:'HISTORIQUE',local:'LOCAL',private:'Espace privé',stored:'Données sur cet appareil',heroTitle:'De la clarté pour mieux décider.',heroDesc:'Analysez les risques, comparez les scénarios et vérifiez les preuves hors ligne.',suggest1:'Analyser une offre suspecte',suggest2:'Vérifier un rendement promis',placeholder:'Posez une question sur les risques ou les investissements...',modeQ:'QVAC + Preuves',modeR:'Preuves uniquement',hint:'Entrée pour envoyer · Maj+Entrée nouvelle ligne',disclaimer:'Analyse éducative, pas un conseil financier.',panel:'Panneau d’analyse',signals:'SIGNAUX DÉTECTÉS',severity:'GRAVITÉ MAXIMALE',findings:'PREUVES IDENTIFIÉES',steps:'ÉTAPES',step1:'Extraction des preuves',step2:'Interprétation QVAC',step3:'Rapport local',diagnostic:'DIAGNOSTIC',labDesc:'Projections calculées par code, pas par le modèle.',principal:'Capital initial (BRL)',rate:'Taux mensuel (%)',months:'Mois',contribution:'Versement mensuel (BRL)',calculate:'Calculer →',labHint:'Définissez les paramètres.',modelDesc:'Confidentialité et limites opérationnelles.',privacy:'CONFIDENTIALITÉ',controls:'CONTRÔLES',localDisclaimer:'Réponse locale. Vérifiez les résultats.',historyUnavailable:'Historique indisponible',historyLoaded:'Historique chargé',resetTitle:'Une nouvelle enquête commence ici.',resetDescription:'Posez une question sur les risques financiers.',waiting:'En attente.',working:'Vérification des preuves…',openEvidence:'Ouvrir les preuves',noSignals:'Aucun signal spécifique. Cela ne prouve pas la sécurité.',noSignalsShort:'AUCUN SIGNAL',critical:'CRITIQUE',high:'ÉLEVÉ',medium:'MODÉRÉ',review:'EXAMEN',evidence:'Preuve',modelUnavailable:'QVAC indisponible :',unfinished:'Analyse incomplète.',error:'Erreur',status:'Moteur'}
};
let language=localStorage.getItem('yako-language')||'en';if(!DICT[language])language='en';
function t(key){return (DICT[language]||DICT.en)[key]||DICT.en[key]||key}
function setText(sel,value){const e=$(sel);if(e)e.textContent=value}
function applyLanguage(){
 document.documentElement.lang=language==='pt'?'pt-BR':language;
 $('#locale').value=language;
 setText('.new-label',t('new'));$('#new').setAttribute('aria-label',t('new'));$('#new').title=t('new');
 setText('.history-label',t('history')+' · '+t('local'));
 setText('.sidebar-foot b',t('private'));setText('.sidebar-foot small',t('stored'));
 setText('#hero h1',t('heroTitle'));setText('#hero p',t('heroDesc'));
 /* YAKO_V1058_PREMIUM_JURY: English demo prompt labels are fixed and match their English scenario payloads. */
 $('#prompt').placeholder=t('placeholder');
 $('#mode option[value="qvac"]').textContent=t('modeQ');$('#mode option[value="rules"]').textContent=t('modeR');
 setText('.hint',t('hint'));setText('.main>.composer-area .disclaimer',t('disclaimer'));
 setText('.insights-head h2',t('panel'));setText('.metric:first-child small',t('signals'));setText('.metric:nth-child(2) small',t('severity'));
 const headings=$$('.insights .section-title');['findings','steps','diagnostic'].forEach((key,i)=>{if(headings[i])headings[i].textContent=t(key)});
 ['stepRules','stepModel','stepFinish'].forEach((id,i)=>{const e=$('#'+id);if(e)e.childNodes.forEach(n=>{if(n.nodeType===3&&n.textContent.trim())n.textContent=' '+t('step'+(i+1))+' '})});
 setText('#labView .page-heading p',t('labDesc'));setText('#modelView .page-heading p',t('modelDesc'));
 ['principal','rate','months','contribution'].forEach((id,i)=>{const e=$('#'+id)?.closest('label');if(e&&e.firstChild)e.firstChild.textContent=[t('principal'),t('rate'),t('months'),t('contribution')][i]});
 setText('#calculate',t('calculate'));if($('#labResult')?.textContent.includes('Configure'))setText('#labResult',t('labHint'));
 const cards=$$('#modelView .model-grid article');
 const cardCopy={
  en:['On-demand local inference. Requires the SDK and a model already stored on the device.','Small language model: may make mistakes. Calculations must be independently verified.','Loopback-only HTTP interface. Server-side account-isolated history; storage encryption depends on deployment.','Analysis only: no wallets, subscriptions, orders or financial transfers.'],
  pt:['Inferência local sob demanda. Requer SDK e modelo já armazenados.','Modelo pequeno: pode cometer erros. Cálculos exigem verificação independente.','Interface HTTP local. O histórico SQLite não é criptografado.','Somente análise: sem carteiras, assinaturas, ordens ou transferências.'],
  es:['Inferencia local bajo demanda. Requiere SDK y modelo descargado.','Modelo pequeño: puede equivocarse. Verifique los cálculos.','Interfaz HTTP local. El historial SQLite no está cifrado.','Solo análisis: sin billeteras, órdenes ni transferencias.'],
  fr:['Inférence locale à la demande. SDK et modèle déjà présents requis.','Petit modèle pouvant se tromper. Vérifiez les calculs.','Interface HTTP locale. Historique SQLite non chiffré.','Analyse uniquement : aucun portefeuille ni transfert.']};
 cards.forEach((card,i)=>{const para=card.querySelector('p');if(para)para.textContent=cardCopy[language][i]});
 const navs=$$('.nav');if(navs[1]){const textNode=[...navs[1].childNodes].find(n=>n.nodeType===3);if(textNode)textNode.textContent=' Scenario Lab'}
 if(navs[2]){const textNode=[...navs[2].childNodes].find(n=>n.nodeType===3);if(textNode)textNode.textContent=' Model Center'}

 $('#toggleInsights').title=t('openEvidence');
}
$('#locale').addEventListener('change',e=>{language=e.target.value;localStorage.setItem('yako-language',language);applyLanguage();});
applyLanguage();


// V10.21 · Fluid composer: measured content height, capped to viewport, accessible and IME-safe.
(()=>{
 const field=document.getElementById('prompt');
 if(!field)return;
 let frame=0;
 function resize(){
   cancelAnimationFrame(frame);
   frame=requestAnimationFrame(()=>{
     const viewport=window.visualViewport?.height||window.innerHeight;
     const max=Math.max(76,Math.min(320,Math.floor(viewport*0.38)));
     field.style.setProperty('--composer-max-height',max+'px');
     field.style.height='auto';
     const target=Math.max(54,Math.min(field.scrollHeight,max));
     field.style.height=target+'px';
     field.style.overflowY=field.scrollHeight>max?'auto':'hidden';
     field.setAttribute('aria-multiline','true');
   });
 }
 window.yakoResizeComposer=resize;
 for(const evt of ['input','change','paste','cut','compositionend'])field.addEventListener(evt,resize);
 window.addEventListener('resize',resize,{passive:true});
 window.visualViewport?.addEventListener('resize',resize,{passive:true});
 resize();
})();

// V10.33 mobile drawer entry point; desktop keeps its single internal rail toggle.
(function(){const b=document.getElementById("mobileMenuToggle"),root=document.querySelector(".app");if(!b||!root)return;const sync=()=>{const opened=!root.classList.contains("sidebar-collapsed");b.setAttribute("aria-expanded",String(opened));b.setAttribute("aria-label",opened?"Fechar menu":"Abrir menu")};b.addEventListener("click",()=>{setSidebar(root.classList.contains("sidebar-collapsed"));sync()});const observer=new MutationObserver(sync);observer.observe(root,{attributes:true,attributeFilter:["class"]});sync()})();

(function(){
 const foot=document.querySelector('.sidebar-foot small');if(foot)foot.textContent='Histórico privado no servidor';
 const tag=document.querySelector('.nav[data-view="chat"] .tag');if(tag)tag.textContent='WEB';
 const out=document.createElement('button');out.type='button';out.textContent='Sair';out.className='yako-web-logout';
 out.addEventListener('click',async()=>{try{const r=await fetch('/qvac-financial/auth/logout/',{method:'POST',credentials:'same-origin',headers:{'X-Yako-Token':yakoDesktopToken()}});if(!r.ok)throw Error('Logout unavailable');location.replace('/qvac-financial/auth/')}catch(e){alert(e.message)}});
 document.querySelector('.sidebar-foot')?.append(out);
})();


/* YAKO_V1039_THINKING_1B — minimal thinking indicator, no external assets */
(function(){
  'use strict';
  if(window.__yakoThinking1039)return;
  window.__yakoThinking1039=true;
  var indicator=null, active=0, lastStarted=0;
  function mount(){
    if(indicator && indicator.isConnected)return indicator;
    var host=document.querySelector('#chatView') || document.querySelector('.chat-view') || document.querySelector('main');
    if(!host)return null;
    indicator=document.createElement('div');
    indicator.className='yako-thinking-v1039';
    indicator.setAttribute('role','status');
    indicator.setAttribute('aria-live','polite');
    indicator.innerHTML='<span class="yako-thinking-v1039-label">Analisando</span><span class="yako-thinking-v1039-track"><span class="yako-thinking-v1039-beam"></span></span>';
    host.prepend(indicator);
    return indicator;
  }
  function update(){
    var el=mount();
    if(el)el.classList.toggle('is-active',active>0);
  }
  function begin(){active++;lastStarted=Date.now();update();}
  function finish(){active=Math.max(0,active-1);update();}
  function isAnalyze(input,init){
    var url=typeof input==='string'?input:(input && input.url)||'';
    var method=(init && init.method)||(input && input.method)||'GET';
    try {return /\/qvac-financial\/api\/analyze(?:\?|$)/.test(String(url)) && String(method).toUpperCase()==='POST';}
    catch(e){return false;}
  }
  var original=window.fetch;
  if(typeof original!=='function')return;
  window.fetch=function(input,init){
    if(!isAnalyze(input,init))return original.apply(this,arguments);
    begin();
    var response;
    try{response=original.apply(this,arguments)}catch(e){finish();throw e;}
    return Promise.resolve(response).then(function(res){
      // We cannot infer completion from headers: streaming continues afterwards.
      // The app's own busy flag controls normal completion; an independent
      // maximum duration avoids an indefinitely stuck indicator.
      var started=Date.now();
      var timer=setInterval(function(){
        var isBusy=true;
        try{isBusy=typeof busy==='undefined'?true:!!busy;}catch(e){}
        if((!isBusy && Date.now()-started>300) || Date.now()-started>180000){
          clearInterval(timer);finish();
        }
      },250);
      if(!res.ok){clearInterval(timer);finish();}
      return res;
    },function(err){finish();throw err;});
  };
})();


/* YAKO_V1040_SHARED_HEADER_ACTIVITY */
function yakoV1040HeaderActivity(active){
  const brand=document.querySelector('.floating-brand');
  if(!brand)return;
  if(!brand.querySelector('.yako-v1040-activity')){
    const track=document.createElement('span');
    track.className='yako-v1040-activity';
    track.setAttribute('aria-hidden','true');
    const beam=document.createElement('span');
    beam.className='yako-v1040-activity-beam';
    track.appendChild(beam);
    brand.appendChild(track);
  }
  brand.classList.toggle('yako-v1040-processing',Boolean(active));
  brand.setAttribute('aria-label',active?'AI Yako — processando':'AI Yako');
}



/* AI Yako V10.50 — coordinated mobile navigation; no backend changes. */
(function yakoV1050Mobile(){
 'use strict';
 const root=document.querySelector('.app');
 const sidebar=document.getElementById('sidebar');
 const insights=document.getElementById('insights');
 const menu=document.getElementById('mobileMenuToggle');
 const evidence=document.getElementById('toggleInsights');
 if(!root||!sidebar||!insights||!menu||!evidence)return;
 const mobile=window.matchMedia('(max-width: 850px)');
 const drawerOpen=()=>!root.classList.contains('sidebar-collapsed');
 const insightsOpen=()=>root.classList.contains('insights-open');
 const closeDrawer=()=>{if(drawerOpen())setSidebar(false,{pin:false})};
 const closeEvidence=()=>{if(insightsOpen())setInsight(false,{pin:false})};
 // Capture phase closes the other panel before existing button handlers toggle this one.
 menu.addEventListener('click',()=>{if(mobile.matches)closeEvidence()},{capture:true});
 evidence.addEventListener('click',()=>{if(mobile.matches)closeDrawer()},{capture:true});
 document.getElementById('railToggle')?.addEventListener('click',()=>{if(mobile.matches)closeEvidence()},{capture:true});
 // A navigation selection (including history) closes the drawer immediately.
 sidebar.addEventListener('click',event=>{
   if(!mobile.matches)return;
   const action=event.target.closest('button,a');
   if(!action||action.id==='railToggle')return;
   closeDrawer();
 });
 // Outside touch/pointer closes panels; no click-through prevention, no delayed timers.
 document.addEventListener('pointerdown',event=>{
   if(!mobile.matches)return;
   const target=event.target;
   if(drawerOpen()&&!sidebar.contains(target)&&!menu.contains(target))closeDrawer();
   if(insightsOpen()&&!insights.contains(target)&&!evidence.contains(target))closeEvidence();
 },{passive:true,capture:true});
 document.addEventListener('keydown',event=>{
   if(event.key==='Escape'){
     closeDrawer();closeEvidence();
     if(mobile.matches&&document.activeElement===menu)menu.blur();
   }
 });
 // Do not persist the mobile drawer state between sessions.
 const sync=()=>{
   if(mobile.matches){
     menu.setAttribute('aria-expanded',String(drawerOpen()));
     evidence.setAttribute('aria-expanded',String(insightsOpen()));
   }
 };
 new MutationObserver(sync).observe(root,{attributes:true,attributeFilter:['class']});
 mobile.addEventListener?.('change',sync);
 sync();
})();

/* YAKO_V1062_PULL_TO_REFRESH */
(() => {
  'use strict';
  if (window.__yakoV1062PullRefresh) return;
  window.__yakoV1062PullRefresh = true;
  const threshold = 84;
  let startY = 0, startX = 0, distance = 0, eligible = false;
  let refreshing = false, label = null, selectedScroller = null;
  const isTouch = ('ontouchstart' in window) || navigator.maxTouchPoints > 0;
  if (!isTouch) return;
  const rootScroller = () => document.scrollingElement || document.documentElement;
  const isScrollable = el => {
    if (!el || el === document.body || el === document.documentElement) return false;
    const css = getComputedStyle(el);
    return /(auto|scroll)/.test(css.overflowY) && el.scrollHeight > el.clientHeight + 3;
  };
  const getScroller = target => {
    for (let el = target; el && el !== document.body; el = el.parentElement) {
      if (isScrollable(el)) return el;
    }
    return rootScroller();
  };
  const top = el => (el ? el.scrollTop : 0) <= 2;
  const excluded = target => target.closest('input,textarea,select,[contenteditable="true"],[role="dialog"],.modal,.chat-messages,.conversation-messages,.messages-list,.chat-scroll,.chat-history');
  function indicator() {
    if (label) return label;
    label = document.createElement('div');
    label.id = 'yako-v1062-pull-indicator';
    label.setAttribute('role','status');
    label.setAttribute('aria-live','polite');
    Object.assign(label.style, {
      position:'fixed',top:'calc(env(safe-area-inset-top, 0px) + 10px)',left:'50%',
      transform:'translate(-50%,-110px)',opacity:'0',transition:'transform .16s ease,opacity .16s ease',
      background:'rgba(16,24,40,.96)',color:'#fff',border:'1px solid rgba(255,255,255,.14)',
      borderRadius:'999px',padding:'11px 19px',font:'600 13px system-ui,sans-serif',
      boxShadow:'0 12px 32px rgba(0,0,0,.23)',pointerEvents:'none',zIndex:'2147483647'
    });
    label.textContent = '↓ Pull to refresh';
    document.body.appendChild(label);
    return label;
  }
  function reset() {
    eligible = false; distance = 0; selectedScroller = null;
    if (label && !refreshing) {
      label.style.transform = 'translate(-50%,-110px)'; label.style.opacity = '0';
    }
  }
  document.addEventListener('touchstart', e => {
    if (refreshing || e.touches.length !== 1 || !(e.target instanceof Element)) {reset();return;}
    if (excluded(e.target)) {reset();return;}
    selectedScroller = getScroller(e.target);
    eligible = top(selectedScroller);
    startY = e.touches[0].clientY;
    startX = e.touches[0].clientX;
    distance = 0;
  }, {passive:true, capture:true});
  document.addEventListener('touchmove', e => {
    if (!eligible || refreshing || e.touches.length !== 1) return;
    const dy = e.touches[0].clientY - startY;
    const dx = Math.abs(e.touches[0].clientX - startX);
    if (dx > 45 || !top(selectedScroller) || dy < -5) {reset();return;}
    if (dy < 9) return;
    distance = dy;
    const el = indicator();
    el.textContent = dy >= threshold ? '↻ Release to refresh' : '↓ Pull to refresh';
    el.style.opacity = '1';
    el.style.transform = `translate(-50%,${Math.min(22, -75 + dy * .9)}px)`;
    if (e.cancelable) e.preventDefault();
  }, {passive:false, capture:true});
  document.addEventListener('touchend', e => {
    if (!eligible || refreshing) {reset();return;}
    const dy = e.changedTouches.length ? e.changedTouches[0].clientY - startY : distance;
    if (dy >= threshold && top(selectedScroller)) {
      refreshing = true;
      const el = indicator(); el.textContent = '↻ Refreshing…';
      el.style.opacity = '1'; el.style.transform = 'translate(-50%,16px)';
      setTimeout(() => window.location.reload(), 180);
    } else reset();
  }, {passive:true, capture:true});
  document.addEventListener('touchcancel', reset, {passive:true, capture:true});
})();


/* YAKO_DOWNLOAD_MODAL_V2 */
(function(){
 'use strict';
 const url='https://pub-2f08c8cef10849eba81e894858738696.r2.dev/AI-YAKO-Linux-x86_64.tar.gz';
 function setup(){
  if(document.getElementById('yako-download-trigger'))return;
  const trigger=document.createElement('button');trigger.id='yako-download-trigger';trigger.type='button';trigger.textContent='↓  Download Apps';trigger.setAttribute('aria-haspopup','dialog');
  const overlay=document.createElement('div');overlay.id='yako-download-overlay';overlay.hidden=true;
  overlay.innerHTML=`<section id="yako-download-dialog" role="dialog" aria-modal="true" aria-labelledby="yako-dl-title">
    <div class="yako-dl-head"><div><h2 id="yako-dl-title">Get AI YAKO</h2><p>Desktop and mobile applications</p></div><button type="button" id="yako-dl-close" aria-label="Close">×</button></div>
    <div class="yako-dl-row"><div><div class="yako-dl-platform">🐧 Linux · x86_64</div><div class="yako-dl-sub">Available · .tar.gz</div></div><a class="yako-dl-action" id="yako-dl-linux" href="${url}" target="_blank" rel="noopener noreferrer">Download</a></div>
    <div class="yako-dl-row"><div><div class="yako-dl-platform">Windows</div><div class="yako-dl-sub">Coming soon</div></div><button class="yako-dl-action" disabled>Unavailable</button></div>
    <div class="yako-dl-row"><div><div class="yako-dl-platform">macOS</div><div class="yako-dl-sub">Coming soon</div></div><button class="yako-dl-action" disabled>Unavailable</button></div>
    <div class="yako-dl-row"><div><div class="yako-dl-platform">Android</div><div class="yako-dl-sub">Coming soon</div></div><button class="yako-dl-action" disabled>Unavailable</button></div>
    <div class="yako-dl-row"><div><div class="yako-dl-platform">iOS</div><div class="yako-dl-sub">Coming soon</div></div><button class="yako-dl-action" disabled>Unavailable</button></div>
    <p id="yako-dl-note">Linux download is available without a request limit.</p></section>`;
  document.body.append(trigger,overlay);
  const close=()=>{overlay.hidden=true;trigger.focus();};
  trigger.addEventListener('click',()=>{overlay.hidden=false;overlay.querySelector('#yako-dl-close').focus();});
  overlay.querySelector('#yako-dl-close').addEventListener('click',close);
  overlay.addEventListener('click',e=>{if(e.target===overlay)close();});
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!overlay.hidden)close();});
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',setup,{once:true});else setup();
})();
