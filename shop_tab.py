# shop_tab.py
# Este arquivo implementa a aba "Loja" do aplicativo, onde os usuários podem comprar itens como temas, avatares, boosts e jogos.
# Ele utiliza o tkinter para criar a interface gráfica e interage com o repositório de perfil para gerenciar os dados do usuário.

# Importações necessárias para a interface gráfica e funcionalidades adicionais
import tkinter as tk
from tkinter import ttk, messagebox
from theme import Theme  # Gerencia os temas do aplicativo
from widgets import CoinFloat, ScrollableFrame  # CoinFloat exibe animações de moedas, ScrollableFrame cria áreas roláveis

# Lista de itens disponíveis na loja, cada item é representado como um dicionário com suas propriedades
SHOP_ITEMS = [
    {"key":"theme_princess","name":"Tema Princess","price":10, "type":"theme","theme":"princess"},
    {"key":"theme_dark","name":"Tema Dark","price":10, "type":"theme","theme":"dark"},
    {"key":"theme_neon","name":"Tema Neon","price":10, "type":"theme","theme":"neon"},
    {"key":"theme_cycle","name":"Tema Dinâmico (alternar rápido)","price":8,  "type":"theme_cycle"},
    {"key":"boost_x2","name":"Moedas x2 (sessão)","price":40, "type":"boost", "mult":2.0},
    {"key":"boost_x3","name":"Moedas x3 (sessão)","price":80, "type":"boost", "mult":3.0},
    {"key":"sound_pack","name":"Pacote de Sons","price":20, "type":"sound"},
    {"key":"avatar_unicorn","name":"Avatar: 🦄","price":15, "type":"avatar", "emoji":"🦄"},
    {"key":"avatar_fox","name":"Avatar: 🦊","price":15, "type":"avatar", "emoji":"🦊"},
    {"key":"avatar_panda","name":"Avatar: 🐼","price":15, "type":"avatar", "emoji":"🐼"},
    {"key":"pack_cute","name":"Pack Cute (🌸💜⭐🦋)","price":25, "type":"pack", "emojis":["🌸","💜","⭐","🦋"]},
    {"key":"pack_animals","name":"Pack Animais (🐱🐶🐻🐯)","price":25, "type":"pack", "emojis":["🐱","🐶","🐻","🐯"]},
    {"key":"game_tictactoe","name":"Desbloquear Jogo da Velha","price":25, "type":"game", "game":"tictactoe"},
    {"key":"game_memory","name":"Desbloquear Memory","price":25, "type":"game", "game":"memory"},
    {"key":"game_quiz","name":"Desbloquear Quiz","price":20, "type":"game", "game":"quiz"},
]

# Ordem dos temas para alternância dinâmica
THEME_ORDER = ["princess", "dark", "neon"]

