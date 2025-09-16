# fsm.py
# Este arquivo implementa a máquina de estados finitos (FSM) para gerenciar o ciclo Pomodoro.
# A classe `PomodoroFSM` controla os estados de foco, pausas curtas e pausas longas, além de rastrear ciclos concluídos.

class PomodoroFSM:
    def __init__(self, focus=25*60, short=5*60, long=15*60):
        """
        Inicializa a máquina de estados com os tempos padrão para foco, pausa curta e pausa longa.
        
        Parâmetros:
        - focus: Duração da sessão de foco em segundos (padrão: 25 minutos).
        - short: Duração da pausa curta em segundos (padrão: 5 minutos).
        - long: Duração da pausa longa em segundos (padrão: 15 minutos).
        """
        self.focus, self.short, self.long = focus, short, long  # Define as durações dos estados
        self.state, self.remaining, self.cycles = "IDLE", focus, 0  # Estado inicial, tempo restante e ciclos concluídos

    def start(self):
        """
        Inicia o ciclo Pomodoro, alterando o estado para "FOCUS" e definindo o tempo restante para a duração do foco.
        """
        self.state, self.remaining = "FOCUS", self.focus

    def tick(self):
        """
        Avança a máquina de estados em 1 segundo. Gerencia as transições entre os estados.
        
        Retorna:
        - True: Se o estado atual foi concluído e houve uma transição (ex.: de "FOCUS" para "BREAK").
        - False: Se o estado atual ainda não foi concluído.
        """
        if self.state not in ("FOCUS", "BREAK", "LONG_BREAK"):  # Verifica se o estado é válido para contagem
            return False

        self.remaining -= 1  # Reduz o tempo restante em 1 segundo

        if self.remaining > 0:
            return False  # O estado atual ainda não foi concluído

        if self.state == "FOCUS":
            # Transição do estado "FOCUS" para "BREAK" ou "LONG_BREAK"
            self.cycles += 1  # Incrementa o número de ciclos concluídos
            if self.cycles % 4 == 0:
                self.state, self.remaining = "LONG_BREAK", self.long  # Após 4 ciclos, inicia uma pausa longa
            else:
                self.state, self.remaining = "BREAK", self.short  # Caso contrário, inicia uma pausa curta
            return True

        elif self.state in ("BREAK", "LONG_BREAK"):
            # Transição de "BREAK" ou "LONG_BREAK" de volta para "FOCUS"
            self.state, self.remaining = "FOCUS", self.focus
            return False