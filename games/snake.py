import tkinter as tk
import random, json, os
from utils import DATA_DIR

SCORES = os.path.join(DATA_DIR, 'scores_snake.json')

def load_scores():
    if not os.path.exists(SCORES): return []
    return json.load(open(SCORES,'r'))

def save_score(score):
    arr = load_scores(); arr.append(score); arr = sorted(arr, reverse=True)[:10]
    json.dump(arr, open(SCORES,'w'))

CELL = 16; W=30; H=20

class SnakeGame(tk.Toplevel):
    def __init__(self, profile):
        super().__init__()
        self.title('Snake — StudyHub')
        self.resizable(False, False)
        self.canvas = tk.Canvas(self, width=W*CELL, height=H*CELL, bg='#111')
        self.canvas.pack()
        self.snake = [(5,5),(4,5),(3,5)]; self.dir=(1,0)
        self.food = self.spawn_food()
        self.score=0; self.profile=profile
        self.bind('<Key>', self.on_key)
        self.tick()

    def on_key(self, ev):
        k = ev.keysym
        dirs = {'Up':(0,-1),'Down':(0,1),'Left':(-1,0),'Right':(1,0)}
        if k in dirs:
            nx,ny=dirs[k]
            if (nx,ny)!=(-self.dir[0],-self.dir[1]): self.dir=(nx,ny)

    def spawn_food(self):
        import random
        while True:
            p = (random.randint(0,W-1), random.randint(0,H-1))
            if p not in self.snake: return p

    def tick(self):
        # move
        head=(self.snake[0][0]+self.dir[0], self.snake[0][1]+self.dir[1])
        if head[0]<0 or head[0]>=W or head[1]<0 or head[1]>=H or head in self.snake:
            save_score(self.score)
            self.profile.add_rewards(coins=max(1,self.score//5), xp=max(0,self.score//10))
            tk.messagebox.showinfo('Snake', f'Game Over! Pontos: {self.score}')
            self.destroy(); return
        self.snake.insert(0, head)
        if head==self.food:
            self.score+=10; self.food=self.spawn_food()
        else:
            self.snake.pop()

        # draw
        self.canvas.delete('all')
        self.canvas.create_text(40,12, text=str(self.score), fill='#fff', anchor='w')
        x,y=self.food; self.canvas.create_rectangle(x*CELL,y*CELL,(x+1)*CELL,(y+1)*CELL, fill='#e33', width=0)
        for i,(x,y) in enumerate(self.snake):
            self.canvas.create_rectangle(x*CELL,y*CELL,(x+1)*CELL,(y+1)*CELL, fill='#6cf' if i==0 else '#4a8', width=0)
        self.after(120, self.tick)


def play(profile):
    SnakeGame(profile)