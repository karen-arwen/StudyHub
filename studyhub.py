# studyhub.py
import tkinter as tk
from tkinter import ttk

from theme import Theme
from utils import ensure_data_dirs, init_default_files
from storage import ProfileRepo, TaskRepo
from tasks_tab import TasksTab
from pomodoro_tab import PomodoroTab
from flashcards_tab import FlashcardsTab
from reports_tab import ReportsTab
from shop_tab import ShopTab
from profile_tab import ProfileTab
from games_tab import GamesTab


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("StudyHub — Produtividade + Estudos + Games")
        self.geometry("1200x780")
        Theme.apply(self, "princess")

        # Header decorativo + seletor de tema
        header = Theme.header(self, title="StudyHub", subtitle="produtividade • estudos • games")
        # barra de ações no header (à direita)
        hdr_bar = ttk.Frame(self)
        hdr_bar.place(in_=header, relx=1.0, rely=0.5, x=-12, y=-16, anchor="e")
        ttk.Button(hdr_bar, text="Princess", style="Accent.TButton",
                   command=lambda: self._switch_theme("princess")).pack(side=tk.LEFT, padx=2)
        ttk.Button(hdr_bar, text="Dark",
                   command=lambda: self._switch_theme("dark")).pack(side=tk.LEFT, padx=2)
        ttk.Button(hdr_bar, text="Neon",
                   command=lambda: self._switch_theme("neon")).pack(side=tk.LEFT, padx=2)

        # Persistência
        self.profile = ProfileRepo()
        self.tasks = TaskRepo()

        # Notebook
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill=tk.BOTH, expand=True)

        # Abas
        self.tab_profile = ProfileTab(self.nb, self.profile)
        self.nb.add(self.tab_profile, text="👤 Perfil")

        self.tab_tasks = TasksTab(self.nb, self.tasks, self.profile)
        self.nb.add(self.tab_tasks, text="✅ Tarefas & Hábitos")

        self.tab_pomo = PomodoroTab(self.nb, self.profile)
        self.nb.add(self.tab_pomo, text="⏳ Pomodoro")

        self.tab_flash = FlashcardsTab(self.nb, self.profile)
        self.nb.add(self.tab_flash, text="🧠 Flashcards")

        self.tab_reports = ReportsTab(self.nb, self.tasks)
        self.nb.add(self.tab_reports, text="📊 Relatórios")

        self.tab_shop = ShopTab(self.nb, self.profile)
        self.nb.add(self.tab_shop, text="🛍 Loja")

        self.tab_games = GamesTab(self.nb, self.profile)
        self.nb.add(self.tab_games, text="🎮 Games")

    def _switch_theme(self, name: str):
        Theme.switch_theme(self, name)
        # força pequenos refreshes nas abas para refletir o tema
        try: self.tab_profile.refresh()
        except: pass
        try: self.tab_tasks.refresh()
        except: pass


if __name__ == "__main__":
    ensure_data_dirs()
    init_default_files()
    App().mainloop()
