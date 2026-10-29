#!/usr/bin/env python3
"""AI Yako desktop: local-first, no Django, no cloud, no wallet signing."""
import json, os, subprocess, threading, tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

APP_NAME='AI Yako — Local Financial Intelligence'

def analyze_offline(text):
    """Deterministic risk flags, NOT model inference or financial advice."""
    t=text.casefold().strip()
    if not t: raise ValueError('Enter a financial scenario.')
    flags=[]
    for term, label in [('private key','Private key exposure'),('seed phrase','Seed phrase exposure'),('urgent','Urgency pressure'),('guaranteed','Unrealistic guarantee'),('leverage','Leverage risk'),('all funds','Concentration risk')]:
        if term in t: flags.append(label)
    return {'mode':'DETERMINISTIC RULES (not QVAC)', 'risk':'REVIEW REQUIRED' if flags else 'NOT ASSESSED', 'flags':flags, 'notice':'No financial execution, signing or broadcasting is enabled.'}

def local_qvac(prompt, executable, model, timeout=120):
    """Optional offline local model executable, explicitly configured by user.

    This is a generic local GGUF runner interface, not a verified QVAC SDK integration.
    No shell, network endpoint, download or automatic installation.
    """
    binary=Path(executable).expanduser().resolve()
    weights=Path(model).expanduser().resolve()
    if not binary.is_file() or not os.access(binary, os.X_OK):
        raise RuntimeError('Local inference executable is missing or not executable.')
    if not weights.is_file() or weights.stat().st_size == 0:
        raise RuntimeError('Local model file is missing or empty.')
    if weights.suffix.lower() != '.gguf':
        raise RuntimeError('This adapter expects a GGUF model file.')
    env={k:v for k,v in os.environ.items() if not any(x in k.upper() for x in ('TOKEN','PASSWORD','SECRET','API_KEY'))}
    env['HF_HUB_OFFLINE']='1'; env['TRANSFORMERS_OFFLINE']='1'
    cmd=[str(binary),'-m',str(weights),'-p',prompt,'-n','384','--temp','0.2']
    try:
        result=subprocess.run(cmd, text=True, capture_output=True, timeout=timeout, env=env, check=False)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError('Local model timed out.') from exc
    if result.returncode != 0:
        raise RuntimeError('Local model failed (exit {}). {}'.format(result.returncode, result.stderr[-350:]))
    return result.stdout.strip()

class App:
    def __init__(self, root):
        self.root=root; root.title(APP_NAME); root.geometry('1000x740'); root.minsize(720,550)
        root.configure(bg='#111827')
        self.mode=tk.StringVar(value='Rules-only (available offline)')
        self.binary=tk.StringVar(value=os.environ.get('AI_YAKO_LOCAL_RUNNER',''))
        self.model=tk.StringVar(value=os.environ.get('AI_YAKO_LOCAL_MODEL',''))
        frame=ttk.Frame(root,padding=22); frame.pack(fill='both',expand=True)
        ttk.Label(frame,text='AI YAKO  /  LOCAL INTELLIGENCE',font=('Sans',19,'bold')).pack(anchor='w',pady=(0,6))
        ttk.Label(frame,text='Offline desktop preview • no Django session • no funds movement').pack(anchor='w',pady=(0,18))
        ttk.Label(frame,text='Financial scenario').pack(anchor='w')
        self.input=tk.Text(frame,height=7,wrap='word'); self.input.pack(fill='x',pady=(5,14))
        self.input.insert('1.0','Analyze the risks of an urgent offer promising guaranteed returns on a leveraged position.')
        ttk.Label(frame,text='Execution mode').pack(anchor='w')
        ttk.Combobox(frame,textvariable=self.mode,values=['Rules-only (available offline)','Local GGUF inference (requires compatible installed runner and model)'],state='readonly').pack(fill='x',pady=(4,12))
        ttk.Label(frame,text='Local inference executable (optional)').pack(anchor='w')
        ttk.Entry(frame,textvariable=self.binary).pack(fill='x',pady=(3,8))
        ttk.Label(frame,text='Local .gguf model path (optional)').pack(anchor='w')
        ttk.Entry(frame,textvariable=self.model).pack(fill='x',pady=(3,12))
        self.button=ttk.Button(frame,text='Analyze locally',command=self.run); self.button.pack(anchor='w',pady=(2,14))
        ttk.Label(frame,text='Results / evidence').pack(anchor='w')
        self.output=tk.Text(frame,height=13,wrap='word',state='disabled'); self.output.pack(fill='both',expand=True,pady=(4,6))
        ttk.Label(frame,text='WDK: NOT CONNECTED  •  Signing: DISABLED  •  Network calls: NONE by this application').pack(anchor='w')
    def show(self,content):
        self.output.configure(state='normal'); self.output.delete('1.0','end'); self.output.insert('1.0',content); self.output.configure(state='disabled')
    def run(self):
        scenario=self.input.get('1.0','end').strip()
        if not scenario: messagebox.showwarning('Missing input','Enter a scenario.'); return
        self.button.configure(state='disabled'); self.show('Processing locally...')
        mode=self.mode.get(); runner=self.binary.get(); model=self.model.get()
        def task():
            try:
                rules=analyze_offline(scenario)
                report=json.dumps(rules,indent=2)
                if mode.startswith('Local GGUF'):
                    prompt='You are a cautious financial risk analyst. Never claim to execute transactions. Analyze the following scenario, distinguish facts from assumptions, and list risks: '+scenario
                    result=local_qvac(prompt,runner,model)
                    report+='\n\nLOCAL MODEL OUTPUT (unverified model provenance):\n'+result
                self.root.after(0,lambda: self.show(report))
            except Exception as exc:
                self.root.after(0,lambda: self.show('ERROR: '+str(exc)))
            finally:
                self.root.after(0,lambda: self.button.configure(state='normal'))
        threading.Thread(target=task,daemon=True).start()

def main():
    root=tk.Tk(); App(root); root.mainloop()

if __name__=='__main__': main()
