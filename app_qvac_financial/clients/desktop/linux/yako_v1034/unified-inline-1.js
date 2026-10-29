
/* YAKO_V1058_PREMIUM_JURY */
(function(){
 const target=document.getElementById('yako-jury-intro');if(!target)return;
 const message='YOUR FINANCIAL INTELLIGENCE IS READY';
 if(window.matchMedia('(prefers-reduced-motion: reduce)').matches){target.textContent=message;return}
 let n=0;const timer=window.setInterval(()=>{if(!target.isConnected){clearInterval(timer);return}target.textContent=message.slice(0,++n);if(n>=message.length)clearInterval(timer)},42);
})();
