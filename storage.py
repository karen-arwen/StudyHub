import json, os
from typing import List, Dict
from models import Task, Profile, Deck, Card
from utils import DATA_DIR, DECKS_DIR, ensure_data_dirs, today_str

PROFILE_PATH = os.path.join(DATA_DIR, "profile.json")
TASKS_PATH = os.path.join(DATA_DIR, "tasks.json")
STATS_PATH = os.path.join(DATA_DIR, "stats.json")  # {"done_per_day": {"YYYY-MM-DD": n}, "focus_minutes": {...}}

class ProfileRepo:
    def __init__(self):
        ensure_data_dirs()
        if not os.path.exists(PROFILE_PATH):
            self.data = Profile().__dict__
            self._save()
        else:
            with open(PROFILE_PATH, "r", encoding="utf-8") as f:
                self.data = json.load(f)
    def _save(self):
        with open(PROFILE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    def add_rewards(self, coins=0, xp=0):
        mult = self.data.get("coin_multiplier", 1.0)
        self.data["coins"] += int(round(coins * mult))
        self.data["xp"] += xp
        while self.data["xp"] >= 100:
            self.data["xp"] -= 100
            self.data["level"] += 1
        self._save()
    def spend(self, amount) -> bool:
        if self.data["coins"] >= amount:
            self.data["coins"] -= amount
            self._save(); return True
        return False
    def unlock_game(self, key:str):
        if key not in self.data.get("unlocked_games", []):
            self.data.setdefault("unlocked_games", []).append(key)
            self._save()
    def add_theme(self, key:str):
        if key not in self.data.get("themes", []):
            self.data.setdefault("themes", []).append(key)
            self._save()

class TaskRepo:
    def __init__(self):
        ensure_data_dirs()
        if not os.path.exists(TASKS_PATH):
            with open(TASKS_PATH, "w", encoding="utf-8") as f: json.dump([], f)
        self._load()
        self._next_id = max([t.id for t in self.tasks], default=0) + 1
    def _load(self):
        with open(TASKS_PATH, "r", encoding="utf-8") as f:
            arr = json.load(f)
            self.tasks: List[Task] = [Task.from_dict(x) for x in arr]
    def _save(self):
        with open(TASKS_PATH, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in self.tasks], f, ensure_ascii=False, indent=2)
    def list_all(self): return list(self.tasks)
    def get(self, tid:int):
        for t in self.tasks:
            if t.id == tid: return t
        raise KeyError(tid)
    def add(self, title, priority=2, tags=None, scheduled=None):
        t = Task(id=self._next_id, title=title, priority=priority, tags=tags or [], scheduled=scheduled)
        self._next_id += 1
        self.tasks.append(t); self._save(); return t
    def update(self, tid:int, **fields):
        t = self.get(tid)
        for k,v in fields.items(): setattr(t,k,v)
        self._save(); return t
    def remove(self, tid:int):
        self.tasks = [t for t in self.tasks if t.id != tid]
        self._save()

class StatsRepo:
    def __init__(self):
        ensure_data_dirs()
        if not os.path.exists(STATS_PATH):
            with open(STATS_PATH, "w", encoding="utf-8") as f: json.dump({"done_per_day":{}, "focus_minutes":{}}, f)
        with open(STATS_PATH, "r", encoding="utf-8") as f:
            self.data: Dict = json.load(f)
    def _save(self):
        with open(STATS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    def inc_done_today(self, n=1):
        d = today_str()
        self.data.setdefault("done_per_day", {})
        self.data["done_per_day"][d] = self.data["done_per_day"].get(d, 0) + n
        self._save()
    def add_focus_minutes(self, minutes):
        d = today_str()
        self.data.setdefault("focus_minutes", {})
        self.data["focus_minutes"][d] = self.data["focus_minutes"].get(d, 0) + minutes
        self._save()
    def last7(self):
        # retorna listas alinhadas de últimos 7 dias
        import datetime as dt
        days = [(dt.date.today()-dt.timedelta(days=i)).isoformat() for i in range(6,-1,-1)]
        done = [self.data.get("done_per_day", {}).get(d,0) for d in days]
        focus = [self.data.get("focus_minutes", {}).get(d,0) for d in days]
        return days, done, focus

class DeckRepo:
    def __init__(self):
        ensure_data_dirs()
    def list_decks(self):
        decks = []
        for fn in os.listdir(DECKS_DIR):
            if fn.endswith('.json'):
                with open(os.path.join(DECKS_DIR, fn), 'r', encoding='utf-8') as f:
                    raw = json.load(f)
                    cards = [Card(**c) for c in raw.get("cards", [])]
                    decks.append(Deck(name=raw.get("name", fn[:-5]), cards=cards))
        if not decks:
            # cria um exemplo
            path = os.path.join(DECKS_DIR, "exemplo.json")
            ex = {"name":"Exemplo", "cards":[{"front":"O que é JVM?","back":"Máquina Virtual Java"},{"front":"constante em Java?","back":"final"}]}
            with open(path,'w',encoding='utf-8') as f: json.dump(ex, f, ensure_ascii=False, indent=2)
            return self.list_decks()
        return decks