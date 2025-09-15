import tkinter as tk
import random
from tkinter import messagebox

ICONS = list('🍎🍉🍇🍓🍋🍒🍑🍍')

class Memory(tk.Toplevel):
    def __init__(self, profile):
        super().__init__(); self.title('Memory — StudyHub'); self.resizable(False, False)
        self.profile = profile
        pairs = ICONS[:8]; arr = pairs + pairs
        random.shuffle(arr)
        self.first = None; self.left = len(arr)
        self.btns = []
        grid = tk.Frame(self); grid.pack(padx=8, pady=8)
        for i, sym in enumerate(arr):
            b = tk.Button(grid, text='?', width=4, height=2, font=('Arial',20))
            b.sym = sym; b.idx = i
            b.config(command=lambda bb=b: self.reveal(bb))
            b.grid(row=i//4, column=i%4, padx=4, pady=4)
            self.btns.append(b)

    def reveal(self, b):
        if b['text'] != '?': return
        b['text'] = b.sym
        if not self.first:
            self.first = b; return
        # compara
        if self.first.sym == b.sym and self.first is not b:
            self.first.config(state='disabled'); b.config(state='disabled'); self.left -= 2
        else:
            self.after(600, lambda: (self.first.config(text='?'), b.config(text='?')))
        self.first = None
        if self.left == 0:
            self.profile.add_rewards(coins=10, xp=5)
            messagebox.showinfo('Memory', 'Parabéns! Você completou o jogo da memória! +10 moedas')
            self.destroy()

def play(profile):
    Memory(profile)
