# utils.py
# Este arquivo contém funções utilitárias para gerenciar diretórios, arquivos e dados padrão da aplicação.

# Constantes:
# - DATA_DIR: Diretório principal para armazenar dados.
# - DECKS_DIR: Diretório para armazenar decks de flashcards.
# - PROFILE_PATH: Caminho para o arquivo de perfil do usuário.
# - TASKS_PATH: Caminho para o arquivo de tarefas.
# - STATS_PATH: Caminho para o arquivo de estatísticas.

import os, json, datetime as dt

DATA_DIR = "data"
DECKS_DIR = os.path.join(DATA_DIR, "decks")
PROFILE_PATH = os.path.join(DATA_DIR, "profile.json")
TASKS_PATH = os.path.join(DATA_DIR, "tasks.json")
STATS_PATH = os.path.join(DATA_DIR, "stats.json")

def ensure_data_dirs():
    """Garante que os diretórios de dados necessários existam."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(DECKS_DIR, exist_ok=True)

def today_str():
    """Retorna a data atual no formato ISO (YYYY-MM-DD)."""
    return dt.date.today().isoformat()

def init_default_files():
    """Inicializa arquivos padrão, caso não existam."""

    # Inicializa profile.json com dados padrão, se não existir.
    if not os.path.exists(PROFILE_PATH):
        profile = {
            "name": "Karen",  # Nome padrão do usuário.
            "coins": 0,        # Moedas iniciais.
            "xp": 0,           # Experiência inicial.
            "level": 1,        # Nível inicial.
            "avatar_skin": "eevee_pastel",  # Avatar padrão.
            "unlocked_games": ["snake"],    # Jogos desbloqueados inicialmente.
            "themes": ["princess"],         # Tema padrão.
            "coin_multiplier": 1.0,          # Multiplicador de moedas padrão.
            "sound_pack": False              # Pacote de som desativado por padrão.
        }
        with open(PROFILE_PATH, "w", encoding="utf-8") as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)

    # Inicializa tasks.json como uma lista vazia, se não existir.
    if not os.path.exists(TASKS_PATH):
        with open(TASKS_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)

    # Inicializa stats.json com estrutura padrão, se não existir.
    if not os.path.exists(STATS_PATH):
        with open(STATS_PATH, "w", encoding="utf-8") as f:
            json.dump({"done_per_day": {}, "focus_minutes": {}}, f)

    # Inicializa decks/exemplo.json com um deck de exemplo, se não existir.
    ex_path = os.path.join(DECKS_DIR, "exemplo.json")
    if not os.path.exists(ex_path):
        ex = {
            "name": "Exemplo",  # Nome do deck.
            "cards": [           # Lista de cartões no deck.
                {"front": "O que é JVM?", "back": "Máquina Virtual Java", "interval": 1, "ease": 2.5, "due": None},
                {"front": "Constante em Java?", "back": "final", "interval": 1, "ease": 2.5, "due": None},
                {"front": "Estrutura de repetição em Python para iteráveis?", "back": "for", "interval": 1, "ease": 2.5, "due": None}
            ]
        }
        with open(ex_path, 'w', encoding='utf-8') as f:
            json.dump(ex, f, ensure_ascii=False, indent=2)
