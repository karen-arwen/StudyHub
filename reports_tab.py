# reports_tab.py
import tkinter as tk
from tkinter import ttk
from widgets import BarChart
from storage import StatsRepo
from theme import Theme

class ReportsTab(ttk.Frame):
    def __init__(self, parent, task_repo):
        super().__init__(parent)
        self.stats = StatsRepo()

        head = ttk.Frame(self); head.pack(fill=tk.X, pady=8)
        ttk.Label(head, text="Relatórios da Semana", style="Header.TLabel").pack(side=tk.LEFT, padx=8)
        ttk.Button(head, text="Atualizar", command=self.refresh).pack(side=tk.RIGHT, padx=8)

        # cartões para os gráficos
        card1 = ttk.Frame(self, style="Card.TFrame"); card1.pack(fill=tk.X, padx=12, pady=8)
        ttk.Label(card1, text="✅ Tarefas concluídas (últimos 7 dias)", style="Sub.TLabel").pack(anchor="w", padx=12, pady=6)
        self.chart_done = BarChart(card1, width=980, height=240)
        self.chart_done.pack(padx=12, pady=8)

        card2 = ttk.Frame(self, style="Card.TFrame"); card2.pack(fill=tk.X, padx=12, pady=8)
        ttk.Label(card2, text="⏳ Minutos de foco (últimos 7 dias)", style="Sub.TLabel").pack(anchor="w", padx=12, pady=6)
        self.chart_focus = BarChart(card2, width=980, height=240)
        self.chart_focus.pack(padx=12, pady=8)

        self.refresh()

    def refresh(self):
        days, done, focus = self.stats.last7()
        labels = [d[5:] for d in days]  # mm-dd
        pal = Theme.palette

        # cores seguras com fallback
        primary = pal.get("primary", pal.get("accent", "#7C3AED"))
        accent  = pal.get("accent", "#7C3AED")

        # desenha os gráficos
        self.chart_done.draw(done, labels, bar_fill=primary)
        self.chart_focus.draw(focus, labels, bar_fill=accent)

