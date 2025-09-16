# badges.py
# Este arquivo implementa um motor simples de conquistas (badges) para o aplicativo.
# Ele gerencia a lista de conquistas disponíveis e permite conceder novas conquistas ao usuário.

class BadgeEngine:
    """
    Motor de conquistas simples.
    - Retorna a lista de conquistas possíveis.
    - Mantém o controle das conquistas já obtidas pelo usuário.
    - A lógica para conceder conquistas pode ser acionada em qualquer parte do aplicativo (ex.: ao concluir 3 pomodoros).
    """
    def __init__(self, profile_repo):
        """
        Inicializa o motor de conquistas com o repositório de perfil do usuário.
        
        Parâmetros:
        - profile_repo: Repositório que gerencia os dados do perfil do usuário.
        """
        self.profile = profile_repo  # Repositório de perfil do usuário

    def all_badges(self):
        """
        Retorna a lista de todas as conquistas disponíveis no aplicativo.
        Cada conquista é representada por um dicionário contendo:
        - key: Identificador único da conquista.
        - name: Nome descritivo da conquista.
        - icon: Ícone associado à conquista.
        
        Retorno:
        - Lista de dicionários representando as conquistas disponíveis.
        """
        return [
            {"key": "pomox3",      "name": "3 Pomodoros seguidos", "icon": "⏳"},
            {"key": "streak10",    "name": "Streak 10+ dias",      "icon": "🔥"},
            {"key": "task25",      "name": "25 tarefas feitas",     "icon": "✅"},
            {"key": "deck_master", "name": "20 acertos no Quiz",    "icon": "🧠"},
            {"key": "rich",        "name": "500 moedas",            "icon": "💰"},
        ]

    def grant(self, key):
        """
        Concede uma conquista ao usuário, se ainda não obtida.
        
        Parâmetros:
        - key: Identificador único da conquista a ser concedida.
        
        Retorno:
        - True: Se a conquista foi concedida com sucesso.
        - False: Se o usuário já possuía a conquista.
        """
        badges = set(self.profile.data.get("badges", []))  # Obtém as conquistas já obtidas pelo usuário
        if key not in badges:
            badges.add(key)  # Adiciona a nova conquista
            self.profile.data["badges"] = list(badges)  # Atualiza a lista de conquistas no perfil
            self.profile._save()  # Salva as alterações no repositório de perfil
            return True
        return False  # A conquista já foi obtida anteriormente
