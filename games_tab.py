# games_tab.py
import tkinter as tk
from tkinter import ttk

class GamesTab(ttk.Frame):
    """
    Lista e abre os jogos desbloqueados (comprados na Loja).
    Espera profile_repo com .data['unlocked_games'].
    """
    def __init__(self, parent, profile_repo):
        super().__init__(parent)
        self.profile = profile_repo

        head = ttk.Frame(self); head.pack(fill=tk.X, pady=8)
        ttk.Label(head, text="Games", style="Header.TLabel").pack(side=tk.LEFT, padx=8)
        ttk.Button(head, text="Atualizar", command=self.refresh).pack(side=tk.RIGHT, padx=8)

        self.grid = ttk.Frame(self); self.grid.pack(fill=tk.BOTH, expand=True)
        self.refresh()

    def refresh(self):
        for w in self.grid.winfo_children(): w.destroy()
        unlocked = set(self.profile.data.get("unlocked_games", []))

        mapping = {
            "snake": ("games.snake", "play", "🐍 Snake"),
            "tictactoe": ("games.tictactoe", "play", "❌⭕ Jogo da Velha"),
            "quiz": ("games.quiz", "play", "❓ Quiz"),
            "memory": ("games.memory", "play", "🧠 Memory"),
        }

        if not unlocked:
            ttk.Label(self.grid, text="Nenhum jogo desbloqueado. Compre na Loja!").pack(pady=16)
            return

        for i, key in enumerate(sorted(unlocked)):
            if key not in mapping: continue
            modname, fn, label = mapping[key]
            def make_cmd(module=modname, func=fn):
                def _open():
                    mod = __import__(module, fromlist=[func])
                    getattr(mod, func)(self.profile)
                return _open
            card = ttk.Frame(self.grid, style="Card.TFrame")
            card.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="nsew")
            ttk.Label(card, text=label, style="Header.TLabel").pack(padx=12, pady=8)
            ttk.Button(card, text="Jogar", style="Accent.TButton", command=make_cmd()).pack(padx=12, pady=12)
