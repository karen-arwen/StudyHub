# studyhub.py
# Importa o módulo tkinter para criar interfaces gráficas e ttk para widgets estilizados
import tkinter as tk
from tkinter import ttk

# Importa módulos e classes auxiliares do projeto
from theme import Theme  # Gerencia temas visuais do aplicativo
from utils import ensure_data_dirs, init_default_files  # Funções utilitárias para inicializar diretórios e arquivos padrão
from storage import ProfileRepo, TaskRepo  # Repositórios para persistência de dados de perfil e tarefas
from tasks_tab import TasksTab  # Aba de tarefas e hábitos
from pomodoro_tab import PomodoroTab  # Aba de Pomodoro
from flashcards_tab import FlashcardsTab  # Aba de flashcards
from reports_tab import ReportsTab  # Aba de relatórios
from shop_tab import ShopTab  # Aba de loja
from profile_tab import ProfileTab  # Aba de perfil
from games_tab import GamesTab  # Aba de jogos

# Classe principal do aplicativo
class App(tk.Tk):
    def __init__(self):
        super().__init__()  # Inicializa a classe base Tk
        self.title("StudyHub — Produtividade + Estudos + Games")  # Define o título da janela principal
        self.geometry("1200x780")  # Define o tamanho inicial da janela
        Theme.apply(self, "princess")  # Aplica o tema inicial "princess"

        # Header decorativo com título, subtítulo e seletor de tema
        header = Theme.header(self, title="StudyHub", subtitle="produtividade • estudos • games")
        # Barra de ações no header (à direita)
        hdr_bar = ttk.Frame(self)
        hdr_bar.place(in_=header, relx=1.0, rely=0.5, x=-12, y=-16, anchor="e")
        # Botões para alternar entre temas visuais
        ttk.Button(hdr_bar, text="Princess", style="Accent.TButton",
                   command=lambda: self._switch_theme("princess")).pack(side=tk.LEFT, padx=2)
        ttk.Button(hdr_bar, text="Dark",
                   command=lambda: self._switch_theme("dark")).pack(side=tk.LEFT, padx=2)
        ttk.Button(hdr_bar, text="Neon",
                   command=lambda: self._switch_theme("neon")).pack(side=tk.LEFT, padx=2)

        # Inicializa os repositórios de dados para persistência
        self.profile = ProfileRepo()  # Repositório para dados de perfil
        self.tasks = TaskRepo()  # Repositório para dados de tarefas

        # Cria um widget Notebook para gerenciar abas
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill=tk.BOTH, expand=True)  # Expande o notebook para preencher a janela

        # Adiciona as abas ao notebook
        self.tab_profile = ProfileTab(self.nb, self.profile)  # Aba de perfil
        self.nb.add(self.tab_profile, text="👤 Perfil")

        self.tab_tasks = TasksTab(self.nb, self.tasks, self.profile)  # Aba de tarefas e hábitos
        self.nb.add(self.tab_tasks, text="✅ Tarefas & Hábitos")

        self.tab_pomo = PomodoroTab(self.nb, self.profile)  # Aba de Pomodoro
        self.nb.add(self.tab_pomo, text="⏳ Pomodoro")

        self.tab_flash = FlashcardsTab(self.nb, self.profile)  # Aba de flashcards
        self.nb.add(self.tab_flash, text="🧠 Flashcards")

        self.tab_reports = ReportsTab(self.nb, self.tasks)  # Aba de relatórios
        self.nb.add(self.tab_reports, text="📊 Relatórios")

        self.tab_shop = ShopTab(self.nb, self.profile)  # Aba de loja
        self.nb.add(self.tab_shop, text="🛍 Loja")

        self.tab_games = GamesTab(self.nb, self.profile)  # Aba de jogos
        self.nb.add(self.tab_games, text="🎮 Games")

    # Método para alternar o tema visual do aplicativo
    def _switch_theme(self, name: str):
        Theme.switch_theme(self, name)  # Aplica o tema especificado
        # Força pequenos refreshes nas abas para refletir o tema
        try: self.tab_profile.refresh()  # Atualiza a aba de perfil
        except: pass
        try: self.tab_tasks.refresh()  # Atualiza a aba de tarefas
        except: pass

# Ponto de entrada do aplicativo
if __name__ == "__main__":
    ensure_data_dirs()  # Garante que os diretórios de dados existam
    init_default_files()  # Inicializa arquivos padrão, se necessário
    App().mainloop()  # Inicia o loop principal do aplicativo
