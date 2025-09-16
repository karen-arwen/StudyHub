# profile_tab.py — Perfil 2.0 (sem export/import)
# Importa módulos necessários para criar a interface gráfica e gerenciar widgets
import tkinter as tk
from tkinter import ttk, messagebox
from widgets import CircularProgress  # Widget personalizado para exibir progresso circular
from theme import Theme  # Gerencia temas visuais do aplicativo
from badges import BadgeEngine  # Motor para gerenciar conquistas (badges)
from dialogs import AvatarPicker  # Diálogo para selecionar avatares

# Define o avatar padrão inicial
DEFAULT_STARTER = "🌸"

# Classe que representa a aba de perfil do usuário
class ProfileTab(ttk.Frame):
    def __init__(self, parent, profile_repo):
        super().__init__(parent)  # Inicializa a classe base ttk.Frame
        self.repo = profile_repo  # Repositório de dados do perfil
        self.badges = BadgeEngine(self.repo)  # Inicializa o motor de conquistas

        # Configurações iniciais do repositório de perfil
        inv = self.repo.data.setdefault("avatar_inventory", [])  # Inventário de avatares
        if not inv:
            inv.append(DEFAULT_STARTER)  # Adiciona o avatar padrão se o inventário estiver vazio
        self.repo.data.setdefault("avatar_skin", inv[0])  # Define o avatar atual
        self.repo.data.setdefault("learning", "Java, Redes, POO")  # Define os tópicos de aprendizado
        self.repo.data.setdefault("badges", [])  # Lista de conquistas
        self.repo.data.setdefault("coins", 0)  # Moedas do usuário
        self.repo.data.setdefault("level", 1)  # Nível do usuário
        self.repo.data.setdefault("xp", 0)  # Experiência do usuário
        self.repo._save()  # Salva as configurações iniciais

        # ===== Header com gradiente (Canvas) =====
        # Espaçador para ajustar o layout
        spacer = ttk.Frame(self)
        spacer.pack(fill=tk.X)
        spacer.configure(height=8)
        spacer.pack_propagate(False)

        # ===== Card principal =====
        card = ttk.Frame(self, style="Card.TFrame")  # Card principal que contém as informações do perfil
        card.pack(padx=12, pady=(8,10), fill=tk.X)

        # Linha 1: Avatar + Nome + Meta
        row1 = ttk.Frame(card, style="Card.TFrame")  # Linha que contém o avatar e informações do usuário
        row1.pack(fill=tk.X, padx=12, pady=10)

        # Avatar grande + botões
        left = ttk.Frame(row1, style="Card.TFrame")  # Área para o avatar e botões relacionados
        left.pack(side=tk.LEFT, padx=(0,16))
        self.avatar_lbl = ttk.Label(left, text=self.cur_avatar(), font=("Segoe UI Emoji", 62))  # Exibe o avatar atual
        self.avatar_lbl.pack()
        btns = ttk.Frame(left, style="Card.TFrame")  # Botões para trocar ou randomizar o avatar
        btns.pack(pady=6)
        ttk.Button(btns, text="Trocar avatar…", style="Accent.TButton", command=self.open_avatar_picker).pack(side=tk.LEFT)
        ttk.Button(btns, text="Aleatório", command=self.random_avatar).pack(side=tk.LEFT, padx=6)

        # Nome + meta
        mid = ttk.Frame(row1, style="Card.TFrame")  # Área para o nome e meta do usuário
        mid.pack(side=tk.LEFT, expand=True, fill=tk.X)
        title = ttk.Label(mid, text="Meu Perfil", style="Header.TLabel")  # Título "Meu Perfil"
        title.pack(anchor="w")
        name_row = ttk.Frame(mid)  # Linha para editar e salvar o nome do usuário
        name_row.pack(anchor="w", pady=(8,4))
        ttk.Label(name_row, text="Nome:").pack(side=tk.LEFT)
        self.name_var = tk.StringVar(value=self.repo.data.get("name","Usuário"))  # Campo de entrada para o nome
        e = ttk.Entry(name_row, textvariable=self.name_var, width=24)
        e.pack(side=tk.LEFT, padx=6)
        ttk.Button(name_row, text="Salvar", command=self.save_name).pack(side=tk.LEFT)

        self.meta_lbl = ttk.Label(mid, text=self.meta_text(), style="Sub.TLabel")  # Exibe a meta do usuário
        self.meta_lbl.pack(anchor="w")

        # Level progress
        prog = ttk.Frame(card, style="Card.TFrame")  # Área para exibir o progresso de nível
        prog.pack(fill=tk.X, padx=12, pady=(0,12))
        self.cp = CircularProgress(prog, size=180)  # Widget de progresso circular
        self.cp.pack(side=tk.LEFT)
        info_col = ttk.Frame(prog, style="Card.TFrame")  # Coluna de informações sobre o progresso
        info_col.pack(side=tk.LEFT, padx=14)
        self.cp.set_progress(min(0.99, self.repo.data.get("xp",0)/100))  # Define o progresso atual
        self.cp.set_time_text(f"XP {self.repo.data.get('xp',0)}/100")  # Exibe o XP atual
        ttk.Label(info_col, text="Progresso para o próximo nível", style="Sub.TLabel").pack(anchor="w", pady=(8,0))
        ttk.Label(info_col, text="Ganhe XP concluindo tarefas, estudando flashcards e jogando.", wraplength=380).pack(anchor="w")

        # “O que estou aprendendo”
        learn = ttk.Labelframe(self, text="O que estou aprendendo")  # Área para editar tópicos de aprendizado
        learn.pack(fill=tk.X, padx=12, pady=(0,10))
        self.learn_var = tk.StringVar(value=self.repo.data.get("learning"))
        ttk.Entry(learn, textvariable=self.learn_var).pack(side=tk.LEFT, padx=6, pady=6, fill=tk.X, expand=True)
        ttk.Button(learn, text="Salvar", style="Accent.TButton", command=self.save_learning).pack(side=tk.LEFT, padx=6)

        # Inventário de avatares (mini-grid)
        inv_box = ttk.Labelframe(self, text="Avatares desbloqueados")  # Área para exibir avatares desbloqueados
        inv_box.pack(fill=tk.X, padx=12, pady=(0,10))
        self.inv_frame = ttk.Frame(inv_box)  # Grid de avatares
        self.inv_frame.pack(fill=tk.X, padx=8, pady=6)

        # Badges (conquistas)
        bad_box = ttk.Labelframe(self, text="Conquistas")  # Área para exibir conquistas
        bad_box.pack(fill=tk.X, padx=12, pady=(0,10))
        self.badges_frame = ttk.Frame(bad_box, style="Card.TFrame")
        self.badges_frame.pack(fill=tk.X, padx=8, pady=6)

        # barra superior direita com "Atualizar"
        topbar = ttk.Frame(self)  # Botão para atualizar a aba
        topbar.place(relx=1.0, y=8, anchor="ne")
        ttk.Button(topbar, text="Atualizar", command=self.refresh).pack()

        self.refresh()  # Atualiza a interface inicial

    # ===== helpers =====

    def cur_avatar(self):
        return self.repo.data.get("avatar_skin", DEFAULT_STARTER)  # Retorna o avatar atual

    def meta_text(self):
        coins = self.repo.data.get("coins",0)  # Moedas do usuário
        lvl = self.repo.data.get("level",1)  # Nível do usuário
        xp = self.repo.data.get("xp",0)  # XP do usuário
        return f"Nível {lvl} • XP {xp}/100 • Moedas {coins}"  # Texto formatado com meta

    def _render_inventory(self):
        for w in self.inv_frame.winfo_children(): w.destroy()  # Limpa o inventário atual
        inv = self.repo.data.get("avatar_inventory", [])
        if not inv:
            ttk.Label(self.inv_frame, text="Sem avatares. Compre na Loja!").pack()
            return
        for i, emoji in enumerate(inv):
            ttk.Button(self.inv_frame, text=emoji, width=3,
                       command=lambda e=emoji: self.set_avatar(e)).grid(row=i//16, column=i%16, padx=2, pady=2)

    def _render_badges(self):
        for w in self.badges_frame.winfo_children(): w.destroy()  # Limpa as conquistas atuais
        got = set(self.repo.data.get("badges", []))  # Conquistas obtidas
        pool = self.badges.all_badges()  # Todas as conquistas disponíveis

        if not pool:
            ttk.Label(self.badges_frame, text="(Sem conquistas ainda)").pack()
            return

        for i, b in enumerate(pool):
            owned = b["key"] in got  # Verifica se a conquista foi obtida
            txt = f'{b["icon"]} {b["name"]}'
            style = "Accent.TButton" if owned else "TButton"
            btn = ttk.Button(self.badges_frame, text=txt, style=style)
            btn.grid(row=i//6, column=i%6, padx=4, pady=4, sticky="w")

    # ===== actions =====
    def set_avatar(self, emoji):
        self.repo.data["avatar_skin"] = emoji  # Define o avatar atual
        self.repo._save(); self.refresh()

    def random_avatar(self):
        inv = self.repo.data.get("avatar_inventory", [])
        if not inv:
            messagebox.showinfo("Avatar", "Sem avatares no inventário.")
            return
        import random
        self.set_avatar(random.choice(inv))  # Escolhe um avatar aleatório

    def save_name(self):
        self.repo.data["name"] = self.name_var.get().strip() or "Usuário"  # Salva o nome do usuário
        self.repo._save(); self.refresh()

    def save_learning(self):
        self.repo.data["learning"] = self.learn_var.get().strip()  # Salva os tópicos de aprendizado
        self.repo._save(); self.refresh()

    def open_avatar_picker(self):
        dlg = AvatarPicker(self, self.repo)  # Abre o diálogo para selecionar avatares
        self.wait_window(dlg.win)
        if dlg.result:
            self.set_avatar(dlg.result)  # Define o avatar selecionado

    def refresh(self):
        self.avatar_lbl.configure(text=self.cur_avatar())  # Atualiza o avatar exibido
        self.meta_lbl.configure(text=self.meta_text())  # Atualiza a meta exibida
        xp = self.repo.data.get("xp",0)
        self.cp.set_progress(min(0.99, xp/100))  # Atualiza o progresso de XP
        self.cp.set_time_text(f"XP {xp}/100")
        self._render_inventory()  # Atualiza o inventário de avatares
        self._render_badges()  # Atualiza as conquistas
