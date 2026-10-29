
/* Scoped controls; no interference with financial workspace */
(function(){
  function setup(){
    const root=document.getElementById('demonstracao');
    if(!root)return;
    const video=root.querySelector('#yk-video');
    const play=root.querySelector('[data-yk64-play]');
    const sound=root.querySelector('[data-yk64-sound]');
    if(!video||!play||!sound)return;
    const reduce=window.matchMedia('(prefers-reduced-motion: reduce)');
    function sync(){
      root.classList.toggle('yk64-playing',!video.paused);
      play.textContent=video.paused?'▶ Reproduzir':'Ⅱ Pausar';
      play.setAttribute('aria-label',video.paused?'Reproduzir vídeo':'Pausar vídeo');
      sound.textContent=video.muted?'♫ Ativar som':'♫ Silenciar';
      sound.setAttribute('aria-label',video.muted?'Ativar som':'Silenciar vídeo');
      sound.setAttribute('aria-pressed',String(!video.muted));
    }
    play.addEventListener('click',async()=>{
      if(video.paused){try{await video.play()}catch(e){}}
      else video.pause();
      sync();
    });
    sound.addEventListener('click',()=>{
      video.muted=!video.muted;
      if(!video.muted)video.volume=0.65;
      sync();
    });
    for(const event of ['play','pause','volumechange','ended'])video.addEventListener(event,sync);
    video.muted=true;
    video.defaultMuted=true;
    if(!reduce.matches)video.play().catch(()=>{});
    else video.pause();
    if(reduce.addEventListener)reduce.addEventListener('change',e=>{if(e.matches)video.pause();sync();});
    sync();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',setup);
  else setup();
})();
