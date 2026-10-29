"""AI Yako V9 Linux GUI. No Django, wallet access or signing."""
import asyncio
import json
import queue
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from yako_v91_engine import analyze_rules, infer_qvac, MODEL_LABEL


class App:
    def __init__(self, root):
        self.root = root
        root.title('AI Yako V9.1 — QVAC Financial Intelligence')
        root.geometry('1050x790')
        root.minsize(760, 580)
        self.events = queue.Queue()
        self.busy = False
        self.report = None
        self.closing = False
        self.mode = tk.StringVar(value='QVAC + Regras')
        self.status = tk.StringVar(value='Pronto • QVAC será inicializado sob demanda')
        outer = ttk.Frame(root, padding=22)
        outer.pack(fill='both', expand=True)
        ttk.Label(outer, text='AI YAKO  /  FINANCIAL INTELLIGENCE', font=('Sans', 19, 'bold')).pack(anchor='w')
        ttk.Label(outer, text='Linux V9.1  •  QVAC oficial  •  Sem assinatura ou execução financeira').pack(anchor='w', pady=(4, 18))
        ttk.Label(outer, text='Cenário financeiro').pack(anchor='w')
        self.scenario = tk.Text(outer, height=6, wrap='word', font=('Sans', 11))
        self.scenario.pack(fill='x', pady=(5, 12))
        self.scenario.insert('1.0', 'Uma plataforma promete retorno garantido de 25% ao mês. Quais são os riscos?')
        row = ttk.Frame(outer)
        row.pack(fill='x', pady=(0, 12))
        ttk.Label(row, text='Modo:').pack(side='left')
        ttk.Combobox(row, textvariable=self.mode, state='readonly', width=20,
                     values=('QVAC + Regras', 'Somente regras')).pack(side='left', padx=(10, 16))
        self.button = ttk.Button(row, text='Analisar', command=self.start)
        self.button.pack(side='left')
        ttk.Button(row, text='Exportar JSON', command=self.export).pack(side='left', padx=(10, 0))
        ttk.Label(outer, textvariable=self.status).pack(anchor='w', pady=(0, 10))
        ttk.Label(outer, text='Análise e evidências').pack(anchor='w')
        output_frame = ttk.Frame(outer)
        output_frame.pack(fill='both', expand=True, pady=(4, 12))
        self.output = tk.Text(output_frame, wrap='word', state='disabled', font=('Sans', 10))
        scroll = ttk.Scrollbar(output_frame, command=self.output.yview)
        self.output.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        self.output.pack(side='left', fill='both', expand=True)
        ttk.Label(outer, text='Modelo: ' + MODEL_LABEL + '  •  Primeira execução pode exigir acesso ao registro.').pack(anchor='w')
        ttk.Label(outer, text='Análise informativa; não comprova fraude. Teste offline já realizado nesta instalação; verifique cada nova distribuição.').pack(anchor='w')
        root.protocol('WM_DELETE_WINDOW', self.close)
        root.after(80, self.poll)

    def write(self, text, clear=False):
        self.output.configure(state='normal')
        if clear:
            self.output.delete('1.0', 'end')
        self.output.insert('end', text)
        self.output.see('end')
        self.output.configure(state='disabled')

    def start(self):
        if self.busy:
            return
        scenario = self.scenario.get('1.0', 'end').strip()
        try:
            report = analyze_rules(scenario)
        except ValueError as exc:
            messagebox.showwarning('Cenário inválido', str(exc))
            return
        self.busy = True
        self.report = report
        self.button.configure(state='disabled')
        self.write('ANÁLISE DETERMINÍSTICA\n' + json.dumps(report['rules'], ensure_ascii=False, indent=2) + '\n\n', clear=True)
        if self.mode.get() == 'Somente regras':
            self.status.set('Análise determinística concluída')
            self.busy = False
            self.button.configure(state='normal')
            return
        self.write('RESPOSTA QVAC\n')
        self.status.set('Preparando QVAC…')
        def worker():
            try:
                result = asyncio.run(infer_qvac(scenario, report, lambda k, v: self.events.put((k, v))))
                self.events.put(('complete', result))
            except Exception as exc:
                self.events.put(('error', f'{type(exc).__name__}: {exc}'))
        threading.Thread(target=worker, daemon=True).start()

    def poll(self):
        if self.closing:
            return
        for _ in range(150):
            try:
                kind, value = self.events.get_nowait()
            except queue.Empty:
                break
            if kind == 'status':
                self.status.set(value)
            elif kind == 'token':
                self.write(value)
            elif kind == 'complete':
                self.report['qvac'] = value
                self.write('\n\nTempo total: ' + str(value['elapsed_seconds']) + ' s\n' + 'Métricas: ' + json.dumps(value.get('timings', {}), ensure_ascii=False) + '\n')
                self.status.set('Concluído • Inferência QVAC real')
                self.busy = False
                self.button.configure(state='normal')
            elif kind == 'error':
                self.report['qvac_error'] = value
                self.write('\n\nERRO QVAC: ' + value + '\nAs regras acima continuam disponíveis.\n')
                self.status.set('Falha QVAC • Análise determinística preservada')
                self.busy = False
                self.button.configure(state='normal')
        self.root.after(80, self.poll)

    def export(self):
        if not self.report:
            messagebox.showinfo('Sem relatório', 'Execute uma análise primeiro.')
            return
        dest = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON', '*.json')],
                                            initialfile='ai-yako-v91-evidence.json')
        if not dest:
            return
        path = Path(dest)
        if path.exists():
            messagebox.showerror('Arquivo existente', 'Para proteger evidências, não sobrescrevemos relatórios.')
            return
        try:
            with path.open('x', encoding='utf-8') as fh:
                json.dump(self.report, fh, ensure_ascii=False, indent=2)
                fh.write('\n')
            path.chmod(0o600)
            self.status.set('Relatório exportado: ' + str(path))
        except OSError as exc:
            messagebox.showerror('Falha na exportação', str(exc))

    def close(self):
        if self.busy and not messagebox.askyesno('Inferência em andamento',
                                                  'Fechar agora interromperá a interface enquanto o worker termina. Continuar?'):
            return
        self.closing = True
        self.root.destroy()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
