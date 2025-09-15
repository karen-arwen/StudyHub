# flashcards_tab.py
import tkinter as tk
from tkinter import ttk
from storage import DeckRepo
from utils import today_str

class FlashcardsTab(ttk.Frame):
    def __init__(self, parent, profile):
        super().__init__(parent)
        self.profile = profile
        self.repo = DeckRepo()
        decks = self.repo.list_decks()
        self.deck = decks[0]
        self.idx = 0
        self.front = True

        top = ttk.Frame(self); top.pack(pady=4)
        ttk.Label(top, text=f"Deck: {self.deck.name}", style="Header.TLabel").pack()

        self.canvas = tk.Canvas(self, width=520, height=240, bg="#FAFAFF", highlightthickness=0)
        self.canvas.pack(pady=8)
        self.text = self.canvas.create_text(260,120, text=self.deck.cards[self.idx].front, font=("TkDefaultFont", 16))

        bar = ttk.Frame(self); bar.pack(pady=6)
        ttk.Button(bar, text="Virar", command=self.flip).pack(side=tk.LEFT, padx=4)
        for q in range(0,6):
            ttk.Button(bar, text=str(q), command=lambda x=q: self.grade(x)).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="Próximo", command=self.next_card).pack(side=tk.LEFT, padx=6)

        self.session_hits = 0; self.session_total = 0

    def flip(self):
        self.front = not self.front
        c = self.deck.cards[self.idx]
        self.canvas.itemconfig(self.text, text=c.front if self.front else c.back)

    def grade(self, q):
        c = self.deck.cards[self.idx]
        self.session_total += 1
        if q >= 3:
            self.session_hits += 1
            c.interval = max(1, int(round(c.interval * c.ease)))
            c.ease = max(1.3, c.ease + (0.1 - (5-q)*(0.08 + (5-q)*0.02)))
        else:
            c.interval = 1
        c.due = today_str()  # simplificado
        self.next_card()

    def next_card(self):
        self.idx = (self.idx + 1) % len(self.deck.cards)
        self.front = True
        self.canvas.itemconfig(self.text, text=self.deck.cards[self.idx].front)
        # fim de rodada (ciclo)
        if self.idx == 0 and self.session_total:
            bonus = 5 + self.session_hits
            self.profile.add_rewards(coins=bonus, xp=self.session_hits)
            self.session_hits = 0; self.session_total = 0
