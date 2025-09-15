# utils.py
import os, json, datetime as dt

DATA_DIR = "data"
DECKS_DIR = os.path.join(DATA_DIR, "decks")
PROFILE_PATH = os.path.join(DATA_DIR, "profile.json")
TASKS_PATH = os.path.join(DATA_DIR, "tasks.json")
STATS_PATH = os.path.join(DATA_DIR, "stats.json")

def ensure_data_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(DECKS_DIR, exist_ok=True)

def today_str():
    return dt.date.today().isoformat()

def init_default_files():
    # profile.json
    if not os.path.exists(PROFILE_PATH):
        profile = {
            "name": "Karen",
            "coins": 0,
            "xp": 0,
            "level": 1,
            "avatar_skin": "eevee_pastel",
            "unlocked_games": ["snake"],
            "themes": ["princess"],
            "coin_multiplier": 1.0,
            "sound_pack": False
        }
        with open(PROFILE_PATH, "w", encoding="utf-8") as f: json.dump(profile, f, ensure_ascii=False, indent=2)

    # tasks.json
    if not os.path.exists(TASKS_PATH):
        with open(TASKS_PATH, "w", encoding="utf-8") as f: json.dump([], f)

    # stats.json
    if not os.path.exists(STATS_PATH):
        with open(STATS_PATH, "w", encoding="utf-8") as f: json.dump({"done_per_day":{}, "focus_minutes":{}}, f)

    # decks/exemplo.json
    ex_path = os.path.join(DECKS_DIR, "exemplo.json")
    if not os.path.exists(ex_path):
        ex = {"name":"Exemplo","cards":[
            {"front":"O que é JVM?","back":"Máquina Virtual Java","interval":1,"ease":2.5,"due":None},
            {"front":"Constante em Java?","back":"final","interval":1,"ease":2.5,"due":None},
            {"front":"Estrutura de repetição em Python para iteráveis?","back":"for","interval":1,"ease":2.5,"due":None}
        ]}
        with open(ex_path,'w',encoding='utf-8') as f: json.dump(ex, f, ensure_ascii=False, indent=2)
