class PomodoroFSM:
    def __init__(self, focus=25*60, short=5*60, long=15*60):
        self.focus, self.short, self.long = focus, short, long
        self.state, self.remaining, self.cycles = "IDLE", focus, 0
    def start(self): self.state, self.remaining = "FOCUS", self.focus
    def tick(self):
        if self.state not in ("FOCUS","BREAK","LONG_BREAK"): return False
        self.remaining -= 1
        if self.remaining>0: return False
        if self.state=="FOCUS":
            self.cycles+=1
            if self.cycles%4==0: self.state,self.remaining="LONG_BREAK",self.long
            else: self.state,self.remaining="BREAK",self.short
            return True
        elif self.state in ("BREAK","LONG_BREAK"): self.state,self.remaining="FOCUS",self.focus; return False