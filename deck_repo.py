# deck_repo.py
# Este arquivo implementa o repositório para gerenciar baralhos e cartões de estudo.
# Ele fornece métodos para criar, listar, atualizar e excluir baralhos e cartões, além de funcionalidades específicas como múltipla escolha.

import os, json, random, re
from typing import List, Optional
from utils import DECKS_DIR, ensure_data_dirs  # Utilitários para gerenciar diretórios e dados
from models import Deck, Card  # Modelos de dados para baralhos e cartões

# Função auxiliar para gerar nomes seguros para arquivos
# Substitui caracteres inválidos por "_" e normaliza o nome
def _safe_name(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r'[^a-z0-9_-]+', '_', s)  # Substitui caracteres não permitidos por "_"
    s = re.sub(r'_+', '_', s)  # Remove múltiplos "_" consecutivos
    return s.strip('_')

# Classe principal para gerenciar baralhos
class DeckRepo:
    def __init__(self):
        ensure_data_dirs()  # Garante que os diretórios necessários existem
        self._bootstrap_default_decks()  # Inicializa baralhos padrão, se necessário

    # ---------------- bootstrap ----------------
    def _bootstrap_default_decks(self):
        """Cria baralhos padrão se eles ainda não existirem."""
        os.makedirs(DECKS_DIR, exist_ok=True)
        existing = {f for f in os.listdir(DECKS_DIR) if f.endswith(".json")}

        def ensure(name: str, cards: list):
            fname = f"{_safe_name(name)}.json"
            if fname not in existing:
                path = os.path.join(DECKS_DIR, fname)
                payload = {"name": name, "cards": cards}
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2)

        # Exemplos de baralhos padrão
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

        ensure("POO/Java", [
            {"front":"Mecanismo de reutilização que usa 'extends'?","back":"Herança","interval":1,"ease":2.5,"due":None},
            {"front":"Encapsulamento expõe dados via...?","back":"getters/setters","interval":1,"ease":2.5,"due":None},
            {"front":"Sobrescrita em Java?","back":"@Override","interval":1,"ease":2.5,"due":None},
            {"front":"Interface define...","back":"contrato de métodos","interval":1,"ease":2.5,"due":None},
        ])

    # ---------------- I/O ----------------
    def list_decks(self) -> List[Deck]:
        """Lista todos os baralhos disponíveis no diretório."""
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
        """Retorna o caminho do arquivo JSON correspondente ao baralho."""
        return os.path.join(DECKS_DIR, f"{_safe_name(name)}.json")

    def save_deck(self, deck: Deck):
        """Salva um baralho no arquivo correspondente."""
        path = self._deck_path(deck.name)
        payload = {"name": deck.name, "cards": [c.__dict__ for c in deck.cards]}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def create_deck(self, name: str) -> Deck:
        """Cria um novo baralho vazio."""
        deck = Deck(name=name, cards=[])
        self.save_deck(deck)
        return deck

    def delete_deck(self, name: str):
        """Exclui o arquivo correspondente ao baralho."""
        path = self._deck_path(name)
        if os.path.exists(path):
            os.remove(path)

    # -------- cards --------
    def add_card(self, deck: Deck, front: str, back: str):
        """Adiciona um novo cartão ao baralho."""
        deck.cards.append(Card(front=front, back=back, interval=1, ease=2.5, due=None))
        self.save_deck(deck)

    def update_card(self, deck: Deck, index: int, front: Optional[str]=None, back: Optional[str]=None):
        """Atualiza o conteúdo de um cartão existente."""
        c = deck.cards[index]
        if front is not None: c.front = front
        if back  is not None: c.back  = back
        self.save_deck(deck)

    def delete_card(self, deck: Deck, index: int):
        """Remove um cartão do baralho pelo índice."""
        deck.cards.pop(index)
        self.save_deck(deck)

    # -------- MCQ --------
    def mcq_options(self, deck: Deck, correct: str, k: int = 4) -> List[str]:
        """Gera opções para múltipla escolha com base nos cartões do baralho."""
        backs = list({c.back for c in deck.cards if c.back})  # Coleta todas as respostas únicas
        if correct not in backs:
            backs.append(correct)  # Garante que a resposta correta está incluída
        random.shuffle(backs)  # Embaralha as opções
        while len(backs) < k:
            backs.append(f"Opção {len(backs)+1}")  # Adiciona opções fictícias se necessário
        if correct not in backs[:k]:
            backs[k-1] = correct  # Garante que a resposta correta está entre as primeiras k opções
        sample = backs[:k]
        random.shuffle(sample)  # Embaralha novamente as opções finais
        return sample
