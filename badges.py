# badges.py — motor de conquistas simples
class BadgeEngine:
    """
    Apenas retorna a lista de conquistas possíveis e mantém as já ganhas.
    A lógica de “dar badge” você pode acionar onde preferir (ex.: ao concluir 3 pomodoros).
    """
    def __init__(self, profile_repo):
        self.profile = profile_repo

    def all_badges(self):
        # catálogo (sinta-se livre pra expandir)
        return [
            {"key":"pomox3",      "name":"3 Pomodoros seguidos", "icon":"⏳"},
            {"key":"streak10",    "name":"Streak 10+ dias",      "icon":"🔥"},
            {"key":"task25",      "name":"25 tarefas feitas",     "icon":"✅"},
            {"key":"deck_master", "name":"20 acertos no Quiz",    "icon":"🧠"},
            {"key":"rich",        "name":"500 moedas",            "icon":"💰"},
        ]

    def grant(self, key):
        badges = set(self.profile.data.get("badges", []))
        if key not in badges:
            badges.add(key)
            self.profile.data["badges"] = list(badges)
            self.profile._save()
            return True
        return False
