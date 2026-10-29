"""AI Yako V10.1 — refined local-first desktop workstation. No network UI services."""
import asyncio
import json
import queue
import sqlite3
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from datetime import datetime
from yako_v10_core import analyze, simulate, rule_explanation
from yako_v10_qvac import infer

BG='#090f1b'; SIDE='#101a2a'; SURFACE='#141f31'; INNER='#1b2940'; BORDER='#2a3950'
TEXT='#edf4ff'; MUTED='#94a9c5'; AQUA='#65e6d0'; GOLD='#f3c27c'; RED='#ff8c91'; BLUE='#8bb9ff'
FONT='DejaVu Sans'; DB=Path.home()/'.local/share/ai-yako-v10/history.sqlite3'
PAGES=[('◈','Overview'),('✧','AI Intelligence'),('◇','Risk Analysis'),('⌁','Scenario Lab'),('▤','History'),('⚙','Model Center')]

def label(parent,text,size=11,color=TEXT,bold=False,**kw):
    return tk.Label(parent,text=text,bg=parent.cget('bg'),fg=color,font=(FONT,size,'bold' if bold else 'normal'),**kw)

def panel(parent,bg=SURFACE):
    return tk.Frame(parent,bg=bg,highlightbackground=BORDER,highlightthickness=1)

def button(parent,text,command,primary=False):
    normal=AQUA if primary else INNER; hover='#8ff8e5' if primary else '#293d58'
    b=tk.Label(parent,text=text,bg=normal,fg=BG if primary else TEXT,font=(FONT,10,'bold'),padx=18,pady=12,cursor='hand2')
    b.bind('<Enter>',lambda e:b.configure(bg=hover) if b.winfo_exists() else None)
    b.bind('<Leave>',lambda e:b.configure(bg=normal) if b.winfo_exists() else None)
    b.bind('<Button-1>',lambda e:command())
    b._colors=(normal,hover)
    return b

