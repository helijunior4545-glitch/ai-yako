'use strict';
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const token=document.querySelector('meta[name="yako-session"]').content;let conversationId=null,busy=false,controller=null;
async function api(path,data){const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json','X-Yako-Token':token},body:JSON.stringify(data)});const v=await r.json();if(!r.ok)throw Error(v.error||'Erro');return v}
async function get(path){const r=await fetch(path,{headers:{'X-Yako-Token':token}});if(!r.ok)throw Error('Erro de histórico');return r.json()}
function el(tag,cls,text){const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e}
function bubble(role,content=''){const box=el('article','bubble '+(role==='user'?'user':'assistant'));if(role!=='user')box.append(el('div','who','✳ Yako'));const body=el('div','text',content);box.append(body);$('#messages').append(box);$('#messages').scrollTop=$('#messages').scrollHeight;return body}
function steps(which){for(const id of ['stepRules','stepModel','stepFinish']){$('#'+id).classList.remove('active','done');$('#'+id).querySelector('b').textContent='—'}if(which==='rules'){$('#stepRules').classList.add('done');$('#stepRules b').textContent='✓'}if(which==='model'){$('#stepRules').classList.add('done');$('#stepRules b').textContent='✓';$('#stepModel').classList.add('active');$('#stepModel b').textContent='●'}if(which==='done'){$$('.step').forEach(e=>{e.classList.add('done');e.querySelector('b').textContent='✓'})}}
function evidence(report){const items=report.findings||[];$('#evidenceBadge').textContent=items.length?items.length:'';$('#riskCount').textContent=items.length;const severity=items.some(x=>x.severity==='CRITICAL')?t('critical'):items.some(x=>x.severity==='HIGH')?t('high'):items.length?t('medium'):t('noSignalsShort');$('#severity').textContent=severity;$('#riskPill').textContent=items.length?t('review'):t('noSignalsShort');$('#riskPill').classList.toggle('danger',!!items.length);const list=$('#findings');list.replaceChildren();if(!items.length)list.append(el('div','empty-small',t('noSignals')));for(const item of items){const row=el('div','finding '+item.severity.toLowerCase());row.append(el('b','',item.flag),el('small','',`${t('evidence')}: “${item.evidence}” · ${item.severity}`));list.append(row)}}
function setBusy(v){busy=v;$('#send').disabled=v;$('#prompt').disabled=v;$('#send').innerHTML=v?'<span class="loader-ring"></span>':svgIcon('send')}
async function send(){
 if(busy)return;
 const text=$('#prompt').value.trim();if(!text)return;
 $('#prompt').value='';$('#hero')?.remove();bubble('user',text);
 const output=bubble('assistant','');setBusy(true);steps('rules');
 $('#metrics').textContent=t('working');
 let resultText='',finished=false;const mode=$('#mode').value;
 try{
  controller=new AbortController();
  const r=await fetch('/api/analyze',{
   method:'POST',headers:{'Content-Type':'application/json','X-Yako-Token':token},
   body:JSON.stringify({text,mode,conversation_id:conversationId,locale:language}),signal:controller.signal
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
     output.textContent=t('working');
    }else if(msg.type==='status'){
     $('#metrics').textContent=msg.data;
    }else if(msg.type==='token'){
     if(!resultText)output.textContent='';
     resultText+=msg.data;output.textContent=resultText;
     $('#messages').scrollTop=$('#messages').scrollHeight;
    }else if(msg.type==='done'){
     finished=true;steps('done');output.textContent=msg.data.answer||output.textContent; if(msg.data.model_used===false || (msg.data.engine||'').includes('Decimal')){$('#stepModel').classList.remove('done','active');$('#stepModel b').textContent='—';}
     $('#metrics').textContent=`Motor: ${msg.data.engine||'local'}\nTempo total: ${msg.data.total_seconds??'—'} s` + (Object.keys(msg.data.timings||{}).length?'\n'+JSON.stringify(msg.data.timings,null,2):'');
     output.parentElement.append(el('div','meta',t('localDisclaimer')));
    }else if(msg.type==='error'){
     finished=true;steps('done');output.textContent=t('modelUnavailable')+'\n'+msg.data.fallback;
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
async function refreshHistory(){try{const rows=await get('/api/conversations');const container=$('#history');container.replaceChildren();for(const row of rows){const b=el('button',row.id===conversationId?'selected':'',row.title);b.title=row.title;b.addEventListener('click',()=>loadConversation(row.id));container.append(b)}}catch(e){$('#history').textContent=t('historyUnavailable')}}
async function loadConversation(id){if(busy)return;const rows=await get('/api/messages?id='+encodeURIComponent(id));conversationId=id;$('#hero')?.remove();$('#messages').replaceChildren();for(const row of rows)bubble(row.role,row.content);evidence({findings:[]});steps('rules');$('#metrics').textContent=t('historyLoaded');show('chat');refreshHistory()}
function reset(){if(busy)return;conversationId=null;$('#messages').replaceChildren();const h=el('div','hero');h.id='hero';h.append(el('div','hero-orbit','✳'),el('div','eyebrow','FINANCIAL INTELLIGENCE · PRIVATE BY DESIGN'));const title=el('h1');title.textContent=t('resetTitle');h.append(title,el('p','',t('resetDescription')));$('#messages').append(h);evidence({findings:[]});steps('rules');$('#metrics').textContent=t('waiting');show('chat');$('#prompt').focus();refreshHistory()}
function show(name){document.querySelector('.main').classList.toggle('non-chat',name!=='chat');scheduleDrawerClose();for(const n of ['chat','lab','model'])$('#'+n+'View').classList.toggle('hidden',n!==name);$$('.nav').forEach(b=>b.classList.toggle('active',b.dataset.view===name));document.title=({chat:'AI Yako · Intelligence',lab:'AI Yako · Scenario Lab',model:'AI Yako · Model Center'})[name]}
$$('.nav').forEach(b=>b.addEventListener('click',()=>show(b.dataset.view)));$('#new').addEventListener('click',reset);$('#send').addEventListener('click',send);$('#prompt').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send()}});document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();reset()}});$$('[data-prompt]').forEach(b=>b.addEventListener('click',()=>{$('#prompt').value=b.dataset.prompt;send()}));
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
evidence=function(report){originalEvidence(report);const items=Array.isArray(report?.findings)?report.findings:[];const btn=$('#toggleInsights');btn.classList.toggle('has-evidence',items.length>0);btn.classList.toggle('high-evidence',items.some(x=>x.severity==='HIGH'||x.severity==='CRITICAL'));btn.title=items.length?`${items.length} evidência(s) disponível(is)`:t('openEvidence');if(items.length){btn.classList.remove('evidence-pulse');void btn.offsetWidth;btn.classList.add('evidence-pulse')}};
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
   pane.style.setProperty('--composer-clearance',(height+16)+'px');
   if(nearBottom)pane.scrollTop=pane.scrollHeight;
   previous=height;
 };
 if(typeof ResizeObserver!=='undefined')new ResizeObserver(sync).observe(composer);
 window.addEventListener('resize',sync,{passive:true});
 requestAnimationFrame(sync);
})();


