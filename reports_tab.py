# reports_tab.py
# Este arquivo implementa a aba "Relatórios" do aplicativo, onde os usuários podem visualizar gráficos semanais de tarefas concluídas e minutos de foco.
# Ele utiliza o tkinter para criar a interface gráfica e interage com o repositório de estatísticas para obter os dados necessários.

# Importações necessárias para a interface gráfica e funcionalidades adicionais
import tkinter as tk
from tkinter import ttk
from widgets import BarChart  # BarChart é um widget personalizado para exibir gráficos de barras
from storage import StatsRepo  # StatsRepo gerencia os dados estatísticos do usuário
from theme import Theme  # Theme gerencia o tema visual do aplicativo

# Classe principal que representa a aba "Relatórios"
class ReportsTab(ttk.Frame):
    def __init__(self, parent, task_repo):
        super().__init__(parent)
        self.stats = StatsRepo()  # Repositório de estatísticas para obter dados semanais

        # === Cabeçalho ===
        # Contém o título "Relatórios da Semana" e um botão para atualizar os gráficos
        head = ttk.Frame(self); head.pack(fill=tk.X, pady=8)
        ttk.Label(head, text="Relatórios da Semana", style="Header.TLabel").pack(side=tk.LEFT, padx=8)
        ttk.Button(head, text="Atualizar", command=self.refresh).pack(side=tk.RIGHT, padx=8)

        # === Cartão para o gráfico de tarefas concluídas ===
        card1 = ttk.Frame(self, style="Card.TFrame"); card1.pack(fill=tk.X, padx=12, pady=8)
        ttk.Label(card1, text="✅ Tarefas concluídas (últimos 7 dias)", style="Sub.TLabel").pack(anchor="w", padx=12, pady=6)
        self.chart_done = BarChart(card1, width=980, height=240)  # Gráfico de barras para tarefas concluídas
        self.chart_done.pack(padx=12, pady=8)

        # === Cartão para o gráfico de minutos de foco ===
        card2 = ttk.Frame(self, style="Card.TFrame"); card2.pack(fill=tk.X, padx=12, pady=8)
        ttk.Label(card2, text="⏳ Minutos de foco (últimos 7 dias)", style="Sub.TLabel").pack(anchor="w", padx=12, pady=6)
        self.chart_focus = BarChart(card2, width=980, height=240)  # Gráfico de barras para minutos de foco
        self.chart_focus.pack(padx=12, pady=8)

        self.refresh()  # Atualiza os gráficos ao inicializar a aba

    # Método para atualizar os gráficos com os dados mais recentes
    def refresh(self):
        days, done, focus = self.stats.last7()  # Obtém os últimos 7 dias de dados
        labels = [d[5:] for d in days]  # Formata as datas no formato "mm-dd"
        pal = Theme.palette  # Obtém a paleta de cores do tema atual

        # Define cores seguras com valores padrão (fallback)
        primary = pal.get("primary", pal.get("accent", "#7C3AED"))  # Cor primária ou acento
        accent  = pal.get("accent", "#7C3AED")  # Cor de acento

        # Desenha os gráficos com os dados obtidos
        self.chart_done.draw(done, labels, bar_fill=primary)  # Gráfico de tarefas concluídas
        self.chart_focus.draw(focus, labels, bar_fill=accent)  # Gráfico de minutos de foco