class App:
    def __init__(self,root):
        self.root=root;root.title('AI Yako V10.1 · Financial Intelligence Workstation');root.geometry('1390x860');root.minsize(1000,660);root.configure(bg=BG)
        self.events=queue.Queue();self.busy=False;self.last=None;self.page='';self.started=None;self.nav={};self.mode=tk.StringVar(value='QVAC + Regras')
        self.build();root.after(75,self.poll);root.protocol('WM_DELETE_WINDOW',self.close)
    def build(self):
        shell=tk.Frame(self.root,bg=BG);shell.pack(fill='both',expand=True)
        side=tk.Frame(shell,bg=SIDE,width=244);side.pack(side='left',fill='y');side.pack_propagate(False)
        brand=tk.Frame(side,bg=SIDE);brand.pack(fill='x',padx=24,pady=(30,38))
        label(brand,'◇',30,AQUA,True).pack(side='left',padx=(0,10))
        b=tk.Frame(brand,bg=SIDE);b.pack(side='left');label(b,'AI YAKO',20,TEXT,True).pack(anchor='w');label(b,'FINANCIAL INTELLIGENCE',8,MUTED).pack(anchor='w')
        label(side,'WORKSPACE',9,MUTED,True).pack(anchor='w',padx=26,pady=(0,14))
        for symbol,name in PAGES:
            row=tk.Frame(side,bg=SIDE,height=48,cursor='hand2');row.pack(fill='x',padx=12,pady=3);row.pack_propagate(False)
            accent=tk.Frame(row,bg=SIDE,width=3);accent.pack(side='left',fill='y')
            txt=label(row,f'  {symbol}    {name}',11,MUTED);txt.pack(side='left',fill='y',padx=12)
            for widget in (row,txt):
                widget.bind('<Button-1>',lambda e,n=name:self.navigate(n))
                widget.bind('<Enter>',lambda e,r=row,n=name:self.hover_nav(r,n,True))
                widget.bind('<Leave>',lambda e,r=row,n=name:self.hover_nav(r,n,False))
            self.nav[name]=(row,txt,accent)
        foot=tk.Frame(side,bg=SIDE);foot.pack(side='bottom',fill='x',padx=24,pady=27)
        label(foot,'●  LOCAL ENGINE',10,AQUA,True).pack(anchor='w');label(foot,'V10.1  /  READ-ONLY',9,MUTED).pack(anchor='w',pady=(7,0))
        right=tk.Frame(shell,bg=BG);right.pack(side='left',fill='both',expand=True)
        top=tk.Frame(right,bg=BG);top.pack(fill='x',padx=32,pady=(28,20))
        left=tk.Frame(top,bg=BG);left.pack(side='left');self.heading=label(left,'Overview',27,TEXT,True);self.heading.pack(anchor='w')
        self.subtitle=label(left,'Seu espaço privado de inteligência financeira.',11,MUTED);self.subtitle.pack(anchor='w',pady=(7,0))
        pill=tk.Frame(top,bg=SURFACE,highlightbackground=BORDER,highlightthickness=1);pill.pack(side='right',pady=8)
        label(pill,'●  LOCAL-FIRST  ·  QVAC',10,AQUA,True).pack(padx=16,pady=11)
        self.content=tk.Frame(right,bg=BG);self.content.pack(fill='both',expand=True,padx=32,pady=(0,18))
        footer=tk.Frame(right,bg=SIDE,height=43);footer.pack(side='bottom',fill='x');footer.pack_propagate(False)
        self.status=label(footer,'●  Sistema pronto  ·  Operações financeiras desabilitadas',9,MUTED);self.status.pack(side='left',padx=22,pady=12)
        label(footer,'PRIVATE BY DESIGN',9,AQUA,True).pack(side='right',padx=24,pady=12)
        self.navigate('Overview')
    def hover_nav(self,row,name,on):
        if name==self.page:return
        row.configure(bg=INNER if on else SIDE)
        for child in row.winfo_children():
            if isinstance(child,tk.Label):child.configure(bg=INNER if on else SIDE)
    def navigate(self,name):
        if self.busy and name!='AI Intelligence':return
        self.page=name;self.heading.configure(text=name)
        desc={'Overview':'Visão geral do seu ambiente de inteligência.','AI Intelligence':'Investigação fundamentada com ferramentas e inferência QVAC.','Risk Analysis':'Sinais verificáveis, sem conclusões inventadas.','Scenario Lab':'Explore hipóteses financeiras com matemática auditável.','History':'Registros locais das suas análises.','Model Center':'Estado do motor local e informações operacionais.'}
        self.subtitle.configure(text=desc[name])
        for n,(row,txt,accent) in self.nav.items():
            active=n==name;row.configure(bg=INNER if active else SIDE);txt.configure(bg=INNER if active else SIDE,fg=TEXT if active else MUTED);accent.configure(bg=AQUA if active else SIDE)
        for w in self.content.winfo_children():w.destroy()
        getattr(self,'page_'+name.lower().replace(' ','_'))()
    def section(self,parent,title,description=None):
        label(parent,title,15,TEXT,True).pack(anchor='w',padx=22,pady=(20,5))
        if description:label(parent,description,10,MUTED).pack(anchor='w',padx=22,pady=(0,14))
    def metric(self,parent,k,v,note,color=AQUA):
        c=panel(parent);c.pack(side='left',fill='both',expand=True,padx=(0,12))
        label(c,k.upper(),9,MUTED,True).pack(anchor='w',padx=20,pady=(19,12));label(c,v,23,color,True).pack(anchor='w',padx=20)
        label(c,note,9,MUTED).pack(anchor='w',padx=20,pady=(10,20))
    def page_overview(self):
        label(self.content,'OPERATIONS  /  CONTROL CENTER',10,AQUA,True).pack(anchor='w',pady=(0,17))
        row=tk.Frame(self.content,bg=BG);row.pack(fill='x')
        self.metric(row,'Inteligência','QVAC','Modelo local sob demanda')
        self.metric(row,'Privacidade','LOCAL','Sem servidor de análise',BLUE)
        self.metric(row,'Execução','READ ONLY','Sem transações ou assinaturas',GOLD)
        c=panel(self.content);c.pack(fill='x',pady=(26,0));self.section(c,'Intelligence workspace','Transforme cenários em evidências, hipóteses e análises compreensíveis.')
        button(c,'Iniciar análise financeira   →',lambda:self.navigate('AI Intelligence'),True).pack(anchor='w',padx=22,pady=(5,25))
        lower=panel(self.content);lower.pack(fill='x',pady=(16,0));self.section(lower,'Capacidades disponíveis')
        for x in ['01   Risk Analysis   /   Sinais financeiros e evidências','02   Scenario Lab   /   Simulação matemática de patrimônio','03   History   /   Relatórios armazenados localmente']:
            label(lower,x,11,MUTED).pack(anchor='w',padx=23,pady=9)
        tk.Frame(lower,bg=SURFACE,height=12).pack()
    def field(self,parent,value,height=5):
        t=tk.Text(parent,height=height,bg=INNER,fg=TEXT,insertbackground=AQUA,selectbackground='#365b73',relief='flat',wrap='word',font=(FONT,11),padx=17,pady=13,highlightthickness=1,highlightbackground=BORDER)
        t.insert('1.0',value);return t
    def page_ai_intelligence(self):
        c=panel(self.content);c.pack(fill='both',expand=True)
        self.section(c,'Financial inquiry','Descreva uma situação financeira. A análise de regras aparece antes da geração do modelo.')
        self.scenario=self.field(c,'Uma plataforma promete retorno garantido de 25% ao mês. Quais são os riscos?',4);self.scenario.pack(fill='x',padx=22)
        controls=tk.Frame(c,bg=SURFACE);controls.pack(fill='x',padx=22,pady=14)
        modes=tk.Frame(controls,bg=INNER);modes.pack(side='left',padx=(0,12))
        for value,title in [('QVAC + Regras','✧  QVAC + REGRAS'),('Somente regras','◇  SOMENTE REGRAS')]:
            x=label(modes,title,9,TEXT if self.mode.get()==value else MUTED,True,cursor='hand2');x.pack(side='left',padx=12,pady=12)
            x.bind('<Button-1>',lambda e,v=value:self.change_mode(v))
        self.mode_frame=modes
        self.run_btn=button(controls,'Analisar cenário   →',self.start,True);self.run_btn.pack(side='left')
        button(controls,'Exportar JSON',self.export).pack(side='left',padx=12)
        head=tk.Frame(c,bg=SURFACE);head.pack(fill='x',padx=22,pady=(13,10))
        label(head,'RESULTADO  /  EVIDÊNCIAS',10,MUTED,True).pack(side='left')
        self.phase=label(head,'AGUARDANDO',9,AQUA,True);self.phase.pack(side='right')
        body=tk.Frame(c,bg=INNER,highlightbackground=BORDER,highlightthickness=1);body.pack(fill='both',expand=True,padx=22,pady=(0,18))
        self.output=tk.Text(body,bg=INNER,fg=TEXT,relief='flat',wrap='word',font=(FONT,10),padx=20,pady=18,spacing2=5,state='disabled',insertbackground=AQUA)
        self.output.pack(side='left',fill='both',expand=True)
        sb=tk.Scrollbar(body,command=self.output.yview,relief='flat');sb.pack(side='right',fill='y');self.output.configure(yscrollcommand=sb.set)
        self.output.tag_configure('section',foreground=AQUA,font=(FONT,11,'bold'),spacing1=9,spacing3=7)
        self.output.tag_configure('warning',foreground=GOLD)
        label(c,'Informação educacional · Não comprova fraude nem substitui avaliação profissional.',9,MUTED).pack(anchor='w',padx=22,pady=(0,16))
    def change_mode(self,v):
        if self.busy:return
        self.mode.set(v)
        for w in self.mode_frame.winfo_children():w.configure(fg=TEXT if ('QVAC' in w.cget('text'))==('QVAC' in v) else MUTED)
    def write(self,text,section=False,replace=False):
        if self.page!='AI Intelligence':return
        self.output.configure(state='normal')
        if replace:self.output.delete('1.0','end')
        self.output.insert('end',text,'section' if section else ())
        self.output.see('end');self.output.configure(state='disabled')
    def start(self):
        if self.busy:return
        scenario=self.scenario.get('1.0','end').strip()
        try:report=analyze(scenario)
        except ValueError as exc:messagebox.showerror('Cenário inválido',str(exc));return
        self.last={'rules':report,'qvac':None};self.write('EVIDÊNCIAS VERIFICÁVEIS\n',section=True,replace=True)
        self.write(rule_explanation(report)+'\n\n')
        if self.mode.get()=='Somente regras':self.phase.configure(text='REGRAS CONCLUÍDAS');self.save();return
        self.busy=True;self.started=time.monotonic();self.phase.configure(text='INICIANDO QVAC');self.status.configure(text='●  QVAC em processamento  ·  Interface responsiva')
        self.run_btn.configure(bg='#446e68',fg=TEXT);self.write('INTERPRETAÇÃO QVAC\n',section=True)
        def worker():
            try:self.events.put(('done',asyncio.run(infer(report,lambda k,v:self.events.put((k,v))))))
            except Exception as exc:self.events.put(('error',f'{type(exc).__name__}: {exc}'))
        threading.Thread(target=worker,daemon=True).start()
    def poll(self):
        for _ in range(100):
            try:kind,value=self.events.get_nowait()
            except queue.Empty:break
            if kind=='status' and self.page=='AI Intelligence':self.phase.configure(text=str(value).upper()[:60])
            elif kind=='token':self.write(str(value))
            elif kind=='done':
                if self.last is not None:self.last['qvac']=value
                self.write(f"\n\nTEMPO TOTAL  {value.get('total_seconds','—')} s\n")
                self.write('MÉTRICAS  '+json.dumps(value.get('timings',{}),ensure_ascii=False)+'\n')
                self.busy=False;self.save();self.status.configure(text='●  Análise concluída  ·  QVAC local')
                if self.page=='AI Intelligence':self.phase.configure(text='CONCLUÍDO');self.run_btn.configure(bg=AQUA,fg=BG)
            elif kind=='error':
                if self.last is not None:self.last['qvac_error']=value
                self.write('\n\nQVAC INDISPONÍVEL: '+value+'\nOs achados determinísticos continuam disponíveis.\n')
                self.busy=False;self.save();self.status.configure(text='●  Erro QVAC  ·  Regras preservadas')
                if self.page=='AI Intelligence':self.phase.configure(text='FALHA DO MODELO');self.run_btn.configure(bg=AQUA,fg=BG)
        self.root.after(75,self.poll)
    def save(self):
        if not self.last:return
        try:
            DB.parent.mkdir(parents=True,exist_ok=True);db=sqlite3.connect(DB)
            db.execute('CREATE TABLE IF NOT EXISTS analyses (id INTEGER PRIMARY KEY, created TEXT NOT NULL, scenario TEXT NOT NULL, report TEXT NOT NULL)')
            db.execute('INSERT INTO analyses(created,scenario,report) VALUES(?,?,?)',(datetime.now().isoformat(timespec='seconds'),self.last['rules']['scenario'],json.dumps(self.last,ensure_ascii=False)))
            db.commit();db.close()
        except (OSError,sqlite3.Error) as exc:self.status.configure(text='●  Histórico não salvo: '+str(exc)[:100])
    def export(self):
        if not self.last:messagebox.showinfo('Sem relatório','Execute uma análise primeiro.');return
        name=filedialog.asksaveasfilename(defaultextension='.json',filetypes=[('JSON','*.json')]);
        if not name:return
        p=Path(name)
        try:
            with p.open('x',encoding='utf-8') as f:json.dump(self.last,f,ensure_ascii=False,indent=2)
            p.chmod(0o600)
        except FileExistsError:messagebox.showerror('Arquivo existente','Escolha um nome ainda não utilizado.')
        except OSError as exc:messagebox.showerror('Erro de exportação',str(exc))
    def page_risk_analysis(self):
        c=panel(self.content);c.pack(fill='both',expand=True);self.section(c,'Risk intelligence','Análise determinística auditável e independente do modelo.')
        entry=self.field(c,'Oferta urgente com retorno garantido de 30% ao mês.',5);entry.pack(fill='x',padx=22)
        out=self.field(c,'Aguardando cenário...',12);out.pack(fill='both',expand=True,padx=22,pady=(18,12))
        def run():
            try:r=analyze(entry.get('1.0','end'));text=rule_explanation(r)
            except ValueError as exc:text=str(exc)
            out.delete('1.0','end');out.insert('1.0',text)
        button(c,'Avaliar sinais   →',run,True).pack(anchor='w',padx=22,pady=(0,23))
    def page_scenario_lab(self):
        c=panel(self.content);c.pack(fill='both',expand=True);self.section(c,'Scenario modeling','Projeções matemáticas hipotéticas, não previsões de mercado.')
        row=tk.Frame(c,bg=SURFACE);row.pack(fill='x',padx=22,pady=(0,16));fields={}
        for title,default in [('Capital inicial','10000'),('Taxa mensal (%)','1'),('Meses','60'),('Aporte mensal','0')]:
            f=tk.Frame(row,bg=SURFACE);f.pack(side='left',fill='x',expand=True,padx=(0,12));label(f,title,10,MUTED).pack(anchor='w',pady=(0,8))
            e=tk.Entry(f,bg=INNER,fg=TEXT,insertbackground=AQUA,relief='flat',font=(FONT,12),highlightbackground=BORDER,highlightthickness=1)
            e.insert(0,default);e.pack(fill='x',ipady=12);fields[title]=e
        result=label(c,'Configure os parâmetros para calcular.',12,AQUA,True);result.pack(anchor='w',padx=23,pady=(2,12))
        chart=tk.Canvas(c,bg=INNER,highlightthickness=0,height=290);chart.pack(fill='both',expand=True,padx=22,pady=(0,15))
        state={'points':None}
        def draw(event=None):
            if not state['points']:return
            pts=state['points'];chart.delete('all');w=max(chart.winfo_width(),300);h=max(chart.winfo_height(),200)
            lo=min(x['balance'] for x in pts);hi=max(x['balance'] for x in pts);span=max(hi-lo,1)
            for j in range(1,5):
                y=20+(h-55)*j/4;chart.create_line(22,y,w-22,y,fill=BORDER)
            xy=[]
            for i,p in enumerate(pts):xy.extend([24+(w-48)*i/max(1,len(pts)-1),h-28-(p['balance']-lo)*(h-65)/span])
            if len(xy)>=4:chart.create_line(*xy,fill=AQUA,width=3,smooth=True)
            chart.create_text(22,14,anchor='w',fill=MUTED,text='EVOLUÇÃO HIPOTÉTICA',font=(FONT,9))
            chart.create_text(w-22,h-12,anchor='e',fill=MUTED,text='MESES  →',font=(FONT,9))
        chart.bind('<Configure>',draw)
        def run():
            try:r=simulate(fields['Capital inicial'].get(),fields['Taxa mensal (%)'].get(),fields['Meses'].get(),fields['Aporte mensal'].get())
            except (ValueError,OverflowError) as exc:messagebox.showerror('Parâmetros inválidos',str(exc));return
            result.configure(text=f"SALDO PROJETADO   R$ {r['final_balance']:,.2f}    ·    APORTADO   R$ {r['total_contributed']:,.2f}")
            state['points']=r['points'];draw()
        button(c,'Calcular projeção   →',run,True).pack(anchor='w',padx=22,pady=(0,22));run()
    def page_history(self):
        c=panel(self.content);c.pack(fill='both',expand=True);self.section(c,'Local archive','Histórico armazenado neste computador, sem sincronização na nuvem.')
        area=self.field(c,'',20);area.pack(fill='both',expand=True,padx=22,pady=(0,20))
        if DB.exists():
            try:
                with sqlite3.connect(DB) as db:rows=db.execute('SELECT created,scenario FROM analyses ORDER BY id DESC LIMIT 60').fetchall()
                area.insert('1.0','\n\n'.join(f'{dt}\n{scenario[:320]}' for dt,scenario in rows) if rows else 'Nenhuma análise salva.')
            except sqlite3.Error as exc:area.insert('1.0','Histórico indisponível: '+str(exc))
        else:area.insert('1.0','Nenhuma análise salva.')
        area.configure(state='disabled')
    def page_model_center(self):
        c=panel(self.content);c.pack(fill='both',expand=True);self.section(c,'Runtime & diagnostics','Informações locais do motor e limites de operação.')
        for title,value in [('PROVEDOR','Tether QVAC Python SDK'),('MODELO','Llama 3.2 1B Instruct Q4_0'),('INFERÊNCIA','Sob demanda; modelo liberado ao final'),('PRIVACIDADE','Análises locais; histórico SQLite não criptografado'),('REDE','Modo offline demonstrado anteriormente; esta sessão não verifica isolamento'),('SEGURANÇA','Nenhuma operação de carteira, assinatura ou transferência')]:
            row=tk.Frame(c,bg=SURFACE);row.pack(fill='x',padx=23,pady=13)
            label(row,title,10,MUTED,True).pack(side='left');label(row,value,10,TEXT).pack(side='right')
        label(c,'O SDK pode consultar registros externos se o modelo não estiver em cache. Não há bloqueio de rede embutido.',10,GOLD,wraplength=780,justify='left').pack(anchor='w',padx=23,pady=20)
    def close(self):
        if self.busy and not messagebox.askyesno('Inferência em andamento','Fechar a janela não garante o cancelamento imediato do worker. Deseja sair?'):return
        self.root.destroy()

def main():
    root=tk.Tk();App(root);root.mainloop()

if __name__=='__main__':main()
