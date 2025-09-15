import tkinter as tk
from tkinter import ttk, messagebox
from storage import ProfileRepo
from games import snake, tictactoe, quiz, memory

SHOP_ITEMS = [
    {"key":"theme_dark","name":"Tema Dark","price":30, "type":"theme"},
    {"key":"theme_neon","name":"Tema Neon","price":30, "type":"theme"},
    {"key":"skin_eevee","name":"Skin Eevee Pastel","price":40, "type":"skin"},
    {"key":"coin_x2","name":"Moedas x2 (sessão)","price":50, "type":"boost"},
    {"key":"sound_pack","name":"Pacote de Sons","price":20, "type":"sound"},
    {"key":"game_tictactoe","name":"Desbloquear Jogo da Velha","price":25, "type":"game", "game":"tictactoe"},
    {"key":"game_memory","name":"Desbloquear Memory","price":25, "type":"game", "game":"memory"},
    {"key":"game_quiz","name":"Desbloquear Quiz","price":20, "type":"game", "game":"quiz"},
]

class ShopTab(ttk.Frame):
    def __init__(self, parent, profile: ProfileRepo):
        super().__init__(parent)
        self.profile = profile
        self.build_ui()

    def build_ui(self):
        top = ttk.Frame(self); top.pack(fill=tk.X, pady=6)
        self.lbl = ttk.Label(top, text=f"Moedas: {self.profile.data['coins']}  •  Nível: {self.profile.data['level']}")
        self.lbl.pack(side=tk.LEFT, padx=6)
        ttk.Button(top, text="Atualizar", command=self.refresh_label).pack(side=tk.RIGHT)

        self.grid_items = ttk.Frame(self); self.grid_items.pack(fill=tk.BOTH, expand=True)
        for i, item in enumerate(SHOP_ITEMS):
            card = ttk.Frame(self.grid_items, style="Card.TFrame")
            card.grid(row=i//2, column=i%2, padx=10, pady=8, sticky="nsew")
            ttk.Label(card, text=item["name"], style="Header.TLabel").pack(anchor="w", padx=10, pady=6)
            ttk.Label(card, text=f"Preço: {item['price']} 🪙").pack(anchor="w", padx=10)
            ttk.Button(card, text="Comprar", command=lambda it=item: self.buy(it)).pack(padx=10, pady=8)

        # Jogos (botões desabilitam se não liberados)
        sep = ttk.Label(self, text="Jogos", style="Header.TLabel"); sep.pack(pady=6)
        btns = ttk.Frame(self); btns.pack()
        self.bt_snake = ttk.Button(btns, text="🐍 Snake", command=lambda: snake.play(self.profile))
        self.bt_ttt   = ttk.Button(btns, text="❌⭕ Jogo da Velha", command=lambda: tictactoe.play(self.profile))
        self.bt_quiz  = ttk.Button(btns, text="❓ Quiz", command=lambda: quiz.play(self.profile))
        self.bt_mem   = ttk.Button(btns, text="🧠 Memory", command=lambda: memory.play(self.profile))
        for b in (self.bt_snake, self.bt_ttt, self.bt_quiz, self.bt_mem): b.pack(side=tk.LEFT, padx=6)
        self.refresh_buttons()

    def refresh_buttons(self):
        unlocked = set(self.profile.data.get("unlocked_games", []))
        self.bt_ttt.state(["!disabled"] if "tictactoe" in unlocked else ["disabled"])
        self.bt_quiz.state(["!disabled"] if "quiz" in unlocked else ["disabled"])
        self.bt_mem.state(["!disabled"] if "memory" in unlocked else ["disabled"])

    def refresh_label(self):
        self.lbl.configure(text=f"Moedas: {self.profile.data['coins']}  •  Nível: {self.profile.data['level']}")
        self.refresh_buttons()

    def buy(self, item):
        if not self.profile.spend(item['price']):
            messagebox.showwarning("Loja", "Moedas insuficientes!"); return
        t = item['type']
        if t == 'theme':
            self.profile.add_theme(item['key'])
        elif t == 'skin':
            self.profile.data['avatar_skin'] = item['key']; self.profile._save()
        elif t == 'boost':
            self.profile.data['coin_multiplier'] = 2.0; self.profile._save()
        elif t == 'sound':
            self.profile.data['sound_pack'] = True; self.profile._save()
        elif t == 'game':
            self.profile.unlock_game(item['game'])
        messagebox.showinfo("Loja", f"Você adquiriu: {item['name']}!")
        self.refresh_label()