# pomodoro_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
from fsm import PomodoroFSM
from widgets import CircularProgress, CoinFloat
from storage import StatsRepo

class PomodoroTab(ttk.Frame):
    def __init__(self, parent, profile):
        super().__init__(parent)
        self.profile = profile
        self.fsm = PomodoroFSM()  # 25/5/15 padrão
        self.stats = StatsRepo()
        self._timer = None
        self._focus_seconds = self.fsm.focus
        self.streak = 0  # pomodoros concluídos seguidos no dia

        header = ttk.Frame(self); header.pack(pady=6, fill=tk.X)
        ttk.Label(header, text="Pomodoro", style="Header.TLabel").pack(side=tk.LEFT, padx=8)
        self.streak_lbl = ttk.Label(header, text="Streak: 0"); self.streak_lbl.pack(side=tk.LEFT, padx=8)

        self.lbl = ttk.Label(self, text="Foco 25:00"); self.lbl.pack(pady=4)
        self.progress = CircularProgress(self, size=220)
        self.progress.pack(pady=10)

        bar = ttk.Frame(self); bar.pack()
        ttk.Button(bar, text="▶ Iniciar", style="Accent.TButton", command=self.start).pack(side=tk.LEFT, padx=4)
        ttk.Button(bar, text="⏸ Pausar", command=self.pause).pack(side=tk.LEFT, padx=4)
        ttk.Button(bar, text="⟲ Reset", command=self.reset).pack(side=tk.LEFT, padx=4)

    # --------- controles ---------
    def start(self):
        self.fsm.start()
        if self._timer: self.after_cancel(self._timer)
        self._tick()

    def pause(self):
        if self._timer: self.after_cancel(self._timer); self._timer=None
        self.fsm.pause()

    def reset(self):
        if self._timer: self.after_cancel(self._timer); self._timer=None
        self.fsm.reset(); self._render()

    # --------- loop ---------
    def _tick(self):
        self._render()
        done_focus = self.fsm.tick()
        if done_focus:
            # recompensa pelo foco concluído
            self.streak += 1
            self.streak_lbl.configure(text=f"Streak: {self.streak}")
            self.profile.add_rewards(coins=10, xp=10)
            CoinFloat.show(self.winfo_toplevel(), "+10 🪙", near_widget=self.progress, offset=(0, -20))

            # estatística de minutos focados
            focus_minutes = int(self._focus_seconds/60)
            self.stats.add_focus_minutes(focus_minutes)

            # badges
            self._check_badges()

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

        # reset streak quando entra em LONG_BREAK (opcional manter), aqui mantemos streak corrida do dia
        # if self.fsm.state == "LONG_BREAK": self.streak = 0

    def _check_badges(self):
        bd = self.profile.data.setdefault("badges", [])
        earned = []
        if self.streak >= 3 and "3 Pomodoros seguidos" not in bd:
            bd.append("3 Pomodoros seguidos"); earned.append("🏆 3 Pomodoros seguidos")
        if self.streak >= 10 and "Streak 10+" not in bd:
            bd.append("Streak 10+"); earned.append("🔥 Streak 10+")
        if earned:
            self.profile._save()
            messagebox.showinfo("Conquista!", "Você ganhou:\n• " + "\n• ".join(earned))
