# dialogs.py (trecho) — Modal melhorado
import tkinter as tk
from tkinter import ttk, messagebox
import datetime as dt
import calendar
from widgets import PlaceholderEntry, TagInput
from tags_repo import TagsRepo


# dialogs.py (SUBSTITUIR ESTA CLASSE)
import tkinter as tk
from tkinter import ttk, messagebox
import datetime as dt
import calendar
from widgets import PlaceholderEntry, TagInput
from tags_repo import TagsRepo


class Modal(ttk.Frame):
    """Base para modais com layout padronizado (card), título e ações."""
    def __init__(self, parent, title="Janela"):
        self.win = tk.Toplevel(parent)
        self.win.title(title)
        self.win.transient(parent)
        self.win.grab_set()
        self.win.resizable(True, True)           # permite crescer
        self.win.minsize(640, 320)               # tamanho mínimo decente

        super().__init__(self.win, style="Card.TFrame")
        self.pack(padx=16, pady=16, fill=tk.BOTH, expand=True)

        # Grid raiz elástico
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # Cabeçalho
        head = ttk.Frame(self, style="Card.TFrame")
        head.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        ttk.Label(head, text=title, style="Header.TLabel").pack(side=tk.LEFT)

        self._row = 1  # linha atual para add_row
        self.result = None

        # atalhos
        self.win.bind("<Return>", lambda e: self._on_enter())
        self.win.bind("<Escape>", lambda e: self.win.destroy())

        self._ok_callback = None  # setado em add_actions

    def _on_enter(self):
        if callable(self._ok_callback):
            self._ok_callback()

    def add_row(self, label_text, widget_left=None, widget_right=None):
        """Linha com Label à esquerda e 1–2 widgets à direita (form 2 colunas)."""
        lbl = ttk.Label(self, text=label_text)
        lbl.grid(row=self._row, column=0, sticky="w", padx=(2, 12), pady=6)

        cell = ttk.Frame(self, style="Card.TFrame")
        cell.grid(row=self._row, column=1, sticky="ew", pady=6)
        cell.grid_columnconfigure(0, weight=1)

        if widget_left and widget_right:
            widget_left.grid(row=0, column=0, sticky="ew")
            ttk.Label(cell, text=" ").grid(row=0, column=1)  # espaçador
            widget_right.grid(row=0, column=2, sticky="w")
        elif widget_left:
            widget_left.grid(row=0, column=0, sticky="ew")
        elif widget_right:
            widget_right.grid(row=0, column=0, sticky="w")

        self._row += 1
        return cell

    def add_actions(self, on_ok, ok_text="Salvar"):
        self._ok_callback = on_ok
        bar = ttk.Frame(self, style="Card.TFrame")
        bar.grid(row=self._row, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        ttk.Button(bar, text="Cancelar", command=self.win.destroy).pack(side=tk.RIGHT)
        ttk.Button(bar, text=ok_text, style="Accent.TButton", command=on_ok).pack(side=tk.RIGHT, padx=8)


# dialogs.py — SUBSTITUIR APENAS A CLASSE TaskDialog
from widgets import PlaceholderEntry, TagInput
from tags_repo import TagsRepo

# dialogs.py — TaskDialog robusto (com fallback de tags)
from widgets import PlaceholderEntry, TagInput  # garante estes imports
from tags_repo import TagsRepo
import tkinter as tk
from tkinter import ttk, messagebox
import datetime as dt

class TaskDialog(Modal):
    PRI_COLORS = {1: "#F87171", 2: "#FBBF24", 3: "#34D399"}

    def __init__(self, parent, initial=None):
        super().__init__(parent, "Nova/Editar Tarefa")
        data = initial or {}
        self.title_var = tk.StringVar(value=data.get("title", ""))
        self.date_var  = tk.StringVar(value=data.get("scheduled") or "")
        self.pri_var   = tk.IntVar(value=int(data.get("priority", 2)))

        # ---------- FORM ----------
        form = ttk.Frame(self, style="Card.TFrame")
        form.grid(row=self._row, column=0, columnspan=2, sticky="nsew")
        self._row += 1
        form.grid_columnconfigure(0, weight=0)   # labels
        form.grid_columnconfigure(1, weight=1)   # campos
        form.grid_columnconfigure(2, weight=0)   # extras (📅)

        PADX = (6, 12); PADY = 6

        # Título
        ttk.Label(form, text="Título:").grid(row=0, column=0, padx=PADX, pady=(0, PADY), sticky="w")
        e_title = PlaceholderEntry(form, textvariable=self.title_var, width=52,
                                   placeholder="Ex.: Estudar Java Cap. 3")
        e_title.grid(row=0, column=1, columnspan=2, padx=PADX, pady=(0, PADY), sticky="ew")
        e_title.focus_set()

        # Prioridade + badge
        ttk.Label(form, text="Prioridade:").grid(row=1, column=0, padx=PADX, pady=PADY, sticky="w")
        pri_box = ttk.Frame(form, style="Card.TFrame")
        pri_box.grid(row=1, column=1, padx=PADX, pady=PADY, sticky="w")

        self.badge = tk.Canvas(form, width=22, height=22, highlightthickness=0, bd=0)
        self.badge.grid(row=1, column=2, padx=(0, 10), pady=PADY, sticky="e")

        def paint_badge():
            col = self.PRI_COLORS.get(self.pri_var.get(), "#9CA3AF")
            self.badge.delete("all")
            self.badge.create_oval(4, 4, 18, 18, fill=col, width=0)

        for val, txt in [(1, "1 — Alta"), (2, "2 — Média"), (3, "3 — Baixa")]:
            ttk.Radiobutton(pri_box, text=txt, value=val, variable=self.pri_var,
                            command=paint_badge).pack(side=tk.LEFT, padx=(0,8))
        paint_badge()

        # Tags (robusto: tenta TagInput; se falhar, usa Entry)
        ttk.Label(form, text="Tags:").grid(row=2, column=0, padx=PADX, pady=PADY, sticky="nw")
        self.tags_widget = None
        self.tags_fallback = None
        try:
            self.tags_widget = TagInput(form, initial=data.get("tags", []), repo=TagsRepo())
            self.tags_widget.grid(row=2, column=1, columnspan=2, padx=PADX, pady=PADY, sticky="ew")
        except Exception as e:
            # fallback seguro
            self.tags_fallback = PlaceholderEntry(form, width=52, placeholder="ex.: estudo, java, prova")
            # se veio tags iniciais, mostra
            if data.get("tags"):
                self.tags_fallback.insert(0, ", ".join(data.get("tags")))
            self.tags_fallback.grid(row=2, column=1, columnspan=2, padx=PADX, pady=PADY, sticky="ew")
            print("[TaskDialog] TagInput falhou, usando fallback:", e)

        # Data + calendário
        ttk.Label(form, text="Data (YYYY-MM-DD):").grid(row=3, column=0, padx=PADX, pady=PADY, sticky="w")
        e_date = PlaceholderEntry(form, textvariable=self.date_var, width=18, placeholder="opcional")
        e_date.grid(row=3, column=1, padx=PADX, pady=PADY, sticky="w")
        ttk.Button(form, text="📅", width=3, command=self.open_calendar)\
            .grid(row=3, column=2, padx=(0, 10), pady=PADY, sticky="w")

        # Ações
        self.add_actions(self.on_ok, ok_text="Salvar")

    # ---- calendário ----
    def open_calendar(self):
        init = None
        try:
            if self.date_var.get().strip():
                y, m, d = map(int, self.date_var.get().split("-"))
                init = dt.date(y, m, d)
        except Exception:
            init = None
        CalendarPopup(self.win, on_pick=self._set_date, initial=init)

    def _set_date(self, s: str):
        self.date_var.set(s)

    # ---- salvar ----
    def on_ok(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Tarefa", "O título é obrigatório.")
            return
        date_txt = self.date_var.get().strip()
        if date_txt:
            try:
                dt.datetime.strptime(date_txt, "%Y-%m-%d")
            except Exception:
                messagebox.showwarning("Data inválida", "Use YYYY-MM-DD ou escolha no calendário.")
                return

        # pega tags tanto do TagInput quanto do fallback
        if self.tags_widget is not None:
            tags = self.tags_widget.get_tags()
        else:
            val = getattr(self, "tags_fallback", None)
            txt = val.get_value() if hasattr(val, "get_value") else (val.get() if val else "")
            tags = [t.strip() for t in (txt or "").split(",") if t.strip()]

        self.result = {
            "title": title,
            "priority": int(self.pri_var.get()),
            "tags": tags,
            "scheduled": date_txt or None
        }
        try:
            TagsRepo().add_many(tags)
        except Exception:
            pass
        self.win.destroy()


class DeckDialog(Modal):
    def __init__(self, parent, initial=None):
        super().__init__(parent, "Novo Baralho")
        name = (initial or {}).get("name", "")
        self.name_var = tk.StringVar(value=name)
        self.add_row("Nome do baralho:", ttk.Entry(self, textvariable=self.name_var, width=32))
        self.add_actions(self.on_ok)

    def on_ok(self):
        self.result = {"name": self.name_var.get().strip()}
        self.win.destroy()

class CardDialog(Modal):
    def __init__(self, parent, initial=None):
        super().__init__(parent, "Novo Cartão")
        front = (initial or {}).get("front", "")
        back  = (initial or {}).get("back", "")
        self.front_var = tk.StringVar(value=front)
        self.back_var  = tk.StringVar(value=back)
        self.add_row("Frente:", ttk.Entry(self, textvariable=self.front_var, width=48))
        self.add_row("Verso:",  ttk.Entry(self, textvariable=self.back_var,  width=48))
        self.add_actions(self.on_ok)

    def on_ok(self):
        self.result = {"front": self.front_var.get().strip(),
                       "back":  self.back_var.get().strip()}
        self.win.destroy()

# dialogs.py (SUBSTITUIR ESTA CLASSE)
class CalendarPopup(tk.Toplevel):
    """Popover de calendário: escolhe uma data e retorna YYYY-MM-DD."""
    WEEKDAYS = ["D", "S", "T", "Q", "Q", "S", "S"]  # dom..sáb

    def __init__(self, parent, on_pick, initial=None):
        super().__init__(parent)
        self.title("Selecionar Data")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        today = dt.date.today()
        self.year = initial.year if isinstance(initial, dt.date) else today.year
        self.month = initial.month if isinstance(initial, dt.date) else today.month
        self.on_pick = on_pick

        root = ttk.Frame(self, style="Card.TFrame")
        root.pack(padx=10, pady=10)

        # Navegação de mês/ano
        nav = ttk.Frame(root, style="Card.TFrame"); nav.pack(fill="x", pady=(0, 6))
        ttk.Button(nav, text="◀", width=3, command=self.prev_month).pack(side=tk.LEFT)
        self.title_lbl = ttk.Label(nav, text="", style="Header.TLabel")
        self.title_lbl.pack(side=tk.LEFT, expand=True)
        ttk.Button(nav, text="▶", width=3, command=self.next_month).pack(side=tk.LEFT)

        # Grid de dias
        self.grid_days = ttk.Frame(root, style="Card.TFrame"); self.grid_days.pack()

        # ações rápidas
        quick = ttk.Frame(root, style="Card.TFrame"); quick.pack(fill="x", pady=(8, 0))
        ttk.Button(quick, text="Hoje",  command=lambda: self.pick(today)).pack(side=tk.LEFT)
        ttk.Button(quick, text="Limpar", command=lambda: self.pick(None)).pack(side=tk.LEFT, padx=6)

        self.draw()

    def prev_month(self):
        self.month -= 1
        if self.month == 0:
            self.month, self.year = 12, self.year - 1
        self.draw()

    def next_month(self):
        self.month += 1
        if self.month == 13:
            self.month, self.year = 1, self.year + 1
        self.draw()

    def draw(self):
        for w in self.grid_days.winfo_children(): w.destroy()
        name = calendar.month_name[self.month]
        self.title_lbl.configure(text=f"{name} {self.year}")

        for i, wd in enumerate(self.WEEKDAYS):
            ttk.Label(self.grid_days, text=wd).grid(row=0, column=i, padx=4, pady=2)

        cal = calendar.monthcalendar(self.year, self.month)
        today = dt.date.today()

        for r, week in enumerate(cal, start=1):
            for c, day in enumerate(week):
                if day == 0:
                    ttk.Label(self.grid_days, text=" ").grid(row=r, column=c, padx=2, pady=2)
                    continue
                d = dt.date(self.year, self.month, day)
                btn = ttk.Button(self.grid_days, text=f"{day:02}", width=4,
                                 command=lambda dd=d: self.pick(dd))
                if d == today:
                    btn.configure(style="Accent.TButton")
                btn.grid(row=r, column=c, padx=2, pady=2)

    def pick(self, date_obj: dt.date | None):
        if date_obj is None:
            self.on_pick("")  # limpar campo
        else:
            self.on_pick(date_obj.strftime("%Y-%m-%d"))
        self.destroy()


    def pick(self, date_obj: dt.date):
        self.on_pick(date_obj.strftime("%Y-%m-%d"))
        self.destroy()


# dialogs.py — AvatarPicker (modal de seleção em grade)
import tkinter as tk
from tkinter import ttk

class AvatarPicker(ttk.Frame):
    def __init__(self, parent, profile_repo):
        self.win = tk.Toplevel(parent)
        self.win.title("Escolher Avatar")
        self.win.transient(parent); self.win.grab_set()
        self.win.resizable(False, False)

        super().__init__(self.win, style="Card.TFrame")
        self.pack(padx=12, pady=12, fill=tk.BOTH, expand=True)

        ttk.Label(self, text="Escolha um avatar", style="Header.TLabel").pack(anchor="w", pady=(0,8))

        grid = ttk.Frame(self, style="Card.TFrame"); grid.pack()
        inv = profile_repo.data.get("avatar_inventory", [])
        self.result = None

        if not inv:
            ttk.Label(grid, text="Sem avatares no inventário.").pack()
        else:
            for i, e in enumerate(inv):
                ttk.Button(grid, text=e, width=3,
                           command=lambda em=e: self._pick(em)).grid(row=i//12, column=i%12, padx=3, pady=3)

        bar = ttk.Frame(self, style="Card.TFrame"); bar.pack(fill=tk.X, pady=(12,0))
        ttk.Button(bar, text="Cancelar", command=self.win.destroy).pack(side=tk.RIGHT)

    def _pick(self, emoji):
        self.result = emoji
        self.win.destroy()
