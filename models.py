# models.py
# Este arquivo define os modelos de dados principais utilizados no aplicativo, incluindo tarefas, perfis de usuário, cartões de estudo e decks.
# Ele utiliza dataclasses para simplificar a definição de classes de dados e fornece métodos auxiliares para conversão de dados.

from dataclasses import dataclass, field
from typing import List, Optional, Dict

# Classe que representa uma tarefa no aplicativo
@dataclass
class Task:
    id: int  # Identificador único da tarefa
    title: str  # Título ou descrição da tarefa
    priority: int = 2  # Prioridade da tarefa: 1 (baixo), 2 (médio), 3 (alto)
    tags: List[str] = field(default_factory=list)  # Lista de tags associadas à tarefa
    scheduled: Optional[str] = None  # Data agendada para a tarefa no formato "YYYY-MM-DD"
    done: bool = False  # Indica se a tarefa foi concluída

    # Converte a tarefa para um dicionário, útil para persistência de dados
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "priority": self.priority,
            "tags": self.tags,
            "scheduled": self.scheduled,
            "done": self.done,
        }

    # Cria uma instância de Task a partir de um dicionário
    @staticmethod
    def from_dict(d: Dict) -> "Task":
        return Task(
            id=d["id"], title=d["title"], priority=d.get("priority", 2),
            tags=d.get("tags", []), scheduled=d.get("scheduled"), done=d.get("done", False)
        )

# Classe que representa o perfil de um usuário
@dataclass
class Profile:
    name: str = "Karen"  # Nome do usuário
    coins: int = 0  # Quantidade de moedas acumuladas
    xp: int = 0  # Pontos de experiência acumulados
    level: int = 1  # Nível atual do usuário
    avatar_skin: str = "eevee_pastel"  # Avatar selecionado pelo usuário
    unlocked_games: List[str] = field(default_factory=lambda: ["snake"])  # Jogos desbloqueados (snake é padrão)
    themes: List[str] = field(default_factory=lambda: ["princess"])  # Temas desbloqueados (princess é padrão)
    coin_multiplier: float = 1.0  # Multiplicador de moedas (boost opcional da loja)
    sound_pack: bool = False  # Indica se o pacote de sons foi adquirido

# Classe que representa um cartão de estudo
@dataclass
class Card:
    front: str  # Lado frontal do cartão (pergunta ou conceito)
    back: str  # Lado traseiro do cartão (resposta ou explicação)
    interval: int = 1  # Intervalo de revisão em dias
    ease: float = 2.5  # Fator de facilidade para ajustar o intervalo
    due: Optional[str] = None  # Data de revisão no formato "YYYY-MM-DD"

# Classe que representa um deck de cartões de estudo
@dataclass
class Deck:
    name: str  # Nome do deck
    cards: List[Card] = field(default_factory=list)  # Lista de cartões associados ao deck