# Classe principal que representa a aba "Loja"
class ShopTab(ttk.Frame):
    def __init__(self, parent, profile_repo):
        super().__init__(parent)
        self.profile = profile_repo  # Repositório de perfil para gerenciar os dados do usuário

        # === Barra superior ===
        # Contém o título "Loja", informações do usuário e botão de atualização
        top = ttk.Frame(self); top.pack(fill=tk.X, pady=6)
        ttk.Label(top, text="Loja", style="Header.TLabel").pack(side=tk.LEFT, padx=8)
        self.lbl = ttk.Label(top, text=self.meta_text()); self.lbl.pack(side=tk.RIGHT, padx=8)
        ttk.Button(top, text="Atualizar", command=self.refresh).pack(side=tk.RIGHT)

        # === Área rolável de itens ===
        # Exibe os itens da loja em um layout de grade dentro de uma área rolável
        self.scroll = ScrollableFrame(self, height=420)
        self.scroll.pack(fill=tk.BOTH, expand=True)
        grid = self.scroll.body

        # Adiciona os itens da loja como "cartões" na grade
        cols = 3  # Número de colunas na grade
        for i, it in enumerate(SHOP_ITEMS):
            card = ttk.Frame(grid, style="Card.TFrame")
            card.grid(row=i//cols, column=i%cols, padx=10, pady=10, sticky="nsew")
            ttk.Label(card, text=it["name"], style="Header.TLabel").pack(anchor="w", padx=12, pady=6)
            ttk.Label(card, text=f"Preço: {it['price']} 🪙").pack(anchor="w", padx=12)
            ttk.Button(card, text="Comprar", style="Accent.TButton",
                       command=lambda item=it: self.buy(item)).pack(padx=12, pady=8)

        # Configura as colunas da grade para serem elásticas
        for c in range(cols):
            grid.grid_columnconfigure(c, weight=1)

        # === Jogos rápidos (se desbloqueados) ===
        # Botões para acessar jogos desbloqueados, exibidos fora da área rolável
        sep = ttk.Label(self, text="Jogos", style="Header.TLabel"); sep.pack(pady=(8,6))
        btns = ttk.Frame(self); btns.pack(pady=(0,6))
        try:
            from games import snake, tictactoe, quiz, memory
            self.bt_snake = ttk.Button(btns, text="🐍 Snake", command=lambda: snake.play(self.profile))
            self.bt_ttt   = ttk.Button(btns, text="❌⭕ Jogo da Velha", command=lambda: tictactoe.play(self.profile))
            self.bt_quiz  = ttk.Button(btns, text="❓ Quiz", command=lambda: quiz.play(self.profile))
            self.bt_mem   = ttk.Button(btns, text="🧠 Memory", command=lambda: memory.play(self.profile))
            for b in (self.bt_snake, self.bt_ttt, self.bt_quiz, self.bt_mem): 
                b.pack(side=tk.LEFT, padx=6)
        except Exception:
            ttk.Label(self, text="(Módulos de jogos não encontrados)").pack()

        self.refresh_buttons()  # Atualiza o estado dos botões de jogos

    # Retorna o texto com informações do usuário (moedas e nível)
    def meta_text(self):
        return f"Moedas: {self.profile.data.get('coins',0)} • Nível: {self.profile.data.get('level',1)}"

    # Atualiza as informações exibidas na aba
    def refresh(self):
        self.lbl.configure(text=self.meta_text())  # Atualiza o texto com informações do usuário
        self.refresh_buttons()  # Atualiza o estado dos botões de jogos

    # Atualiza o estado (habilitado/desabilitado) dos botões de jogos com base nos jogos desbloqueados
    def refresh_buttons(self):
        unlocked = set(self.profile.data.get("unlocked_games", []))
        try:
            if hasattr(self, "bt_ttt"):
                self.bt_ttt.state(["!disabled"] if "tictactoe" in unlocked else ["disabled"])
                self.bt_quiz.state(["!disabled"] if "quiz" in unlocked else ["disabled"])
                self.bt_mem.state(["!disabled"] if "memory" in unlocked else ["disabled"])
        except Exception:
            pass

    # Adiciona novos avatares ao inventário do usuário
    def _add_avatars(self, emojis):
        inv = self.profile.data.setdefault("avatar_inventory", [])  # Obtém ou inicializa o inventário de avatares
        changed = False
        for e in emojis:
            if e not in inv:
                inv.append(e); changed = True
        if changed:
            self.profile._save()  # Salva as alterações no perfil

    # Alterna para o próximo tema na ordem definida
    def _theme_cycle(self):
        cur = Theme.current
        idx = THEME_ORDER.index(cur) if cur in THEME_ORDER else 0
        nxt = THEME_ORDER[(idx+1) % len(THEME_ORDER)]
        Theme.switch_theme(self.winfo_toplevel(), nxt)

    # Realiza a compra de um item da loja
    def buy(self, item):
        price = item["price"]
        if not self.profile.spend(price):  # Verifica se o usuário tem moedas suficientes
            messagebox.showwarning("Loja", "Moedas insuficientes!")
            return

        t = item["type"]
        # Processa a compra com base no tipo do item
        if t == "theme":
            Theme.switch_theme(self.winfo_toplevel(), item["theme"])
            self.profile.add_theme(item["key"])
        elif t == "theme_cycle":
            self._theme_cycle()
        elif t == "boost":
            self.profile.data["coin_multiplier"] = float(item.get("mult", 2.0))
            self.profile._save()
        elif t == "sound":
            self.profile.data["sound_pack"] = True
            self.profile._save()
        elif t == "avatar":
            self._add_avatars([item.get("emoji","🌸")])
        elif t == "pack":
            self._add_avatars(item.get("emojis", []))
        elif t == "game":
            self.profile.unlock_game(item["game"])

        # Exibe animação de moedas e mensagem de confirmação
        CoinFloat.show(self.winfo_toplevel(), f"-{price} 🪙", near_widget=self, offset=(0, -20))
        messagebox.showinfo("Loja", f"Você adquiriu: {item['name']}!")
        self.refresh()  # Atualiza a interface após a compra
