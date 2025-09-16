# flashcards_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
from deck_repo import DeckRepo
from dialogs import DeckDialog, CardDialog
from widgets import CoinFloat
from utils import today_str

class DeckSelector(tk.Toplevel):
    """Janela para escolher um baralho."""
    def __init__(self, parent, repo: DeckRepo, on_pick):
        super().__init__(parent)
        self.title("Selecionar Baralho")
        self.resizable(False, False)
        self.repo = repo
        self.on_pick = on_pick

        frame = ttk.Frame(self, style="Card.TFrame"); frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        ttk.Label(frame, text="Escolha um baralho:", style="Header.TLabel").pack(anchor="w", pady=4)
        self.listbox = tk.Listbox(frame, height=10)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        decks = self.repo.list_decks()
        for d in decks:
            self.listbox.insert(tk.END, d.name)

        bar = ttk.Frame(frame); bar.pack(fill=tk.X, pady=6)
        ttk.Button(bar, text="Novo", command=self.new_deck).pack(side=tk.LEFT)
        ttk.Button(bar, text="Excluir", command=self.delete_deck).pack(side=tk.LEFT, padx=4)
        ttk.Button(bar, text="Selecionar", style="Accent.TButton", command=self.pick).pack(side=tk.RIGHT)

    def current_name(self):
        sel = self.listbox.curselection()
        if not sel: return None
        return self.listbox.get(sel[0])

    def new_deck(self):
        dlg = DeckDialog(self, initial={"name": "Novo Deck"})
        self.wait_window(dlg.win)
        if dlg.result and dlg.result.get("name"):
            self.repo.create_deck(dlg.result["name"])
            self.refresh()

    def delete_deck(self):
        name = self.current_name()
        if not name: return
        if messagebox.askyesno("Excluir", f"Apagar baralho '{name}'?"):
            self.repo.delete_deck(name)
            self.refresh()

    def refresh(self):
        self.listbox.delete(0, tk.END)
        for d in self.repo.list_decks():
            self.listbox.insert(tk.END, d.name)

    def pick(self):
        name = self.current_name()
        if not name: return
        self.on_pick(name)
        self.destroy()

class CardManager(tk.Toplevel):
    """Janela para criar/editar/excluir cartões do baralho atual."""
    def __init__(self, parent, repo: DeckRepo, deck):
        super().__init__(parent)
        self.title(f"Cartões — {deck.name}")
        self.resizable(False, False)
        self.repo = repo
        self.deck = deck

        frame = ttk.Frame(self, style="Card.TFrame"); frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.listbox = tk.Listbox(frame, width=50, height=12)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.refresh()

        right = ttk.Frame(frame, style="Card.TFrame"); right.pack(side=tk.LEFT, fill=tk.Y, padx=8)
        ttk.Button(right, text="＋ Novo", style="Accent.TButton", command=self.add).pack(fill=tk.X, pady=2)
        ttk.Button(right, text="✎ Editar", command=self.edit).pack(fill=tk.X, pady=2)
        ttk.Button(right, text="🗑 Excluir", command=self.delete).pack(fill=tk.X, pady=2)
        ttk.Button(right, text="Fechar", command=self.destroy).pack(fill=tk.X, pady=12)

    def refresh(self):
        self.listbox.delete(0, tk.END)
        for i, c in enumerate(self.deck.cards):
            self.listbox.insert(tk.END, f"[{i+1}] {c.front}  →  {c.back}")

    def _idx(self):
        s = self.listbox.curselection()
        return s[0] if s else None

    def add(self):
        dlg = CardDialog(self)
        self.wait_window(dlg.win)
        if dlg.result and dlg.result.get("front") and dlg.result.get("back"):
            self.repo.add_card(self.deck, dlg.result["front"], dlg.result["back"])
            self.refresh()

    def edit(self):
        i = self._idx()
        if i is None: return
        c = self.deck.cards[i]
        dlg = CardDialog(self, initial={"front": c.front, "back": c.back})
        self.wait_window(dlg.win)
        if dlg.result:
            self.repo.update_card(self.deck, i, dlg.result.get("front"), dlg.result.get("back"))
            self.refresh()

    def delete(self):
        i = self._idx()
        if i is None: return
        self.repo.delete_card(self.deck, i)
        self.refresh()

