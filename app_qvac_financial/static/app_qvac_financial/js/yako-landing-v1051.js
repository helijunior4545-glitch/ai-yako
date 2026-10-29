(()=>{'use strict';
const root=document.getElementById('yl-root');if(!root)return;
const video=document.getElementById('yl-video'),player=document.getElementById('yl-player');
const play=document.getElementById('yl-play'),toggle=document.getElementById('yl-toggle'),mute=document.getElementById('yl-mute'),full=document.getElementById('yl-fullscreen'),progress=document.getElementById('yl-progress'),time=document.getElementById('yl-time');
const clock=n=>{if(!Number.isFinite(n))return'00:00';return String(Math.floor(n/60)).padStart(2,'0')+':'+String(Math.floor(n%60)).padStart(2,'0')};
if(video){video.volume=.7;video.muted=true;
const sync=()=>{player.classList.toggle('playing',!video.paused);if(toggle)toggle.textContent=video.paused?'Play':'Pause';if(progress)progress.value=video.duration?Math.round(video.currentTime/video.duration*1000):0;if(time)time.textContent=clock(video.currentTime)+' / '+clock(video.duration)};
const act=async()=>{if(video.paused){try{await video.play()}catch(e){console.warn('Video playback unavailable',e)}}else video.pause();sync()};
play?.addEventListener('click',act);toggle?.addEventListener('click',act);
video.addEventListener('click',act);['play','pause','ended','timeupdate','loadedmetadata','durationchange'].forEach(ev=>video.addEventListener(ev,sync));
progress?.addEventListener('input',()=>{if(video.duration)video.currentTime=video.duration*(Number(progress.value)/1000)});
mute?.addEventListener('click',()=>{video.muted=!video.muted;mute.textContent=video.muted?'Sound off':'Sound on'});
full?.addEventListener('click',()=>{if(document.fullscreenElement)document.exitFullscreen?.();else player.requestFullscreen?.()});sync();}
let etag=null;const endpoint=root.dataset.contentUrl;
if(endpoint){const refresh=async()=>{if(document.hidden)return;try{const headers=etag?{'If-None-Match':etag}:{};const r=await fetch(endpoint,{headers,credentials:'same-origin'});if(r.status===304)return;if(!r.ok)return;etag=r.headers.get('ETag');const j=await r.json();if(!j||!j.content)return;const c=j.content;const fields=[['yl-title','hero_title'],['yl-film-title','video_title']];for(const [id,key] of fields){const el=document.getElementById(id);if(el&&typeof c[key]==='string'&&c[key])el.textContent=c[key]}}catch(e){/* preserve last valid content */}};
setInterval(refresh,60000);}
})();
