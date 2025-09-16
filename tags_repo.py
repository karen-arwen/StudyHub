# tags_repo.py
# Importa módulos necessários para manipulação de arquivos e JSON
import os, json
from typing import List, Dict
from utils import DATA_DIR, ensure_data_dirs  # Utilitários para gerenciar diretórios e dados

# Caminho para o arquivo que armazena as tags globais
TAGS_PATH = os.path.join(DATA_DIR, "tags.json")

class TagsRepo:
    """
    Repositório para gerenciar tags globais armazenadas em data/tags.json.
    Estrutura do arquivo JSON:
    {
        "tags": {
            "java": 3,  # Tag 'java' foi usada 3 vezes
            "redes": 1  # Tag 'redes' foi usada 1 vez
        }
    }
    """
    def __init__(self):
        ensure_data_dirs()  # Garante que os diretórios necessários existam
        if not os.path.exists(TAGS_PATH):
            # Cria o arquivo tags.json vazio, se não existir
            with open(TAGS_PATH, "w", encoding="utf-8") as f:
                json.dump({"tags": {}}, f)
        # Carrega os dados do arquivo JSON
        with open(TAGS_PATH, "r", encoding="utf-8") as f:
            self.data: Dict[str, Dict[str, int]] = json.load(f)
        # Garante que a chave "tags" exista no dicionário
        self.data.setdefault("tags", {})

    def save(self):
        """Salva os dados de tags no arquivo JSON."""
        with open(TAGS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def add_many(self, tags: List[str]):
        """Adiciona múltiplas tags ao repositório, incrementando sua contagem."""
        for t in tags:
            t = t.strip()  # Remove espaços extras
            if not t: continue  # Ignora tags vazias
            # Incrementa a contagem da tag ou inicializa com 1
            self.data["tags"][t] = self.data["tags"].get(t, 0) + 1
        self.save()  # Salva as alterações

    def remove_many(self, tags: List[str]):
        """Remove múltiplas tags do repositório, decrementando sua contagem."""
        for t in tags:
            if t in self.data["tags"]:
                # Decrementa a contagem da tag, mas não permite valores negativos
                self.data["tags"][t] = max(0, self.data["tags"][t]-1)
                # Remove a tag se sua contagem chegar a 0
                if self.data["tags"][t] == 0:
                    del self.data["tags"][t]
        self.save()  # Salva as alterações

    def suggestions(self, prefix: str = "", limit: int = 8) -> List[str]:
        """Sugere tags com base em um prefixo e ordena por frequência e ordem alfabética."""
        prefix = (prefix or "").strip().lower()  # Normaliza o prefixo
        items = list(self.data["tags"].items())  # Obtém as tags e suas contagens
        # Ordena por frequência (descendente) e depois por ordem alfabética
        items.sort(key=lambda kv: (-kv[1], kv[0]))
        if not prefix:
            # Retorna as tags mais frequentes, limitado ao número especificado
            return [k for k, _ in items[:limit]]
        # Filtra as tags que começam com o prefixo e aplica o limite
        return [k for k, _ in items if k.lower().startswith(prefix)][:limit]