class FlashcardsTab(ttk.Frame):
    def __init__(self, parent, profile):
        super().__init__(parent)
        self.profile = profile
        self.repo = DeckRepo()
        self.decks = self.repo.list_decks()
        self.deck_i = 0
        self.deck = self.decks[self.deck_i]
        self.idx = 0
        self.front = True
        self.streak = 0
        self.session_hits = 0; self.session_total = 0
        self.mode_mcq = True  # modo padrão: múltipla escolha

        header = ttk.Frame(self); header.pack(fill=tk.X, pady=6)
        ttk.Label(header, text="Flashcards", style="Header.TLabel").pack(side=tk.LEFT, padx=8)
        ttk.Button(header, text="Selecionar Baralho", command=self.open_selector).pack(side=tk.LEFT, padx=4)
        ttk.Button(header, text="Gerenciar Cartões", command=self.open_manager).pack(side=tk.LEFT, padx=4)
        ttk.Button(header, text="Trocar para Texto" , command=self.toggle_mode).pack(side=tk.RIGHT, padx=4)

        info = ttk.Frame(self); info.pack(fill=tk.X)
        self.lbl_deck = ttk.Label(info, text=f"Deck: {self.deck.name}")
        self.lbl_deck.pack(side=tk.LEFT, padx=8)
        self.lbl_streak = ttk.Label(info, text="Streak: 0")
        self.lbl_streak.pack(side=tk.LEFT, padx=8)

        # cartão
        self.canvas = tk.Canvas(self, width=640, height=320, bg="#FFFFFF", highlightthickness=0)
        self.canvas.pack(pady=10)
        self.card_bg = self.canvas.create_rectangle(20,20,620,300, fill="#FFFBFF", outline="#E9E1FF", width=2)
        txt = self.deck.cards[self.idx].front if self.deck.cards else "(vazio)"
        self.text = self.canvas.create_text(320,140, text=txt, font=("TkDefaultFont", 18, "bold"))

        # barra de ações
        self.bar = ttk.Frame(self); self.bar.pack(pady=6)
        self._build_controls()

    # ----------- controles dinâmicos -----------
    def _build_controls(self):
        for w in self.bar.winfo_children(): w.destroy()
        if self.mode_mcq:
            self.btns = []
            for _ in range(4):
                b = ttk.Button(self.bar, text="...", command=lambda bb=len(self.btns): self.answer(bb))
                self.btns.append(b)
            for b in self.btns: b.pack(side=tk.LEFT, padx=6)

            ttk.Button(self.bar, text="Próximo", command=self.next_card).pack(side=tk.LEFT, padx=10)
            self._prepare_mcq()
        else:
            ttk.Button(self.bar, text="Virar", command=self.flip).pack(side=tk.LEFT, padx=4)
            ttk.Button(self.bar, text="Acertei", style="Accent.TButton", command=lambda: self.grade(True)).pack(side=tk.LEFT, padx=6)
            ttk.Button(self.bar, text="Errei", command=lambda: self.grade(False)).pack(side=tk.LEFT, padx=6)
            ttk.Button(self.bar, text="Próximo", command=self.next_card).pack(side=tk.LEFT, padx=10)

    def toggle_mode(self):
        self.mode_mcq = not self.mode_mcq
        self._build_controls()

    # ----------- deck management -----------
    def open_selector(self):
        DeckSelector(self, self.repo, on_pick=self._select_deck)

    def _select_deck(self, name: str):
        # recarrega
        decks = self.repo.list_decks()
        for i, d in enumerate(decks):
            if d.name == name:
                self.decks = decks
                self.deck_i = i
                self.deck = d
                break
        self.idx = 0; self.front = True; self.streak = 0
        self.lbl_deck.configure(text=f"Deck: {self.deck.name}")
        self.lbl_streak.configure(text="Streak: 0")
        self._update_text()

        # se estiver em MCQ, preparar alternativas do novo deck
        if self.mode_mcq: self._prepare_mcq()

    def open_manager(self):
        CardManager(self, self.repo, self.deck)

    # ----------- estudo: modo MCQ -----------
    def _prepare_mcq(self):
        if not self.deck.cards:
            for b in self.btns: b.configure(text="—", state="disabled")
            return
        c = self.deck.cards[self.idx]
        options = self.repo.mcq_options(self.deck, c.back, k=4)
        self._correct_text = c.back
        for i, b in enumerate(self.btns):
            b.configure(text=options[i], state="normal")

        self.front = True
        self.canvas.itemconfig(self.text, text=c.front)

    def answer(self, btn_index: int):
        if not self.deck.cards: return
        chosen = self.btns[btn_index].cget("text")
        correct = (chosen == self._correct_text)
        self._grade_internal(correct)

    # ----------- estudo: modo texto (acertou/errou) -----------
    def flip(self):
        if not self.deck.cards: return
        self.front = not self.front
        c = self.deck.cards[self.idx]
        self.canvas.itemconfig(self.text, text=c.front if self.front else c.back)

    def grade(self, correct: bool):
        if not self.deck.cards: return
        self._grade_internal(correct)

    # ----------- núcleo de pontuação -----------
    def _grade_internal(self, correct: bool):
        c = self.deck.cards[self.idx]
        self.session_total += 1
        if correct:
            self.session_hits += 1
            self.streak += 1
            base = 2 + min(self.streak, 5)  # combo até 5
            self.profile.add_rewards(coins=base, xp=2)  # +XP por acerto
            CoinFloat.show(self.winfo_toplevel(), f"+{base} 🪙", near_widget=self.canvas, offset=(0, -10))
            # SM-2 simplificado
            c.interval = max(1, int(round(c.interval * c.ease)))
            c.ease = max(1.3, c.ease + 0.1)
        else:
            self.streak = 0
            c.interval = 1
            c.ease = max(1.3, c.ease - 0.1)
        c.due = today_str()
        self.lbl_streak.configure(text=f"Streak: {self.streak}")
        self.next_card()

    def next_card(self):
        if not self.deck.cards:
            self.canvas.itemconfig(self.text, text="(vazio)"); return
        self.idx = (self.idx + 1) % len(self.deck.cards)
        self.front = True
        self._update_text()
        if self.mode_mcq: self._prepare_mcq()

    def _update_text(self):
        if not self.deck.cards:
            self.canvas.itemconfig(self.text, text="(vazio)")
        else:
            self.canvas.itemconfig(self.text, text=self.deck.cards[self.idx].front)
