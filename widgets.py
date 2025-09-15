# widgets.py
import tkinter as tk

class CircularProgress(tk.Canvas):
    def __init__(self, master, size=160, thickness=14, **kw):
        super().__init__(master, width=size, height=size, highlightthickness=0, **kw)
        self.size=size; self.thickness=thickness
        self.bg_circle = self.create_oval(thickness, thickness, size-thickness, size-thickness,
                                          outline="#e9e9e9", width=thickness)
        self.fg_arc = self.create_arc(thickness, thickness, size-thickness, size-thickness,
                                      start=90, extent=0, style=tk.ARC, width=thickness)
        self.text = self.create_text(size/2, size/2, text="00:00", font=("TkDefaultFont", 14, "bold"))
    def set_progress(self, ratio: float):
        self.itemconfig(self.fg_arc, extent=-360*ratio)
    def set_time_text(self, s: str):
        self.itemconfig(self.text, text=s)

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
