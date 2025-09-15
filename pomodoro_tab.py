# pomodoro_tab.py
import tkinter as tk
from tkinter import ttk
from widgets import CircularProgress  # <== corrigido
from fsm import PomodoroFSM
from storage import StatsRepo

class PomodoroTab(ttk.Frame):
    def __init__(self, parent, profile):
        super().__init__(parent)
        self.profile = profile
        self.fsm = PomodoroFSM()
        self.stats = StatsRepo()

        self.lbl = ttk.Label(self, text="Pomodoro — Foco 25:00")
        self.lbl.pack(pady=6)
        self.progress = CircularProgress(self, size=220)
        self.progress.pack(pady=10)

        bar = ttk.Frame(self); bar.pack()
        ttk.Button(bar, text="▶ Iniciar", style="Accent.TButton", command=self.start).pack(side=tk.LEFT, padx=4)
        ttk.Button(bar, text="⏸ Pausar", command=self.pause).pack(side=tk.LEFT, padx=4)
        ttk.Button(bar, text="⟲ Reset", command=self.reset).pack(side=tk.LEFT, padx=4)

        self._timer = None
        self._focus_seconds = self.fsm.focus

    def start(self):
        self.fsm.start(); self._tick()

    def pause(self):
        if self._timer: self.after_cancel(self._timer); self._timer=None
        self.fsm.pause()

    def reset(self):
        if self._timer: self.after_cancel(self._timer); self._timer=None
        self.fsm.reset(); self._render()

    def _tick(self):
        self._render()
        done_focus = self.fsm.tick()
        if done_focus:
            self.profile.add_rewards(coins=10, xp=10)
            focus_minutes = int(self._focus_seconds/60)
            self.stats.add_focus_minutes(focus_minutes)
        self._timer = self.after(1000, self._tick)

    def _render(self):
        mins, secs = divmod(self.fsm.remaining, 60)
        if self.fsm.state == "FOCUS":
            ratio = 1 - (self.fsm.remaining / self._focus_seconds)
        else:
            ratio = 1 - (self.fsm.remaining / (self.fsm.long if self.fsm.state=="LONG_BREAK" else self.fsm.short))
        self.progress.set_progress(max(0.0, min(1.0, ratio)))
        self.progress.set_time_text(f"{mins:02}:{secs:02}")
        self.lbl.configure(text=f"{self.fsm.state.replace('_',' ').title()} — {mins:02}:{secs:02}")
