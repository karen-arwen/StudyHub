import tkinter as tk
from tkinter import messagebox

QUESTS = [
    ("Qual palavra-chave define constante em Java?", "final"),
    ("Qual método inicia uma thread em Java?", "start"),
    ("Sigla do banco relacional da AWS usada no curso?", "aurora")
]

class Quiz(tk.Toplevel):
    def __init__(self, profile):
        super().__init__(); self.title('Quiz — StudyHub'); self.resizable(False, False)
        self.profile=profile; self.i=0; self.score=0
        self.q = tk.Label(self, text=QUESTS[self.i][0], font=('TkDefaultFont', 14)); self.q.pack(padx=12, pady=10)
        self.var = tk.StringVar(); e = tk.Entry(self, textvariable=self.var, width=32); e.pack(padx=12); e.focus_set()
        tk.Button(self, text='Responder', command=self.answer).pack(pady=8)
    def answer(self):
        if self.var.get().strip().lower() == QUESTS[self.i][1]:
            self.score+=1
        self.i+=1; self.var.set('')
        if self.i>=len(QUESTS):
            self.profile.add_rewards(coins=2*self.score, xp=self.score)
            messagebox.showinfo('Quiz', f'Acertos: {self.score}/{len(QUESTS)} — +{2*self.score} moedas')
            self.destroy(); return
        self.q.configure(text=QUESTS[self.i][0])

def play(profile):
    Quiz(profile)