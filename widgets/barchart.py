import tkinter as tk

class BarChart(tk.Canvas):
    def __init__(self, master, width=520, height=200, **kw):
        super().__init__(master, width=width, height=height, highlightthickness=0, **kw)
        self.width=width; self.height=height
    def draw(self, values, labels=None):
        self.delete("all")
        if not values: return
        n=len(values); w = self.width/(n*1.5)
        maxv = max(values) or 1
        for i,v in enumerate(values):
            x = (i+1)*self.width/(n+1)
            h = (v/maxv)*(self.height-30)
            self.create_rectangle(x-w/2, self.height-20-h, x+w/2, self.height-20, fill="#B388EB", width=0)
            if labels:
                self.create_text(x, self.height-8, text=labels[i], font=("TkDefaultFont",9))
            self.create_text(x, self.height-30-h-10, text=str(v), font=("TkDefaultFont",9))