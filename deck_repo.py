# deck_repo.py — versão com slug seguro p/ nomes de deck
import os, json, random, re
from typing import List, Optional
from utils import DECKS_DIR, ensure_data_dirs
from models import Deck, Card

def _safe_name(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r'[^a-z0-9_-]+', '_', s)   # troca tudo que não é [a-z0-9_-] por _
    s = re.sub(r'_+', '_', s)             # colapsa __
    return s.strip('_')

class DeckRepo:
    def __init__(self):
        ensure_data_dirs()
        self._bootstrap_default_decks()

    # ---------------- bootstrap ----------------
    def _bootstrap_default_decks(self):
        os.makedirs(DECKS_DIR, exist_ok=True)
        existing = {f for f in os.listdir(DECKS_DIR) if f.endswith(".json")}

        def ensure(name: str, cards: list):
            fname = f"{_safe_name(name)}.json"
            if fname not in existing:
                path = os.path.join(DECKS_DIR, fname)
                payload = {"name": name, "cards": cards}
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2)

        ensure("Exemplo", [
            {"front":"O que é JVM?","back":"Máquina Virtual Java","interval":1,"ease":2.5,"due":None},
            {"front":"Constante em Java?","back":"final","interval":1,"ease":2.5,"due":None},
            {"front":"Estrutura de repetição em Python?","back":"for","interval":1,"ease":2.5,"due":None},
            {"front":"Qual palavra-chave cria função em Python?","back":"def","interval":1,"ease":2.5,"due":None},
        ])

        ensure("Python Básico", [
            {"front":"Tipo imutável para sequências de Python?","back":"tuple","interval":1,"ease":2.5,"due":None},
            {"front":"Qual estrutura armazena pares chave-valor?","back":"dict","interval":1,"ease":2.5,"due":None},
            {"front":"Como converter string para inteiro?","back":"int()","interval":1,"ease":2.5,"due":None},
            {"front":"Palavra-chave para exceções?","back":"try/except","interval":1,"ease":2.5,"due":None},
        ])

        ensure("Redes", [
            {"front":"Porta padrão HTTP?","back":"80","interval":1,"ease":2.5,"due":None},
            {"front":"Protocolo para e-mail de envio?","back":"SMTP","interval":1,"ease":2.5,"due":None},
            {"front":"Camada do IP no modelo TCP/IP?","back":"Internet","interval":1,"ease":2.5,"due":None},
            {"front":"Faixa privada que começa com 192.168?","back":"Classe C privada","interval":1,"ease":2.5,"due":None},
        ])

        # Pode manter o nome “POO/Java” visualmente — o arquivo vira "poo_java.json"
        ensure("POO/Java", [
            {"front":"Mecanismo de reutilização que usa 'extends'?","back":"Herança","interval":1,"ease":2.5,"due":None},
            {"front":"Encapsulamento expõe dados via...?","back":"getters/setters","interval":1,"ease":2.5,"due":None},
            {"front":"Sobrescrita em Java?","back":"@Override","interval":1,"ease":2.5,"due":None},
            {"front":"Interface define...","back":"contrato de métodos","interval":1,"ease":2.5,"due":None},
        ])

    # ---------------- I/O ----------------
    def list_decks(self) -> List[Deck]:
        decks: List[Deck] = []
        for fn in os.listdir(DECKS_DIR):
            if not fn.endswith(".json"): continue
            try:
                with open(os.path.join(DECKS_DIR, fn), "r", encoding="utf-8") as f:
                    raw = json.load(f)
                cards = [Card(**c) for c in raw.get("cards", [])]
                name = raw.get("name", os.path.splitext(fn)[0])
                decks.append(Deck(name=name, cards=cards))
            except Exception:
                continue
        decks.sort(key=lambda d: d.name.lower())
        return decks

    def _deck_path(self, name: str) -> str:
        return os.path.join(DECKS_DIR, f"{_safe_name(name)}.json")

    def save_deck(self, deck: Deck):
        path = self._deck_path(deck.name)
        payload = {"name": deck.name, "cards": [c.__dict__ for c in deck.cards]}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def create_deck(self, name: str) -> Deck:
        deck = Deck(name=name, cards=[])
        self.save_deck(deck)
        return deck

    def delete_deck(self, name: str):
        path = self._deck_path(name)
        if os.path.exists(path):
            os.remove(path)

    # -------- cards --------
    def add_card(self, deck: Deck, front: str, back: str):
        deck.cards.append(Card(front=front, back=back, interval=1, ease=2.5, due=None))
        self.save_deck(deck)

    def update_card(self, deck: Deck, index: int, front: Optional[str]=None, back: Optional[str]=None):
        c = deck.cards[index]
        if front is not None: c.front = front
        if back  is not None: c.back  = back
        self.save_deck(deck)

    def delete_card(self, deck: Deck, index: int):
        deck.cards.pop(index)
        self.save_deck(deck)

    # -------- MCQ --------
    def mcq_options(self, deck: Deck, correct: str, k: int = 4) -> List[str]:
        backs = list({c.back for c in deck.cards if c.back})
        if correct not in backs:
            backs.append(correct)
        random.shuffle(backs)
        while len(backs) < k:
            backs.append(f"Opção {len(backs)+1}")
        if correct not in backs[:k]:
            backs[k-1] = correct
        sample = backs[:k]
        random.shuffle(sample)
        return sample
