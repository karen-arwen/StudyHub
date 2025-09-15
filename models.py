from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class Task:
    id: int
    title: str
    priority: int = 2          # 1 baixo, 2 médio, 3 alto
    tags: List[str] = field(default_factory=list)
    scheduled: Optional[str] = None  # YYYY-MM-DD
    done: bool = False

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "priority": self.priority,
            "tags": self.tags,
            "scheduled": self.scheduled,
            "done": self.done,
        }

    @staticmethod
    def from_dict(d: Dict) -> "Task":
        return Task(
            id=d["id"], title=d["title"], priority=d.get("priority",2),
            tags=d.get("tags", []), scheduled=d.get("scheduled"), done=d.get("done", False)
        )

@dataclass
class Profile:
    name: str = "Karen"
    coins: int = 0
    xp: int = 0
    level: int = 1
    avatar_skin: str = "eevee_pastel"
    unlocked_games: List[str] = field(default_factory=lambda: ["snake"])  # snake vem liberado
    themes: List[str] = field(default_factory=lambda: ["princess"])      # tema padrão
    coin_multiplier: float = 1.0                                          # boost opcional da loja
    sound_pack: bool = False

@dataclass
class Card:
    front: str
    back: str
    interval: int = 1     # dias
    ease: float = 2.5
    due: Optional[str] = None  # YYYY-MM-DD

@dataclass
class Deck:
    name: str
    cards: List[Card] = field(default_factory=list)