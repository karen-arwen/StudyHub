import tkinter as tk
from tkinter import messagebox

class TTT(tk.Toplevel):
    def __init__(self, profile):
        super().__init__(); self.title('Jogo da Velha — StudyHub'); self.resizable(False, False)
        self.profile=profile
        self.turn='X'; self.btns=[]
        grid = tk.Frame(self); grid.pack(padx=8, pady=8)
        for r in range(3):
            row=[]
            for c in range(3):
                b=tk.Button(grid, text=' ', width=4, height=2, font=('Arial',24), command=lambda rr=r,cc=c: self.play(rr,cc))
                b.grid(row=r, column=c, padx=4, pady=4)
                row.append(b)
            self.btns.append(row)

    def play(self,r,c):
        b=self.btns[r][c]
        if b['text']!=' ': return
        b['text']=self.turn
        if self.check_win(self.turn):
            messagebox.showinfo('Vitória', f'{self.turn} venceu! +5 moedas')
            self.profile.add_rewards(coins=5, xp=2)
            self.destroy(); return
        if all(self.btns[i][j]['text']!=' ' for i in range(3) for j in range(3)):
            messagebox.showinfo('Empate', 'Deu velha! +2 moedas')
            self.profile.add_rewards(coins=2, xp=1)
            self.destroy(); return
        self.turn='O' if self.turn=='X' else 'X'

    def check_win(self, p):
        g=[[self.btns[i][j]['text'] for j in range(3)] for i in range(3)]
        lines=g + list(zip(*g)) + [[g[i][i] for i in range(3)], [g[i][2-i] for i in range(3)]]
        return any(all(cell==p for cell in line) for line in lines)

def play(profile):
    TTT(profile)