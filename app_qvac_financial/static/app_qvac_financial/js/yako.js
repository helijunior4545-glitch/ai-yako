(() => { 'use strict';
  const tabs=[...document.querySelectorAll('[data-panel]')];
  const views=[...document.querySelectorAll('.panel-view')];
  tabs.forEach(tab=>tab.addEventListener('click',()=>{
    const key=tab.dataset.panel;
    tabs.forEach(item=>item.classList.toggle('active',item===tab));
    views.forEach(view=>view.classList.toggle('active',view.id==='panel-'+key));
  }));
  const list=document.getElementById('capability-list');
  if(!list)return;
  fetch('../capabilities/',{credentials:'omit',cache:'no-store'}).then(r=>{
    if(!r.ok)throw new Error('Unavailable');return r.json();
  }).then(data=>{
    const labels=[['qvac_inference','QVAC inference'],['wdk_signing','WDK signing'],['device_pairing','Device pairing'],['sync','Secure sync']];
    list.replaceChildren();
    labels.forEach(([key,label])=>{
      const row=document.createElement('div');row.className='capability-row';
      const name=document.createElement('span');name.textContent=label;
      const status=document.createElement('span');status.textContent=data[key]===true?'Available':'Not connected';
      row.append(name,status);list.append(row);
    });
  }).catch(()=>{list.textContent='Capability status unavailable. No operations are enabled.';});
})();
