# pomodoro_tab.py
# Este arquivo implementa a aba "Pomodoro" do aplicativo, onde os usuários podem gerenciar sessões de foco e pausas utilizando a técnica Pomodoro.
# Ele utiliza o tkinter para criar a interface gráfica e interage com o repositório de estatísticas e perfil para registrar progresso e recompensas.

# Importações necessárias para a interface gráfica e funcionalidades adicionais
import tkinter as tk
from tkinter import ttk, messagebox
from fsm import PomodoroFSM  # Máquina de estados finitos para gerenciar o ciclo Pomodoro
from widgets import CircularProgress, CoinFloat  # CircularProgress exibe o progresso visualmente, CoinFloat exibe animações de moedas
from storage import StatsRepo  # StatsRepo gerencia os dados estatísticos do usuário

# Classe principal que representa a aba "Pomodoro"
class PomodoroTab(ttk.Frame):
    def __init__(self, parent, profile):
        super().__init__(parent)
        self.profile = profile  # Repositório de perfil do usuário
        self.fsm = PomodoroFSM()  # Máquina de estados para gerenciar o ciclo Pomodoro (25/5/15 padrão)
        self.stats = StatsRepo()  # Repositório de estatísticas para registrar minutos focados
        self._timer = None  # Referência ao temporizador ativo
        self._focus_seconds = self.fsm.focus  # Duração da sessão de foco em segundos
        self.streak = 0  # Contador de pomodoros concluídos consecutivamente no dia

        # === Cabeçalho ===
        # Contém o título "Pomodoro" e o contador de streaks
        header = ttk.Frame(self); header.pack(pady=6, fill=tk.X)
        ttk.Label(header, text="Pomodoro", style="Header.TLabel").pack(side=tk.LEFT, padx=8)
        self.streak_lbl = ttk.Label(header, text="Streak: 0"); self.streak_lbl.pack(side=tk.LEFT, padx=8)

        # === Progresso e tempo restante ===
        self.lbl = ttk.Label(self, text="Foco 25:00"); self.lbl.pack(pady=4)
        self.progress = CircularProgress(self, size=220)  # Widget circular para exibir o progresso
        self.progress.pack(pady=10)

        # === Barra de controle ===
        # Contém botões para iniciar, pausar e resetar o ciclo Pomodoro
        bar = ttk.Frame(self); bar.pack()
        ttk.Button(bar, text="▶ Iniciar", style="Accent.TButton", command=self.start).pack(side=tk.LEFT, padx=4)
        ttk.Button(bar, text="⏸ Pausar", command=self.pause).pack(side=tk.LEFT, padx=4)
        ttk.Button(bar, text="⟲ Reset", command=self.reset).pack(side=tk.LEFT, padx=4)

    # --------- controles ---------
    # Inicia o ciclo Pomodoro
    def start(self):
        self.fsm.start()  # Altera o estado da máquina para "FOCUS"
        if self._timer: self.after_cancel(self._timer)  # Cancela o temporizador anterior, se existir
        self._tick()  # Inicia o loop do temporizador

    # Pausa o ciclo Pomodoro
    def pause(self):
        if self._timer: self.after_cancel(self._timer); self._timer=None  # Cancela o temporizador
        self.fsm.pause()  # Altera o estado da máquina para "PAUSED"

    # Reseta o ciclo Pomodoro
    def reset(self):
        if self._timer: self.after_cancel(self._timer); self._timer=None  # Cancela o temporizador
        self.fsm.reset(); self._render()  # Reseta a máquina de estados e atualiza a interface

    # --------- loop ---------
    # Loop principal do temporizador, executado a cada segundo
    def _tick(self):
        self._render()  # Atualiza a interface com o estado atual
        done_focus = self.fsm.tick()  # Avança o estado da máquina e verifica se o foco foi concluído
        if done_focus:
            # Recompensa pelo foco concluído
            self.streak += 1  # Incrementa o contador de streaks
            self.streak_lbl.configure(text=f"Streak: {self.streak}")  # Atualiza o texto do streak
            self.profile.add_rewards(coins=10, xp=10)  # Adiciona recompensas ao perfil do usuário
            CoinFloat.show(self.winfo_toplevel(), "+10 🪙", near_widget=self.progress, offset=(0, -20))  # Animação de moedas

            # Estatística de minutos focados
            focus_minutes = int(self._focus_seconds/60)  # Converte segundos de foco para minutos
            self.stats.add_focus_minutes(focus_minutes)  # Registra os minutos focados

            # Verifica e concede badges (conquistas)
            self._check_badges()

        self._timer = self.after(1000, self._tick)  # Agenda a próxima execução do loop em 1 segundo

    # Atualiza a interface com o estado atual do ciclo Pomodoro
    def _render(self):
        mins, secs = divmod(self.fsm.remaining, 60)  # Calcula minutos e segundos restantes
        if self.fsm.state == "FOCUS":
            ratio = 1 - (self.fsm.remaining / self._focus_seconds)  # Progresso da sessão de foco
        else:
            ratio = 1 - (self.fsm.remaining / (self.fsm.long if self.fsm.state=="LONG_BREAK" else self.fsm.short))  # Progresso da pausa
        self.progress.set_progress(max(0.0, min(1.0, ratio)))  # Atualiza o progresso visual
        self.progress.set_time_text(f"{mins:02}:{secs:02}")  # Atualiza o texto do tempo restante
        self.lbl.configure(text=f"{self.fsm.state.replace('_',' ').title()} — {mins:02}:{secs:02}")  # Atualiza o texto do estado atual

        # Reset opcional do streak ao entrar em LONG_BREAK (aqui mantemos o streak do dia)
        # if self.fsm.state == "LONG_BREAK": self.streak = 0

    # Verifica e concede badges (conquistas) com base no streak atual
    def _check_badges(self):
        bd = self.profile.data.setdefault("badges", [])  # Obtém ou inicializa a lista de badges
        earned = []  # Lista de badges conquistados nesta verificação
        if self.streak >= 3 and "3 Pomodoros seguidos" not in bd:
            bd.append("3 Pomodoros seguidos"); earned.append("🏆 3 Pomodoros seguidos")
        if self.streak >= 10 and "Streak 10+" not in bd:
            bd.append("Streak 10+"); earned.append("🔥 Streak 10+")
        if earned:
            self.profile._save()  # Salva as conquistas no perfil
            messagebox.showinfo("Conquista!", "Você ganhou:\n• " + "\n• ".join(earned))  # Exibe mensagem de conquista
