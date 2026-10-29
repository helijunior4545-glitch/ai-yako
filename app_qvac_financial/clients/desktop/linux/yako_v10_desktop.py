"""AI Yako V10 — local financial workstation (Tkinter, standard library)."""
import asyncio, json, queue, sqlite3, threading, tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from datetime import datetime
from yako_v10_core import analyze, simulate, rule_explanation
from yako_v10_qvac import infer

BG='#0b101b'; PANEL='#151e2e'; CARD='#1c2940'; WHITE='#edf3ff'; MUTED='#9caec8'; ACCENT='#5ce0c2'; WARNING='#f2ba75'
DB=Path.home()/'.local/share/ai-yako-v10/history.sqlite3'

class App:
    def __init__(self, root):
        self.root=root; root.title('AI Yako V10 | Financial Intelligence Workstation'); root.geometry('1280x830'); root.minsize(940,650); root.configure(bg=BG)
        self.events=queue.Queue(); self.busy=False; self.last=None; self.current='Overview'
        self.mode=tk.StringVar(value='QVAC + Regras'); self.status=tk.StringVar(value='PRONTO  ·  Processamento local')
        self.setup_style(); self.build(); root.after(80,self.poll); root.protocol('WM_DELETE_WINDOW',self.close)
    def setup_style(self):
        st=ttk.Style(); st.theme_use('clam')
        st.configure('Y.TFrame',background=BG); st.configure('Panel.TFrame',background=PANEL)
        st.configure('Y.TButton',background=CARD,foreground=WHITE,padding=(14,11),borderwidth=0,font=('DejaVu Sans',10))
        st.map('Y.TButton',background=[('active','#2b4262')]); st.configure('Y.TCombobox',fieldbackground=CARD,background=CARD,foreground=WHITE)
    def label(self,parent,text,size=11,color=WHITE,bold=False,**kw):
        return tk.Label(parent,text=text,bg=parent.cget('bg'),fg=color,font=('DejaVu Sans',size,'bold' if bold else 'normal'),**kw)
    def build(self):
        shell=tk.Frame(self.root,bg=BG); shell.pack(fill='both',expand=True)
        side=tk.Frame(shell,bg=PANEL,width=228); side.pack(side='left',fill='y'); side.pack_propagate(False)
        self.label(side,'◈  AI YAKO',20,ACCENT,True).pack(anchor='w',padx=22,pady=(29,5))
        self.label(side,'FINANCIAL INTELLIGENCE',8,MUTED).pack(anchor='w',padx=23,pady=(0,38))
        self.nav={}
        for title in ['Overview','AI Intelligence','Risk Analysis','Scenario Lab','History','Model Center']:
            btn=tk.Button(side,text='  '+title,anchor='w',bg=PANEL,fg=MUTED,activebackground=CARD,activeforeground=WHITE,relief='flat',bd=0,font=('DejaVu Sans',11),padx=15,pady=13,command=lambda t=title:self.navigate(t))
            btn.pack(fill='x',padx=12,pady=2); self.nav[title]=btn
        self.label(side,'LOCAL-FIRST  •  V10',9,MUTED).pack(side='bottom',anchor='w',padx=23,pady=25)
        right=tk.Frame(shell,bg=BG); right.pack(side='left',fill='both',expand=True)
        header=tk.Frame(right,bg=BG); header.pack(fill='x',padx=32,pady=(26,15))
        self.heading=self.label(header,'Overview',24,WHITE,True); self.heading.pack(side='left')
        self.label(header,'●  OFFLINE-CAPABLE',10,ACCENT,True).pack(side='right')
        self.content=tk.Frame(right,bg=BG); self.content.pack(fill='both',expand=True,padx=32,pady=(0,14))
        bottom=tk.Frame(right,bg=PANEL,height=39); bottom.pack(fill='x',side='bottom'); self.label(bottom,'  QVAC local  ·  Sem carteira conectada  ·  Sem execução financeira',9,MUTED).pack(side='left',padx=16,pady=11)
        self.label(bottom,'Privacidade por padrão',9,ACCENT).pack(side='right',padx=18)
        self.navigate('Overview')
    def clear(self):
        for widget in self.content.winfo_children():widget.destroy()
    def card(self,parent):
        f=tk.Frame(parent,bg=PANEL,highlightbackground='#263650',highlightthickness=1); return f
    def navigate(self,page):
        if self.busy and page!='AI Intelligence': return
        self.current=page; self.heading.configure(text=page)
        for name,b in self.nav.items(): b.configure(bg=CARD if name==page else PANEL,fg=WHITE if name==page else MUTED)
        self.clear()
        getattr(self,'page_'+page.lower().replace(' ','_'))()
    def page_overview(self):
        self.label(self.content,'Sua central privada de inteligência financeira.',15,MUTED).pack(anchor='w',pady=(2,22))
        row=tk.Frame(self.content,bg=BG); row.pack(fill='x')
        for title,value,sub in [('EXECUÇÃO','100% LOCAL','Sem chamadas cloud pelo motor de regras'),('MOTOR','QVAC SDK','Llama 3.2 1B sob demanda'),('SEGURANÇA','READ ONLY','Sem transferências ou assinaturas')]:
            c=self.card(row); c.pack(side='left',fill='both',expand=True,padx=(0,12)); self.label(c,title,10,MUTED,True).pack(anchor='w',padx=19,pady=(18,9)); self.label(c,value,20,ACCENT,True).pack(anchor='w',padx=19); self.label(c,sub,9,MUTED).pack(anchor='w',padx=19,pady=(8,19))
        c=self.card(self.content); c.pack(fill='x',pady=24); self.label(c,'COMECE POR UMA ANÁLISE',15,WHITE,True).pack(anchor='w',padx=24,pady=(24,8))
        self.label(c,'Investigue promessas financeiras, compare cenários e registre evidências locais.',11,MUTED).pack(anchor='w',padx=24,pady=(0,19))
        ttk.Button(c,text='Abrir AI Intelligence  →',style='Y.TButton',command=lambda:self.navigate('AI Intelligence')).pack(anchor='w',padx=24,pady=(0,25))
    def page_ai_intelligence(self):
        self.label(self.content,'Análise híbrida: regras auditáveis + linguagem natural QVAC.',11,MUTED).pack(anchor='w',pady=(0,12))
        c=self.card(self.content); c.pack(fill='both',expand=True)
        self.label(c,'CENÁRIO FINANCEIRO',10,MUTED,True).pack(anchor='w',padx=20,pady=(18,7))
        self.scenario=tk.Text(c,height=4,bg=CARD,fg=WHITE,insertbackground=WHITE,relief='flat',wrap='word',font=('DejaVu Sans',11),padx=13,pady=12)
        self.scenario.pack(fill='x',padx=20); self.scenario.insert('1.0','Uma plataforma promete retorno garantido de 25% ao mês. Quais são os riscos?')
        bar=tk.Frame(c,bg=PANEL); bar.pack(fill='x',padx=20,pady=12)
        ttk.Combobox(bar,textvariable=self.mode,values=('QVAC + Regras','Somente regras'),state='readonly',width=19).pack(side='left')
        self.run_btn=ttk.Button(bar,text='Analisar cenário  →',style='Y.TButton',command=self.start); self.run_btn.pack(side='left',padx=12)
        ttk.Button(bar,text='Exportar JSON',style='Y.TButton',command=self.export).pack(side='left')
        self.label(c,'RESULTADO & EVIDÊNCIAS',10,MUTED,True).pack(anchor='w',padx=20,pady=(12,7))
        area=tk.Frame(c,bg=PANEL); area.pack(fill='both',expand=True,padx=20,pady=(0,12))
        self.output=tk.Text(area,bg=CARD,fg=WHITE,insertbackground=WHITE,relief='flat',wrap='word',font=('DejaVu Sans',10),padx=15,pady=14,state='disabled')
        self.output.pack(side='left',fill='both',expand=True)
        scroll=tk.Scrollbar(area,command=self.output.yview); scroll.pack(side='right',fill='y'); self.output.configure(yscrollcommand=scroll.set)
        self.label(c,'O texto da IA pode conter erros. Evidências de regras não comprovam fraude.',9,MUTED).pack(anchor='w',padx=20,pady=(0,10))
        self.label(c,'STATUS',9,MUTED,True).pack(anchor='w',padx=20)
        self.label(c,'Pronto para analisar',10,ACCENT).pack(anchor='w',padx=20,pady=(0,12)); self.status_widget=c.winfo_children()[-1]
    def write(self,text,replace=False):
        if self.current!='AI Intelligence':return
        self.output.configure(state='normal')
        if replace:self.output.delete('1.0','end')
        self.output.insert('end',text); self.output.see('end'); self.output.configure(state='disabled')
    def start(self):
        if self.busy:return
        text=self.scenario.get('1.0','end').strip()
        try: report=analyze(text)
        except ValueError as exc:messagebox.showerror('Entrada inválida',str(exc));return
        self.last={'rules':report,'qvac':None}; self.write('ANÁLISE DETERMINÍSTICA\n'+rule_explanation(report)+'\n\n',True)
        if self.mode.get()=='Somente regras':self.status_widget.configure(text='Análise concluída · Somente regras'); self.save();return
        self.busy=True; self.run_btn.configure(state='disabled'); self.write('RESPOSTA QVAC\n'); self.status_widget.configure(text='Inicializando…')
        def task():
            try:self.events.put(('done',asyncio.run(infer(report,lambda k,v:self.events.put((k,v))))))
            except Exception as exc:self.events.put(('error',f'{type(exc).__name__}: {exc}'))
        threading.Thread(target=task,daemon=True).start()
    def poll(self):
        for _ in range(100):
            try:kind,value=self.events.get_nowait()
            except queue.Empty:break
            if kind=='status' and self.current=='AI Intelligence':self.status_widget.configure(text=value)
            elif kind=='token':self.write(value)
            elif kind=='done':
                self.last['qvac']=value; self.write('\n\nTEMPO TOTAL: '+str(value['total_seconds'])+' s\n');self.write('MÉTRICAS: '+json.dumps(value['timings'],ensure_ascii=False)+'\n')
                self.busy=False; self.save()
                if self.current=='AI Intelligence':self.run_btn.configure(state='normal');self.status_widget.configure(text='Concluído · QVAC local')
            elif kind=='error':
                self.last['qvac_error']=value; self.write('\n\nFalha QVAC: '+value+'\nAs regras permanecem disponíveis.\n');self.busy=False;self.save()
                if self.current=='AI Intelligence':self.run_btn.configure(state='normal');self.status_widget.configure(text='Falha no modelo · Regras preservadas')
        self.root.after(80,self.poll)
    def save(self):
        if not self.last:return
        try:
            DB.parent.mkdir(parents=True,exist_ok=True); db=sqlite3.connect(DB)
            db.execute('CREATE TABLE IF NOT EXISTS analyses (id INTEGER PRIMARY KEY, created TEXT NOT NULL, scenario TEXT NOT NULL, report TEXT NOT NULL)')
            db.execute('INSERT INTO analyses(created,scenario,report) VALUES(?,?,?)',(datetime.now().isoformat(timespec='seconds'),self.last['rules']['scenario'],json.dumps(self.last,ensure_ascii=False)))
            db.commit();db.close()
        except Exception:pass
    def export(self):
        if not self.last:messagebox.showinfo('Sem relatório','Execute uma análise primeiro.');return
        path=filedialog.asksaveasfilename(defaultextension='.json',filetypes=[('JSON','*.json')])
        if not path:return
        dest=Path(path)
        if dest.exists():messagebox.showerror('Arquivo existente','Para preservar evidências, escolha um nome novo.');return
        try:
            with dest.open('x',encoding='utf-8') as f:json.dump(self.last,f,ensure_ascii=False,indent=2)
            dest.chmod(0o600)
        except OSError as exc:messagebox.showerror('Erro',str(exc))
    def page_risk_analysis(self):
        self.label(self.content,'Motor de evidências · Sem inferências não verificadas.',11,MUTED).pack(anchor='w',pady=(0,16))
        c=self.card(self.content);c.pack(fill='both',expand=True)
        self.label(c,'TEXTO PARA AVALIAÇÃO',10,MUTED,True).pack(anchor='w',padx=20,pady=(20,10))
        inp=tk.Text(c,height=6,bg=CARD,fg=WHITE,insertbackground=WHITE,relief='flat',padx=12,pady=10,wrap='word');inp.pack(fill='x',padx=20)
        inp.insert('1.0','Oferta urgente com retorno garantido de 30% ao mês.')
        out=tk.Text(c,bg=CARD,fg=WHITE,relief='flat',padx=14,pady=12,wrap='word');out.pack(fill='both',expand=True,padx=20,pady=(14,20))
        def run():
            try:r=analyze(inp.get('1.0','end'));result=rule_explanation(r)
            except ValueError as exc:result=str(exc)
            out.delete('1.0','end');out.insert('1.0',result)
        ttk.Button(c,text='Executar análise de risco',style='Y.TButton',command=run).pack(anchor='w',padx=20,pady=(0,15))
    def page_scenario_lab(self):
        self.label(self.content,'Projeções matemáticas locais · Não representam previsões.',11,MUTED).pack(anchor='w',pady=(0,16))
        c=self.card(self.content);c.pack(fill='both',expand=True)
        row=tk.Frame(c,bg=PANEL);row.pack(fill='x',padx=22,pady=20)
        fields={}
        for title,default in [('Capital inicial','10000'),('Taxa mensal (%)','1'),('Meses','60'),('Aporte mensal','0')]:
            block=tk.Frame(row,bg=PANEL);block.pack(side='left',fill='x',expand=True,padx=(0,12));self.label(block,title,10,MUTED).pack(anchor='w',pady=(0,7))
            e=tk.Entry(block,bg=CARD,fg=WHITE,insertbackground=WHITE,relief='flat',font=('DejaVu Sans',12));e.insert(0,default);e.pack(fill='x',ipady=10);fields[title]=e
        result=self.label(c,'Configure os parâmetros e calcule.',12,ACCENT,True);result.pack(anchor='w',padx=24,pady=(0,12))
        chart=tk.Canvas(c,bg=CARD,highlightthickness=0,height=310);chart.pack(fill='both',expand=True,padx=22,pady=(0,22))
        def run():
            try:r=simulate(fields['Capital inicial'].get(),fields['Taxa mensal (%)'].get(),fields['Meses'].get(),fields['Aporte mensal'].get())
            except Exception as exc:messagebox.showerror('Parâmetros inválidos',str(exc));return
            result.configure(text=f"Saldo hipotético: R$ {r['final_balance']:,.2f}   ·   Aportado: R$ {r['total_contributed']:,.2f}")
            chart.delete('all');chart.update_idletasks();w=max(chart.winfo_width(),300);h=max(chart.winfo_height(),200);pts=r['points'];lo=min(x['balance'] for x in pts);hi=max(x['balance'] for x in pts);span=max(hi-lo,1)
            coords=[]
            for i,p in enumerate(pts):coords.extend((25+i*(w-50)/(len(pts)-1),h-30-(p['balance']-lo)*(h-65)/span))
            chart.create_line(*coords,fill=ACCENT,width=3,smooth=True);chart.create_text(20,15,text='EVOLUÇÃO DO SALDO',fill=MUTED,anchor='w',font=('DejaVu Sans',10))
            chart.create_text(w-18,h-13,text=r['note'],fill=MUTED,anchor='e',font=('DejaVu Sans',8))
        ttk.Button(c,text='Calcular projeção  →',style='Y.TButton',command=run).pack(anchor='w',padx=22,pady=(0,20));run()
    def page_history(self):
        self.label(self.content,'Histórico privado armazenado neste computador.',11,MUTED).pack(anchor='w',pady=(0,14))
        c=self.card(self.content);c.pack(fill='both',expand=True)
        area=tk.Text(c,bg=PANEL,fg=WHITE,relief='flat',font=('DejaVu Sans',11),padx=20,pady=20,wrap='word');area.pack(fill='both',expand=True)
        if DB.exists():
            try:
                db=sqlite3.connect(DB); rows=db.execute('SELECT created,scenario FROM analyses ORDER BY id DESC LIMIT 60').fetchall();db.close()
                for date,scenario in rows:area.insert('end',f'{date}\n{scenario[:280]}\n'+'─'*55+'\n\n')
            except sqlite3.Error as exc:area.insert('end','Histórico indisponível: '+str(exc))
        else:area.insert('end','Nenhuma análise salva ainda.')
        area.configure(state='disabled')
    def page_model_center(self):
        self.label(self.content,'Diagnóstico do runtime local.',11,MUTED).pack(anchor='w',pady=(0,16))
        c=self.card(self.content);c.pack(fill='x')
        for title,value in [('PROVEDOR','Tether QVAC SDK (Python)'),('MODELO','Llama 3.2 1B Instruct Q4_0'),('EXECUÇÃO','Sob demanda; liberado ao fim da análise'),('REDE','Teste offline depende de desconexão real do sistema'),('TRANSAÇÕES','Desabilitadas'),('HARDWARE','CPU; aceleração depende do runtime disponível')]:
            row=tk.Frame(c,bg=PANEL);row.pack(fill='x',padx=22,pady=12)
            self.label(row,title,10,MUTED,True).pack(side='left');self.label(row,value,11,WHITE).pack(side='right')
    def close(self):
        if self.busy and not messagebox.askyesno('Inferência em andamento','Fechar a janela não garante interrupção imediata do worker. Fechar mesmo assim?'):return
        self.root.destroy()

def main():
    root=tk.Tk();App(root);root.mainloop()
if __name__=='__main__':main()
