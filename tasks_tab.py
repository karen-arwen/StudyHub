# tasks_tab.py
import tkinter as tk
from tkinter import ttk, filedialog
from command import CommandManager, AddTask, EditTask, DeleteTask, ToggleDone
from storage import StatsRepo
from dialogs import TaskDialog
from widgets import CoinFloat

CHECK_UN = '☐'
CHECK_OK = '☑'

# mapinha de emojis coloridos (6 tons)
_TAG_EMOJI = ["🟪","🟩","🟦","🟧","🟥","🟨"]

def _tag_emoji_for(text: str) -> str:
    """Escolhe um emoji colorido estável a partir do texto da tag."""
    h = 0
    for ch in text.lower():
        h = (h * 131 + ord(ch)) & 0xFFFFFFFF
    return _TAG_EMOJI[h % len(_TAG_EMOJI)]

def _pretty_tags(tags):
    """Converte ['python','programming'] -> '🟪 python   🟩 programming'"""
    return "   ".join(f"{_tag_emoji_for(t)} {t}" for t in (tags or []))


class TasksTab(ttk.Frame):
    def __init__(self, parent, repo, profile_repo=None):
        super().__init__(parent)
        self.repo = repo
        self.profile = profile_repo  # para recompensas visuais
        self.cm = CommandManager()
        self.stats = StatsRepo()

        # Barra superior
        top = ttk.Frame(self); top.pack(fill=tk.X, pady=6)
        ttk.Label(top, text="Busca:").pack(side=tk.LEFT, padx=4)
        self.q = tk.StringVar(); e = ttk.Entry(top, textvariable=self.q, width=28); e.pack(side=tk.LEFT)
        e.bind("<KeyRelease>", lambda ev: self.refresh())
        ttk.Button(top, text="＋ Nova", style="Accent.TButton", command=self.add).pack(side=tk.LEFT, padx=8)
        ttk.Button(top, text="✎ Editar", command=self.edit).pack(side=tk.LEFT)
        ttk.Button(top, text="🗑", command=self.delete).pack(side=tk.LEFT)
        ttk.Button(top, text="↶ Undo", command=lambda:(self.cm.undo(), self.refresh())).pack(side=tk.RIGHT)
        ttk.Button(top, text="↷ Redo", command=lambda:(self.cm.redo(), self.refresh())).pack(side=tk.RIGHT)
        ttk.Button(top, text="⬇ CSV", command=self.export_csv).pack(side=tk.RIGHT, padx=6)

        cols = ("id","title","priority","tags","scheduled","done")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=18)
        headers = ["#","Tarefa","Pri","Tags","Data","Feita"]
        for c,h in zip(cols,headers): self.tree.heading(c, text=h, command=lambda col=c: self.sort_by(col))
        widths = [50, 520, 60, 260, 120, 70]
        for c,w in zip(cols,widths): self.tree.column(c, width=w, anchor=tk.W)

        self.tree.pack(fill=tk.BOTH, expand=True, pady=6)
        self.tree.bind("<Button-1>", self.on_click)

        # tasks_tab.py — dentro de __init__ após self.tree.pack(...)
        # Paleta suave que funciona claro/escuro
        self.tree.tag_configure("pri1", background="#FDE7E9", foreground="#7F1D1D")  # vermelho leve
        self.tree.tag_configure("pri2", background="#FEF3C7", foreground="#92400E")  # âmbar
        self.tree.tag_configure("pri3", background="#DCFCE7", foreground="#065F46")  # verde
        self.tree.tag_configure("done", foreground="#9AA0A6")                        # concluída (apaga texto)


        self.sort_col = "done"   # feitas ao fim
        self.sort_reverse = False
        self.refresh()

    # ---------- helpers ----------
    def filter_items(self):
        q = self.q.get().strip().lower()
        items = self.repo.list_all()
        if not q: return items
        def match(t):
            return (q in t.title.lower()) or any(q in tag.lower() for tag in t.tags) or q in str(t.priority)
        return [t for t in items if match(t)]

    def refresh(self):
        # limpa a tabela
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        # carrega itens + filtro de busca
        try:
            items = list(self.repo.list_all())
        except Exception:
            items = []

        q = (self.q.get() or "").strip().lower()
        if q:
            def hit(t):
                if q in (t.title or "").lower(): 
                    return True
                if q in str(getattr(t, "priority", "")): 
                    return True
                for tg in (t.tags or []):
                    if q in (tg or "").lower(): 
                        return True
                return False
            items = [t for t in items if hit(t)]

        # ordena: feitas por último; depois prioridade (1..3); depois data
        def sort_key(t):
            sched = t.scheduled or "9999-99-99"
            pri = getattr(t, "priority", 3) or 3
            return (t.done, pri, sched, t.id)
        items.sort(key=sort_key)

        # insere (com cores por prioridade e tags fofas)
        for t in items:
            check = CHECK_OK if t.done else CHECK_UN
            row_tags = ["done"] if t.done else [f"pri{getattr(t, 'priority', 3)}"]
            self.tree.insert(
                "", tk.END, iid=str(t.id),
                values=(
                    t.id,
                    t.title,
                    getattr(t, "priority", 3),
                    _pretty_tags(t.tags),       # 👈 tags bonitinhas aqui
                    t.scheduled or "",
                    check
                ),
                tags=tuple(row_tags)
            )


    def current_id(self):
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    # ---------- eventos ----------
    def on_click(self, ev):
        region = self.tree.identify("region", ev.x, ev.y)
        if region != "cell": return
        iid = self.tree.identify_row(ev.y)
        col = self.tree.identify_column(ev.x)
        if not iid: return
        # coluna #6 é 'done'
        if col == "#6":
            self.cm.do(ToggleDone(self.repo, int(iid), stats=self.stats))
            # recompensa (leve) ao concluir tarefa
            t = self.repo.get(int(iid))
            if t.done and self.profile:
                self.profile.add_rewards(coins=5, xp=2)
                # animação de moedinha perto da tree
                CoinFloat.show(self.winfo_toplevel(), "+5 🪙", near_widget=self.tree, offset=(0, -10))
            self.refresh()

    def add(self):
        dlg = TaskDialog(self)
        self.wait_window(dlg.win)
        if dlg.result and dlg.result.get("title"):
            self.cm.do(AddTask(self.repo, **dlg.result)); self.refresh()

    def edit(self):
        tid = self.current_id()
        if not tid: return
        t = self.repo.get(tid)
        init = {"title": t.title, "priority": t.priority, "tags": t.tags, "scheduled": t.scheduled}
        dlg = TaskDialog(self, initial=init)
        self.wait_window(dlg.win)
        if dlg.result:
            self.cm.do(EditTask(self.repo, tid, dlg.result)); self.refresh()

    def delete(self):
        tid = self.current_id()
        if not tid: return
        self.cm.do(DeleteTask(self.repo, tid)); self.refresh()

    def sort_by(self, col):
        self.sort_col = col
        self.refresh()

    def export_csv(self):
        import csv
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if not path: return
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["id","title","priority","tags","scheduled","done"])
            for t in self.repo.list_all():
                w.writerow([t.id, t.title, t.priority, ";".join(t.tags), t.scheduled or "", t.done])
