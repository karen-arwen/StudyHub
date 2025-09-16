# tags_repo.py
import os, json
from typing import List, Dict
from utils import DATA_DIR, ensure_data_dirs

TAGS_PATH = os.path.join(DATA_DIR, "tags.json")

class TagsRepo:
    """
    Guarda e sugere tags globais em data/tags.json
    Estrutura: { "tags": {"java": 3, "redes": 1, ...} }
    """
    def __init__(self):
        ensure_data_dirs()
        if not os.path.exists(TAGS_PATH):
            with open(TAGS_PATH, "w", encoding="utf-8") as f:
                json.dump({"tags": {}}, f)
        with open(TAGS_PATH, "r", encoding="utf-8") as f:
            self.data: Dict[str, Dict[str, int]] = json.load(f)
        self.data.setdefault("tags", {})

    def save(self):
        with open(TAGS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def add_many(self, tags: List[str]):
        for t in tags:
            t = t.strip()
            if not t: continue
            self.data["tags"][t] = self.data["tags"].get(t, 0) + 1
        self.save()

    def remove_many(self, tags: List[str]):
        for t in tags:
            if t in self.data["tags"]:
                self.data["tags"][t] = max(0, self.data["tags"][t]-1)
                if self.data["tags"][t] == 0:
                    del self.data["tags"][t]
        self.save()

    def suggestions(self, prefix: str = "", limit: int = 8) -> List[str]:
        prefix = (prefix or "").strip().lower()
        items = list(self.data["tags"].items())
        # ordena por frequência desc, depois alfabética
        items.sort(key=lambda kv: (-kv[1], kv[0]))
        if not prefix:
            return [k for k, _ in items[:limit]]
        return [k for k, _ in items if k.lower().startswith(prefix)][:limit]
