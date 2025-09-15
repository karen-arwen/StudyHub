import tkinter as tk
from tkinter import ttk, simpledialog, filedialog
from command import CommandManager, AddTask, EditTask, DeleteTask, ToggleDone
from storage import StatsRepo

class TasksTab(ttk.Frame):
    def __init__(self, parent, repo):
        super().__init__(parent)
        self.repo = repo
        self.cm = CommandManager()
        self.stats = StatsRepo()

        # Barra superior (busca + ações)
        top = ttk.Frame(self); top.pack(fill=tk.X, pady=6)
        ttk.Label(top, text="Busca:").pack(side=tk.LEFT, padx=4)
        self.q = tk.StringVar()
        e = ttk.Entry(top, textvariable=self.q, width=28); e.pack(side=tk.LEFT)
        e.bind("<KeyRelease>", lambda ev: self.refresh())

        ttk.Button(top, text="＋ Adicionar", style="Accent.TButton", command=self.add).pack(side=tk.LEFT, padx=8)
        ttk.Button(top, text="✎ Editar", command=self.edit).pack(side=tk.LEFT)
        ttk.Button(top, text="✔/✘", command=self.toggle).pack(side=tk.LEFT)
        ttk.Button(top, text="🗑", command=self.delete).pack(side=tk.LEFT)
        ttk.Button(top, text="↶ Undo", command=lambda: (self.cm.undo(), self.refresh())).pack(side=tk.RIGHT)
        ttk.Button(top, text="↷ Redo", command=lambda: (self.cm.redo(), self.refresh())).pack(side=tk.RIGHT)
        ttk.Button(top, text="⬇ CSV", command=self.export_csv).pack(side=tk.RIGHT, padx=6)

        cols = ("id","title","priority","tags","scheduled","done")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=16)
        headers = ["#","Tarefa","Pri","Tags","Data","Feita?"]
        for c,h in zip(cols,headers): self.tree.heading(c, text=h, command=lambda col=c: self.sort_by(col))
        for c,w in zip(cols,[50,340,60,220,100,70]): self.tree.column(c, width=w, anchor=tk.W)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=6)

        self.sort_reverse=False; self.sort_col="id"
        self.refresh()

    def filter(self, items):
        q = self.q.get().strip().lower()
        if not q: return items
        def match(t):
            blob = f"{t.title} {' '.join(t.tags)} {t.priority} {t.scheduled}".lower()
            return q in blob
        return [t for t in items if match(t)]

    def refresh(self):
        for x in self.tree.get_children(): self.tree.delete(x)
        items = self.filter(self.repo.list_all())
        # sort
        items.sort(key=lambda t: getattr(t, self.sort_col) if self.sort_col!="tags" else ",".join(t.tags), reverse=self.sort_reverse)
        for t in items:
            self.tree.insert("", tk.END, iid=str(t.id), values=(t.id, t.title, t.priority, ", ".join(t.tags), t.scheduled or "", "✔" if t.done else "✘"))

    def current_id(self):
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    def add(self):
        title = simpledialog.askstring("Nova tarefa", "Título:")
        if not title: return
        pri = simpledialog.askinteger("Prioridade", "1 (baixo), 2 (médio), 3 (alto)", initialvalue=2, minvalue=1, maxvalue=3)
        tags = simpledialog.askstring("Tags", "Separadas por vírgula:") or ""
        sch = simpledialog.askstring("Agendar (YYYY-MM-DD)", "Opcional:") or None
        self.cm.do(AddTask(self.repo, title, pri, [t.strip() for t in tags.split(',') if t.strip()], sch))
        self.refresh()

    def edit(self):
        tid = self.current_id()
        if not tid: return
        t = self.repo.get(tid)
        title = simpledialog.askstring("Editar título", "Título:", initialvalue=t.title) or t.title
        pri = simpledialog.askinteger("Prioridade", "1..3", initialvalue=t.priority, minvalue=1, maxvalue=3) or t.priority
        tags = simpledialog.askstring("Tags", "vírgulas:", initialvalue=", ".join(t.tags)) or ", ".join(t.tags)
        sch = simpledialog.askstring("Agendar", initialvalue=t.scheduled or "") or t.scheduled
        self.cm.do(EditTask(self.repo, tid, {"title":title, "priority":pri, "tags":[s.strip() for s in tags.split(',') if s.strip()], "scheduled":sch}))
        self.refresh()

    def delete(self):
        tid = self.current_id()
        if not tid: return
        self.cm.do(DeleteTask(self.repo, tid))
        self.refresh()

    def toggle(self):
        tid = self.current_id()
        if not tid: return
        self.cm.do(ToggleDone(self.repo, tid, stats=self.stats))
        self.refresh()

    def sort_by(self, col):
        if self.sort_col == col: self.sort_reverse = not self.sort_reverse
        else: self.sort_col = col; self.sort_reverse=False
        self.refresh()

    def export_csv(self):
        import csv
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if not path: return
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f); w.writerow(["id","title","priority","tags","scheduled","done"]) 
            for t in self.repo.list_all(): w.writerow([t.id, t.title, t.priority, ";".join(t.tags), t.scheduled or "", t.done])