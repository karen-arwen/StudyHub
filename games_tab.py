# games_tab.py
# Este arquivo implementa a aba "Games" do aplicativo, onde os usuários podem acessar os jogos desbloqueados.
# Ele utiliza o tkinter para criar a interface gráfica e carrega dinamicamente os módulos dos jogos disponíveis.

import tkinter as tk
from tkinter import ttk

# Classe principal que representa a aba "Games"
class GamesTab(ttk.Frame):
    """
    Lista e abre os jogos desbloqueados (comprados na Loja).
    Espera profile_repo com .data['unlocked_games'].
    """
    def __init__(self, parent, profile_repo):
        super().__init__(parent)
        self.profile = profile_repo  # Repositório de perfil contendo os jogos desbloqueados

        # === Cabeçalho ===
        # Contém o título "Games" e um botão para atualizar a lista de jogos
        head = ttk.Frame(self); head.pack(fill=tk.X, pady=8)
        ttk.Label(head, text="Games", style="Header.TLabel").pack(side=tk.LEFT, padx=8)
        ttk.Button(head, text="Atualizar", command=self.refresh).pack(side=tk.RIGHT, padx=8)

        # === Área de jogos ===
        # Contém os cartões dos jogos desbloqueados
        self.grid = ttk.Frame(self); self.grid.pack(fill=tk.BOTH, expand=True)
        self.refresh()  # Atualiza a lista de jogos ao inicializar a aba

    # Atualiza a lista de jogos exibidos na aba
    def refresh(self):
        for w in self.grid.winfo_children(): w.destroy()  # Remove todos os widgets existentes na grade
        unlocked = set(self.profile.data.get("unlocked_games", []))  # Obtém os jogos desbloqueados do perfil

        # Mapeamento de jogos para seus módulos, funções e rótulos
        mapping = {
            "snake": ("games.snake", "play", "🐍 Snake"),
            "tictactoe": ("games.tictactoe", "play", "❌⭕ Jogo da Velha"),
            "quiz": ("games.quiz", "play", "❓ Quiz"),
            "memory": ("games.memory", "play", "🧠 Memory"),
        }

        # Exibe uma mensagem se nenhum jogo estiver desbloqueado
        if not unlocked:
            ttk.Label(self.grid, text="Nenhum jogo desbloqueado. Compre na Loja!").pack(pady=16)
            return

        # Cria cartões para cada jogo desbloqueado
        for i, key in enumerate(sorted(unlocked)):
            if key not in mapping: continue  # Ignora jogos que não estão no mapeamento
            modname, fn, label = mapping[key]  # Obtém o módulo, função e rótulo do jogo

            # Função para carregar e executar o jogo dinamicamente
            def make_cmd(module=modname, func=fn):
                def _open():
                    mod = __import__(module, fromlist=[func])  # Importa o módulo do jogo
                    getattr(mod, func)(self.profile)  # Executa a função do jogo passando o perfil do usuário
                return _open

            # Cria o cartão do jogo
            card = ttk.Frame(self.grid, style="Card.TFrame")
            card.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="nsew")  # Posiciona o cartão na grade
            ttk.Label(card, text=label, style="Header.TLabel").pack(padx=12, pady=8)  # Rótulo do jogo
            ttk.Button(card, text="Jogar", style="Accent.TButton", command=make_cmd()).pack(padx=12, pady=12)  # Botão para jogar
