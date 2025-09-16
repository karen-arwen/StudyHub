# profile_tab.py — Perfil 2.0 (sem export/import)
import tkinter as tk
from tkinter import ttk, messagebox
from widgets import CircularProgress
from theme import Theme
from badges import BadgeEngine
from dialogs import AvatarPicker  # classe nova do item 2

DEFAULT_STARTER = "🌸"

class ProfileTab(ttk.Frame):
    def __init__(self, parent, profile_repo):
        super().__init__(parent)
        self.repo = profile_repo
        self.badges = BadgeEngine(self.repo)

        inv = self.repo.data.setdefault("avatar_inventory", [])
        if not inv:
            inv.append(DEFAULT_STARTER)
        self.repo.data.setdefault("avatar_skin", inv[0])
        self.repo.data.setdefault("learning", "Java, Redes, POO")
        self.repo.data.setdefault("badges", [])
        self.repo.data.setdefault("coins", 0)
        self.repo.data.setdefault("level", 1)
        self.repo.data.setdefault("xp", 0)
        self.repo._save()

        # ===== Header com gradiente (Canvas) =====
        # (Sem header local — usamos o header global do App)
        spacer = ttk.Frame(self)
        spacer.pack(fill=tk.X)
        spacer.configure(height=8)
        spacer.pack_propagate(False)


        # ===== Card principal =====
        card = ttk.Frame(self, style="Card.TFrame"); card.pack(padx=12, pady=(8,10), fill=tk.X)

        # Linha 1: Avatar + Nome + Meta
        row1 = ttk.Frame(card, style="Card.TFrame"); row1.pack(fill=tk.X, padx=12, pady=10)

        # Avatar grande + botões
        left = ttk.Frame(row1, style="Card.TFrame"); left.pack(side=tk.LEFT, padx=(0,16))
        self.avatar_lbl = ttk.Label(left, text=self.cur_avatar(), font=("Segoe UI Emoji", 62))
        self.avatar_lbl.pack()
        btns = ttk.Frame(left, style="Card.TFrame"); btns.pack(pady=6)
        ttk.Button(btns, text="Trocar avatar…", style="Accent.TButton", command=self.open_avatar_picker).pack(side=tk.LEFT)
        ttk.Button(btns, text="Aleatório", command=self.random_avatar).pack(side=tk.LEFT, padx=6)

        # Nome + meta
        mid = ttk.Frame(row1, style="Card.TFrame"); mid.pack(side=tk.LEFT, expand=True, fill=tk.X)
        title = ttk.Label(mid, text="Meu Perfil", style="Header.TLabel"); title.pack(anchor="w")
        name_row = ttk.Frame(mid); name_row.pack(anchor="w", pady=(8,4))
        ttk.Label(name_row, text="Nome:").pack(side=tk.LEFT)
        self.name_var = tk.StringVar(value=self.repo.data.get("name","Usuário"))
        e = ttk.Entry(name_row, textvariable=self.name_var, width=24); e.pack(side=tk.LEFT, padx=6)
        ttk.Button(name_row, text="Salvar", command=self.save_name).pack(side=tk.LEFT)

        self.meta_lbl = ttk.Label(mid, text=self.meta_text(), style="Sub.TLabel")
        self.meta_lbl.pack(anchor="w")

        # Level progress
        prog = ttk.Frame(card, style="Card.TFrame"); prog.pack(fill=tk.X, padx=12, pady=(0,12))
        self.cp = CircularProgress(prog, size=180); self.cp.pack(side=tk.LEFT)
        info_col = ttk.Frame(prog, style="Card.TFrame"); info_col.pack(side=tk.LEFT, padx=14)
        self.cp.set_progress(min(0.99, self.repo.data.get("xp",0)/100))
        self.cp.set_time_text(f"XP {self.repo.data.get('xp',0)}/100")
        ttk.Label(info_col, text="Progresso para o próximo nível", style="Sub.TLabel").pack(anchor="w", pady=(8,0))
        ttk.Label(info_col, text="Ganhe XP concluindo tarefas, estudando flashcards e jogando.", wraplength=380).pack(anchor="w")

        # “O que estou aprendendo”
        learn = ttk.Labelframe(self, text="O que estou aprendendo")
        learn.pack(fill=tk.X, padx=12, pady=(0,10))
        self.learn_var = tk.StringVar(value=self.repo.data.get("learning"))
        ttk.Entry(learn, textvariable=self.learn_var).pack(side=tk.LEFT, padx=6, pady=6, fill=tk.X, expand=True)
        ttk.Button(learn, text="Salvar", style="Accent.TButton", command=self.save_learning).pack(side=tk.LEFT, padx=6)

        # Inventário de avatares (mini-grid)
        inv_box = ttk.Labelframe(self, text="Avatares desbloqueados"); inv_box.pack(fill=tk.X, padx=12, pady=(0,10))
        self.inv_frame = ttk.Frame(inv_box); self.inv_frame.pack(fill=tk.X, padx=8, pady=6)

        # Badges (conquistas)
        bad_box = ttk.Labelframe(self, text="Conquistas"); bad_box.pack(fill=tk.X, padx=12, pady=(0,10))
        self.badges_frame = ttk.Frame(bad_box, style="Card.TFrame"); self.badges_frame.pack(fill=tk.X, padx=8, pady=6)

        # barra superior direita com "Atualizar"
        topbar = ttk.Frame(self); topbar.place(relx=1.0, y=8, anchor="ne")
        ttk.Button(topbar, text="Atualizar", command=self.refresh).pack()

        self.refresh()

    # ===== helpers =====

    def cur_avatar(self):
        return self.repo.data.get("avatar_skin", DEFAULT_STARTER)

    def meta_text(self):
        coins = self.repo.data.get("coins",0)
        lvl = self.repo.data.get("level",1)
        xp = self.repo.data.get("xp",0)
        return f"Nível {lvl} • XP {xp}/100 • Moedas {coins}"

    def _render_inventory(self):
        for w in self.inv_frame.winfo_children(): w.destroy()
        inv = self.repo.data.get("avatar_inventory", [])
        if not inv:
            ttk.Label(self.inv_frame, text="Sem avatares. Compre na Loja!").pack()
            return
        for i, emoji in enumerate(inv):
            ttk.Button(self.inv_frame, text=emoji, width=3,
                       command=lambda e=emoji: self.set_avatar(e)).grid(row=i//16, column=i%16, padx=2, pady=2)

    def _render_badges(self):
        for w in self.badges_frame.winfo_children(): w.destroy()
        got = set(self.repo.data.get("badges", []))
        pool = self.badges.all_badges()

        if not pool:
            ttk.Label(self.badges_frame, text="(Sem conquistas ainda)").pack()
            return

        for i, b in enumerate(pool):
            owned = b["key"] in got
            txt = f'{b["icon"]} {b["name"]}'
            style = "Accent.TButton" if owned else "TButton"
            btn = ttk.Button(self.badges_frame, text=txt, style=style)
            btn.grid(row=i//6, column=i%6, padx=4, pady=4, sticky="w")

    # ===== actions =====
    def set_avatar(self, emoji):
        self.repo.data["avatar_skin"] = emoji
        self.repo._save(); self.refresh()

    def random_avatar(self):
        inv = self.repo.data.get("avatar_inventory", [])
        if not inv:
            messagebox.showinfo("Avatar", "Sem avatares no inventário.")
            return
        import random
        self.set_avatar(random.choice(inv))

    def save_name(self):
        self.repo.data["name"] = self.name_var.get().strip() or "Usuário"
        self.repo._save(); self.refresh()

    def save_learning(self):
        self.repo.data["learning"] = self.learn_var.get().strip()
        self.repo._save(); self.refresh()

    def open_avatar_picker(self):
        dlg = AvatarPicker(self, self.repo)
        self.wait_window(dlg.win)
        if dlg.result:
            self.set_avatar(dlg.result)

    def refresh(self):
        self.avatar_lbl.configure(text=self.cur_avatar())
        self.meta_lbl.configure(text=self.meta_text())
        xp = self.repo.data.get("xp",0)
        self.cp.set_progress(min(0.99, xp/100))
        self.cp.set_time_text(f"XP {xp}/100")
        self._render_inventory()
        self._render_badges()
