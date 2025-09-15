# reports_tab.py
import tkinter as tk
from tkinter import ttk
from widgets import BarChart  # <== corrigido
from storage import StatsRepo

class ReportsTab(ttk.Frame):
    def __init__(self, parent, repo):
        super().__init__(parent)
        self.stats = StatsRepo()
        ttk.Label(self, text="Estatísticas da Semana", style="Header.TLabel").pack(pady=6)
        self.chart_done = BarChart(self, width=680, height=220)
        self.chart_done.pack(pady=6)
        self.chart_focus = BarChart(self, width=680, height=220)
        self.chart_focus.pack(pady=6)
        ttk.Button(self, text="Atualizar", command=self.refresh).pack(pady=6)
        self.refresh()

    def refresh(self):
        days, done, focus = self.stats.last7()
        # Labels compactos (MM-DD)
        labels = [d[5:] for d in days]
        self.chart_done.draw(done, labels)
        self.chart_focus.draw(focus, labels)
