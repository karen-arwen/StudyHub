# storage.py
# Importa módulos necessários para manipulação de arquivos, JSON e tipos
import json, os
from typing import List, Dict
from models import Task, Profile  # Modelos de dados para tarefas e perfil
from utils import DATA_DIR, ensure_data_dirs, today_str  # Utilitários para diretórios e datas

# Caminhos para os arquivos de dados
PROFILE_PATH = os.path.join(DATA_DIR, "profile.json")
TASKS_PATH   = os.path.join(DATA_DIR, "tasks.json")
STATS_PATH   = os.path.join(DATA_DIR, "stats.json")

# Classe para gerenciar o repositório de perfil
class ProfileRepo:
    def __init__(self):
        ensure_data_dirs()  # Garante que os diretórios necessários existam
        if not os.path.exists(PROFILE_PATH):
            # Cria um perfil padrão se o arquivo não existir
            self.data = Profile().__dict__
            self.data.setdefault("badges", [])
            self.data.setdefault("learning", "Java, Redes, POO")
            self._save()
        else:
            # Carrega os dados do perfil
            with open(PROFILE_PATH, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            # Garante que chaves novas sejam adicionadas a perfis antigos
            self.data.setdefault("badges", [])
            self.data.setdefault("learning", "Java, Redes, POO")
            self.data.setdefault("coin_multiplier", 1.0)
            self.data.setdefault("sound_pack", False)
            self.data.setdefault("themes", ["princess"])
            self.data.setdefault("unlocked_games", ["snake"])
            self._save()

    def _save(self):
        """Salva os dados do perfil no arquivo JSON."""
        with open(PROFILE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def add_rewards(self, coins=0, xp=0):
        """Adiciona recompensas de moedas e XP ao perfil."""
        mult = self.data.get("coin_multiplier", 1.0)
        self.data["coins"] = int(self.data.get("coins", 0) + round(coins * mult))
        self.data["xp"] = self.data.get("xp", 0) + xp
        while self.data["xp"] >= 100:
            self.data["xp"] -= 100
            self.data["level"] = self.data.get("level", 1) + 1
        self._save()

    def spend(self, amount) -> bool:
        """Deduz uma quantidade de moedas do perfil, se possível."""
        if self.data.get("coins", 0) >= amount:
            self.data["coins"] -= amount
            self._save(); return True
        return False

    def unlock_game(self, key: str):
        """Desbloqueia um jogo no perfil."""
        ug = self.data.setdefault("unlocked_games", [])
        if key not in ug:
            ug.append(key); self._save()

    def add_theme(self, key: str):
        """Adiciona um tema ao perfil."""
        th = self.data.setdefault("themes", [])
        if key not in th:
            th.append(key); self._save()

# Classe para gerenciar o repositório de tarefas
class TaskRepo:
    def __init__(self):
        ensure_data_dirs()  # Garante que os diretórios necessários existam
        if not os.path.exists(TASKS_PATH):
            # Cria um arquivo vazio de tarefas se não existir
            with open(TASKS_PATH, "w", encoding="utf-8") as f: json.dump([], f)
        self._load()
        self._next_id = max([t.id for t in self.tasks], default=0) + 1

    def _load(self):
        """Carrega as tarefas do arquivo JSON."""
        with open(TASKS_PATH, "r", encoding="utf-8") as f:
            arr = json.load(f)
            self.tasks: List[Task] = [Task.from_dict(x) for x in arr]

    def _save(self):
        """Salva as tarefas no arquivo JSON."""
        with open(TASKS_PATH, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in self.tasks], f, ensure_ascii=False, indent=2)

    def list_all(self):
        """Retorna todas as tarefas."""
        return list(self.tasks)

    def get(self, tid: int):
        """Obtém uma tarefa pelo ID."""
        for t in self.tasks:
            if t.id == tid: return t
        raise KeyError(tid)

    def add(self, title, priority=2, tags=None, scheduled=None):
        """Adiciona uma nova tarefa."""
        t = Task(id=self._next_id, title=title, priority=priority, tags=tags or [], scheduled=scheduled)
        self._next_id += 1
        self.tasks.append(t); self._save(); return t

    def update(self, tid: int, **fields):
        """Atualiza os campos de uma tarefa existente."""
        t = self.get(tid)
        for k, v in fields.items(): setattr(t, k, v)
        self._save(); return t

    def remove(self, tid: int):
        """Remove uma tarefa pelo ID."""
        self.tasks = [t for t in self.tasks if t.id != tid]
        self._save()

# Classe para gerenciar estatísticas
class StatsRepo:
    def __init__(self):
        ensure_data_dirs()  # Garante que os diretórios necessários existam
        if not os.path.exists(STATS_PATH):
            # Cria um arquivo vazio de estatísticas se não existir
            with open(STATS_PATH, "w", encoding="utf-8") as f:
                json.dump({"done_per_day": {}, "focus_minutes": {}}, f)
        with open(STATS_PATH, "r", encoding="utf-8") as f:
            self.data: Dict = json.load(f)

    def _save(self):
        """Salva os dados de estatísticas no arquivo JSON."""
        with open(STATS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def inc_done_today(self, n=1):
        """Incrementa o número de tarefas concluídas hoje."""
        d = today_str()
        self.data.setdefault("done_per_day", {})
        self.data["done_per_day"][d] = self.data["done_per_day"].get(d, 0) + n
        self._save()

    def add_focus_minutes(self, minutes):
        """Adiciona minutos de foco ao dia atual."""
        d = today_str()
        self.data.setdefault("focus_minutes", {})
        self.data["focus_minutes"][d] = self.data["focus_minutes"].get(d, 0) + minutes
        self._save()

    def last7(self):
        """Retorna os dados dos últimos 7 dias (tarefas concluídas e minutos de foco)."""
        import datetime as dt
        days = [(dt.date.today()-dt.timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
        done = [self.data.get("done_per_day", {}).get(d, 0) for d in days]
        focus = [self.data.get("focus_minutes", {}).get(d, 0) for d in days]
        return days, done, focus

# DeckRepo permanece igual em seu arquivo original (se você já tiver).
# Se ele estiver neste mesmo arquivo no seu projeto, mantenha a versão que cria/exibe decks.