// V10.19: fully local interface dictionaries. English is default on first run.
const DICT={
 en:{new:'New analysis',history:'HISTORY',local:'LOCAL',private:'Private workspace',stored:'Data stays on this device',heroTitle:'Clarity for smarter decisions.',heroDesc:'Investigate risks, compare scenarios and inspect evidence. Your analysis runs locally.',suggest1:'Investigate a suspicious offer',suggest2:'Check a return promise',placeholder:'Ask about risks, investments or financial scenarios...',modeQ:'QVAC + Evidence',modeR:'Evidence only',hint:'Enter to send · Shift+Enter for a new line',disclaimer:'Educational analysis. Not financial advice. No transactions.',panel:'Analysis panel',signals:'DETECTED SIGNALS',severity:'HIGHEST SEVERITY',findings:'IDENTIFIED EVIDENCE',steps:'PROCESSING STEPS',step1:'Evidence extraction',step2:'QVAC interpretation',step3:'Local report',diagnostic:'DIAGNOSTICS',labDesc:'Mathematical projections calculated by code, not by a language model.',principal:'Initial capital (BRL)',rate:'Monthly rate (%)',months:'Months',contribution:'Monthly contribution (BRL)',calculate:'Calculate projection →',labHint:'Set parameters and calculate.',modelDesc:'Operational transparency, privacy and system limits.',privacy:'PRIVACY',controls:'CONTROLS',localDisclaimer:'Generated locally. Verify conclusions and sources.',historyUnavailable:'History unavailable',historyLoaded:'History loaded · evidence not recalculated',resetTitle:'A new investigation begins here.',resetDescription:'Ask about risks or financial scenarios.',waiting:'Waiting for analysis.',working:'Checking evidence and preparing an answer…',openEvidence:'Open Evidence Engine',noSignals:'No specific signals detected in this message. This does not establish safety.',noSignalsShort:'NO SIGNALS',critical:'CRITICAL',high:'HIGH',medium:'MODERATE',review:'REVIEW',evidence:'Evidence',modelUnavailable:'QVAC unavailable. Deterministic analysis:',unfinished:'Analysis ended without confirmation.',error:'Error',status:'Engine'},
 pt:{new:'Nova análise',history:'HISTÓRICO',local:'LOCAL',private:'Área privada',stored:'Dados neste dispositivo',heroTitle:'Clareza para decisões mais inteligentes.',heroDesc:'Investigue riscos, compare cenários e examine evidências. A análise funciona localmente.',suggest1:'Investigar oferta suspeita',suggest2:'Verificar promessa de retorno',placeholder:'Pergunte sobre riscos, investimentos ou cenários...',modeQ:'QVAC + Evidências',modeR:'Somente evidências',hint:'Enter para enviar · Shift+Enter para nova linha',disclaimer:'Análise educacional. Não é aconselhamento financeiro nem executa transações.',panel:'Painel de análise',signals:'SINAIS DETECTADOS',severity:'MAIOR SEVERIDADE',findings:'EVIDÊNCIAS IDENTIFICADAS',steps:'ETAPAS DE PROCESSAMENTO',step1:'Extração de evidências',step2:'Interpretação QVAC',step3:'Relatório local',diagnostic:'DIAGNÓSTICO',labDesc:'Projeções matemáticas calculadas por código, não pelo modelo.',principal:'Capital inicial (BRL)',rate:'Taxa mensal (%)',months:'Meses',contribution:'Aporte mensal (BRL)',calculate:'Calcular projeção →',labHint:'Configure os parâmetros e calcule.',modelDesc:'Transparência operacional, privacidade e limites do sistema.',privacy:'PRIVACIDADE',controls:'CONTROLES',localDisclaimer:'Resposta gerada localmente. Verifique conclusões e fontes.',historyUnavailable:'Histórico indisponível',historyLoaded:'Histórico carregado · evidências não recalculadas',resetTitle:'Uma nova investigação começa aqui.',resetDescription:'Pergunte sobre riscos ou cenários financeiros.',waiting:'Aguardando análise.',working:'Verificando evidências e preparando resposta…',openEvidence:'Abrir Evidence Engine',noSignals:'Nenhum sinal específico detectado. Isso não comprova segurança.',noSignalsShort:'SEM SINAIS',critical:'CRÍTICO',high:'ALTO',medium:'MODERADO',review:'REVISÃO',evidence:'Evidência',modelUnavailable:'QVAC indisponível. Análise determinística:',unfinished:'Análise encerrada sem confirmação.',error:'Erro',status:'Motor'},
 es:{new:'Nuevo análisis',history:'HISTORIAL',local:'LOCAL',private:'Espacio privado',stored:'Datos en este dispositivo',heroTitle:'Claridad para mejores decisiones.',heroDesc:'Investiga riesgos, compara escenarios y examina evidencias sin conexión.',suggest1:'Investigar una oferta sospechosa',suggest2:'Verificar rentabilidad prometida',placeholder:'Pregunta sobre riesgos, inversiones o escenarios...',modeQ:'QVAC + Evidencias',modeR:'Solo evidencias',hint:'Enter para enviar · Shift+Enter nueva línea',disclaimer:'Análisis educativo. No es asesoramiento financiero.',panel:'Panel de análisis',signals:'SEÑALES DETECTADAS',severity:'MÁXIMA GRAVEDAD',findings:'EVIDENCIAS IDENTIFICADAS',steps:'ETAPAS',step1:'Extracción de evidencias',step2:'Interpretación QVAC',step3:'Informe local',diagnostic:'DIAGNÓSTICO',labDesc:'Proyecciones calculadas por código, no por IA.',principal:'Capital inicial (BRL)',rate:'Tasa mensual (%)',months:'Meses',contribution:'Aporte mensual (BRL)',calculate:'Calcular proyección →',labHint:'Configure parámetros y calcule.',modelDesc:'Privacidad y límites operativos.',privacy:'PRIVACIDAD',controls:'CONTROLES',localDisclaimer:'Respuesta local. Verifique resultados y fuentes.',historyUnavailable:'Historial no disponible',historyLoaded:'Historial cargado',resetTitle:'Una nueva investigación comienza aquí.',resetDescription:'Pregunte sobre riesgos o escenarios financieros.',waiting:'Esperando análisis.',working:'Verificando evidencias…',openEvidence:'Abrir panel de evidencias',noSignals:'Sin señales específicas. No demuestra seguridad.',noSignalsShort:'SIN SEÑALES',critical:'CRÍTICO',high:'ALTO',medium:'MODERADO',review:'REVISIÓN',evidence:'Evidencia',modelUnavailable:'QVAC no disponible:',unfinished:'Análisis incompleto.',error:'Error',status:'Motor'},
 fr:{new:'Nouvelle analyse',history:'HISTORIQUE',local:'LOCAL',private:'Espace privé',stored:'Données sur cet appareil',heroTitle:'De la clarté pour mieux décider.',heroDesc:'Analysez les risques, comparez les scénarios et vérifiez les preuves hors ligne.',suggest1:'Analyser une offre suspecte',suggest2:'Vérifier un rendement promis',placeholder:'Posez une question sur les risques ou les investissements...',modeQ:'QVAC + Preuves',modeR:'Preuves uniquement',hint:'Entrée pour envoyer · Maj+Entrée nouvelle ligne',disclaimer:'Analyse éducative, pas un conseil financier.',panel:'Panneau d’analyse',signals:'SIGNAUX DÉTECTÉS',severity:'GRAVITÉ MAXIMALE',findings:'PREUVES IDENTIFIÉES',steps:'ÉTAPES',step1:'Extraction des preuves',step2:'Interprétation QVAC',step3:'Rapport local',diagnostic:'DIAGNOSTIC',labDesc:'Projections calculées par code, pas par le modèle.',principal:'Capital initial (BRL)',rate:'Taux mensuel (%)',months:'Mois',contribution:'Versement mensuel (BRL)',calculate:'Calculer →',labHint:'Définissez les paramètres.',modelDesc:'Confidentialité et limites opérationnelles.',privacy:'CONFIDENTIALITÉ',controls:'CONTRÔLES',localDisclaimer:'Réponse locale. Vérifiez les résultats.',historyUnavailable:'Historique indisponible',historyLoaded:'Historique chargé',resetTitle:'Une nouvelle enquête commence ici.',resetDescription:'Posez une question sur les risques financiers.',waiting:'En attente.',working:'Vérification des preuves…',openEvidence:'Ouvrir les preuves',noSignals:'Aucun signal spécifique. Cela ne prouve pas la sécurité.',noSignalsShort:'AUCUN SIGNAL',critical:'CRITIQUE',high:'ÉLEVÉ',medium:'MODÉRÉ',review:'EXAMEN',evidence:'Preuve',modelUnavailable:'QVAC indisponible :',unfinished:'Analyse incomplète.',error:'Erreur',status:'Moteur'}
};
let language=localStorage.getItem('yako-language')||'en';if(!DICT[language])language='en';
function t(key){return (DICT[language]||DICT.en)[key]||DICT.en[key]||key}
function setText(sel,value){const e=$(sel);if(e)e.textContent=value}
function applyLanguage(){
 document.documentElement.lang=language==='pt'?'pt-BR':language;
 $('#locale').value=language;
 setText('#new',t('new')+'  +');
 setText('.history-label',t('history')+' · '+t('local'));
 setText('.sidebar-foot b',t('private'));setText('.sidebar-foot small',t('stored'));
 setText('#hero h1',t('heroTitle'));setText('#hero p',t('heroDesc'));
 const sug=$$('[data-prompt]');if(sug[0])sug[0].textContent=t('suggest1');if(sug[1])sug[1].textContent=t('suggest2');
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
  en:['On-demand local inference. Requires the SDK and a model already stored on the device.','Small language model: may make mistakes. Calculations must be independently verified.','Loopback-only HTTP interface. Local SQLite history is not encrypted.','Analysis only: no wallets, subscriptions, orders or financial transfers.'],
  pt:['Inferência local sob demanda. Requer SDK e modelo já armazenados.','Modelo pequeno: pode cometer erros. Cálculos exigem verificação independente.','Interface HTTP local. O histórico SQLite não é criptografado.','Somente análise: sem carteiras, assinaturas, ordens ou transferências.'],
  es:['Inferencia local bajo demanda. Requiere SDK y modelo descargado.','Modelo pequeño: puede equivocarse. Verifique los cálculos.','Interfaz HTTP local. El historial SQLite no está cifrado.','Solo análisis: sin billeteras, órdenes ni transferencias.'],
  fr:['Inférence locale à la demande. SDK et modèle déjà présents requis.','Petit modèle pouvant se tromper. Vérifiez les calculs.','Interface HTTP locale. Historique SQLite non chiffré.','Analyse uniquement : aucun portefeuille ni transfert.']};
 cards.forEach((card,i)=>{const para=card.querySelector('p');if(para)para.textContent=cardCopy[language][i]});
 const navs=$$('.nav');if(navs[1]){const textNode=[...navs[1].childNodes].find(n=>n.nodeType===3);if(textNode)textNode.textContent=' Scenario Lab'}
 if(navs[2]){const textNode=[...navs[2].childNodes].find(n=>n.nodeType===3);if(textNode)textNode.textContent=' Model Center'}

 $('#toggleSidebar').title=t('new');$('#toggleInsights').title=t('openEvidence');
}
$('#locale').addEventListener('change',e=>{language=e.target.value;localStorage.setItem('yako-language',language);applyLanguage();});
applyLanguage();

