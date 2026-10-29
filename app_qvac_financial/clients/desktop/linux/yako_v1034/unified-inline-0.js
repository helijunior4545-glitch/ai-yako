/* AI Yako V10.46: shared progress microinteraction; no network calls */
(function(){'use strict';if(window.__yako46)return;window.__yako46=true;
function init(){if(document.getElementById('yako46-activity'))return;
var bar=document.createElement('div');bar.id='yako46-activity';bar.setAttribute('role','progressbar');bar.setAttribute('aria-label','Análise em andamento');bar.setAttribute('aria-valuetext','Processando');bar.hidden=true;document.body.appendChild(bar);
var pending=0,timer=null;
function paint(){var active=pending>0;document.body.classList.toggle('yako46-busy',active);bar.hidden=!active;}
function begin(){pending++;paint();clearTimeout(timer);timer=setTimeout(function(){pending=0;paint()},180000)}
function end(){pending=Math.max(0,pending-1);paint();if(!pending)clearTimeout(timer)}
// Detect only chat form submissions and AI API calls; don't animate unrelated requests.
document.addEventListener('submit',function(e){if(e.target.closest('form')&&e.target.querySelector('textarea')){begin();setTimeout(end,180000)}},true);
var orig=window.fetch;if(typeof orig==='function')window.fetch=function(input,opts){
 var url=typeof input==='string'?input:(input&&input.url)||'';
 var match=/\/((api\/)?(chat|analy[sz]e|message|stream|ask|respond))([/?#]|$)/i.test(url);
 if(!match)return orig.apply(this,arguments);
 begin();var promise;
 try{promise=orig.apply(this,arguments)}catch(err){end();throw err}
 return Promise.resolve(promise).then(function(response){
 // Streaming can continue after headers: track reader completion when possible.
 if(response.body&&/event-stream|ndjson/i.test(response.headers.get('content-type')||'')){
  try{var clone=response.clone();clone.text().then(end,end)}catch(e){end()}
 }else end();return response;
 },function(error){end();throw error});
};
window.addEventListener('pagehide',function(){pending=0;paint()});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
