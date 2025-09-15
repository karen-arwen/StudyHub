# studyhub.py
import tkinter as tk
from tkinter import ttk

import theme
from utils import ensure_data_dirs, init_default_files
from storage import ProfileRepo, TaskRepo
from tasks_tab import TasksTab
from pomodoro_tab import PomodoroTab
from flashcards_tab import FlashcardsTab
from reports_tab import ReportsTab
from shop_tab import ShopTab  # Loja como uma aba

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("StudyHub — Produtividade + Estudos + Games")
        self.geometry("1080x720")
        theme.apply(self)

        # Repositórios (persistência)
        self.profile = ProfileRepo()
        self.tasks = TaskRepo()

        # Notebook com as abas
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill=tk.BOTH, expand=True)

        self.tab_tasks = TasksTab(self.nb, self.tasks)
        self.nb.add(self.tab_tasks, text="✅ Tarefas & Hábitos")

        self.tab_pomo = PomodoroTab(self.nb, self.profile)
        self.nb.add(self.tab_pomo, text="⏳ Pomodoro")

        self.tab_flash = FlashcardsTab(self.nb, self.profile)
        self.nb.add(self.tab_flash, text="🧠 Flashcards")

        self.tab_reports = ReportsTab(self.nb, self.tasks)
        self.nb.add(self.tab_reports, text="📊 Relatórios")

        self.tab_shop = ShopTab(self.nb, self.profile)
        self.nb.add(self.tab_shop, text="🛍 Loja")

if __name__ == "__main__":
    ensure_data_dirs()
    init_default_files()  # cria JSONs se estiverem faltando
    App().mainloop()
