import tkinter as tk

class CircularProgress(tk.Canvas):
    def __init__(self, master, size=160, thickness=14, **kw):
        super().__init__(master, width=size, height=size, highlightthickness=0, **kw)
        self.size=size; self.thickness=thickness
        self.bg=self.create_oval(thickness,thickness,size-thickness,size-thickness, outline="#eee", width=thickness)
        self.arc=self.create_arc(thickness,thickness,size-thickness,size-thickness, start=90, extent=0, style=tk.ARC,width=thickness)
        self.txt=self.create_text(size/2,size/2,text="00:00", font=("TkDefaultFont",14,"bold"))
    def set_progress(self, ratio): self.itemconfig(self.arc, extent=-360*ratio)
    def set_time(self, s): self.itemconfig(self.txt,text=s)