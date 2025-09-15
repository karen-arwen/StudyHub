from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def do(self): ...
    @abstractmethod
    def undo(self): ...

class CommandManager:
    def __init__(self):
        self._undo = []
        self._redo = []
    def do(self, cmd: 'Command'):
        cmd.do(); self._undo.append(cmd); self._redo.clear()
    def undo(self):
        if not self._undo: return
        c = self._undo.pop(); c.undo(); self._redo.append(c)
    def redo(self):
        if not self._redo: return
        c = self._redo.pop(); c.do(); self._undo.append(c)

class AddTask(Command):
    def __init__(self, repo, title, priority=2, tags=None, scheduled=None):
        self.repo=repo; self.kw=dict(title=title, priority=priority, tags=tags, scheduled=scheduled)
        self.created=None
    def do(self): self.created=self.repo.add(**self.kw)
    def undo(self): self.repo.remove(self.created.id)

class EditTask(Command):
    def __init__(self, repo, tid, fields):
        self.repo=repo; self.tid=tid; self.fields=fields; self.prev=None
    def do(self):
        t=self.repo.get(self.tid); self.prev={k:getattr(t,k) for k in self.fields}; self.repo.update(self.tid, **self.fields)
    def undo(self): self.repo.update(self.tid, **self.prev)

class DeleteTask(Command):
    def __init__(self, repo, tid): self.repo=repo; self.tid=tid; self.prev=None
    def do(self):
        t=self.repo.get(self.tid); self.prev=t.to_dict(); self.repo.remove(self.tid)
    def undo(self):
        from models import Task
        obj=Task.from_dict(self.prev); self.repo.tasks.append(obj); self.repo._save()

class ToggleDone(Command):
    def __init__(self, repo, tid, stats=None): self.repo=repo; self.tid=tid; self.prev=None; self.stats=stats
    def do(self):
        t=self.repo.get(self.tid); self.prev=t.done; self.repo.update(self.tid, done=not t.done)
        if not self.prev and self.stats:
            self.stats.inc_done_today(1)
    def undo(self):
        # se desfizer uma conclusão, não decrementa estatística para simplificar
        self.repo.update(self.tid, done=self.prev)