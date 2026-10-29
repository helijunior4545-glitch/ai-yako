"""V7 standalone GUI; V6 GUI remains untouched."""
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from yako_v7_engine import analyze, digest

class App:
    def __init__(self,root):
        root.title('AI Yako V7 — Offline Evidence'); root.geometry('1040x760'); root.minsize(750,600)
        self.root=root
        frame=ttk.Frame(root,padding=20); frame.pack(fill='both',expand=True)
        ttk.Label(frame,text='AI YAKO / OFFLINE EVIDENCE',font=('Sans',20,'bold')).pack(anchor='w')
        ttk.Label(frame,text='Deterministic analysis + optional local GGUF runner (not official QVAC). WDK/signing disabled.').pack(anchor='w',pady=(3,16))
        ttk.Label(frame,text='Financial scenario').pack(anchor='w')
        self.scenario=tk.Text(frame,height=6,wrap='word'); self.scenario.pack(fill='x',pady=(3,12))
        self.scenario.insert('1.0','Analyze an urgent offer guaranteeing returns with leverage.')
        self.runner=tk.StringVar(); self.model=tk.StringVar(); self.sha=tk.StringVar()
        for label,var in [('Local executable (optional)',self.runner),('GGUF model path (optional)',self.model),('Pinned model SHA256 (required when model is configured)',self.sha)]:
            ttk.Label(frame,text=label).pack(anchor='w'); ttk.Entry(frame,textvariable=var).pack(fill='x',pady=(2,8))
        self.isolate=tk.BooleanVar(value=False)
        ttk.Checkbutton(frame,text='Attempt Linux network namespace isolation (requires OS permission)',variable=self.isolate).pack(anchor='w',pady=(0,10))
        self.button=ttk.Button(frame,text='Analyze locally',command=self.run); self.button.pack(anchor='w')
        ttk.Label(frame,text='Evidence JSON (contains scenario-derived model output; do not share confidential data)').pack(anchor='w',pady=(14,4))
        self.output=tk.Text(frame,wrap='word',state='disabled'); self.output.pack(fill='both',expand=True)
    def show(self,s):
        self.output.configure(state='normal'); self.output.delete('1.0','end'); self.output.insert('1.0',s); self.output.configure(state='disabled')
    def run(self):
        scenario=self.scenario.get('1.0','end').strip(); runner=self.runner.get().strip(); model=self.model.get().strip(); sha=self.sha.get().strip()
        if not scenario: messagebox.showwarning('Missing scenario','Enter a scenario'); return
        self.button.configure(state='disabled'); self.show('Processing locally...')
        def task():
            try: result=json.dumps(analyze(scenario,runner or None,model or None,sha or None,self.isolate.get()),indent=2,ensure_ascii=False)
            except Exception as e: result='ERROR: '+str(e)
            self.root.after(0,lambda:self.show(result)); self.root.after(0,lambda:self.button.configure(state='normal'))
        threading.Thread(target=task,daemon=True).start()
if __name__=='__main__':
    root=tk.Tk(); App(root); root.mainloop()
