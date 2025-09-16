# theme.py
from tkinter import ttk

# Paletas de temas
# theme.py — paletas com 'primary'
THEMES = {
    "princess": {
        "bg": "#F6F1FF",
        "fg": "#2D2A32",
        "accent": "#8B5CF6",
        "accent_fg": "#FFFFFF",
        "card": "#FFFFFF",
        "subtle": "#ECE8F9",
        "header_bg": "#8B5CF6",
        "header_fg": "#FFFFFF",
        "header_fg_sub": "#E9D5FF",
        "grad_1": "#A78BFA",
        # novo
        "primary": "#8B5CF6",         # igual ao accent
    },
    "dark": {
        "bg": "#101016",
        "fg": "#E5E7EB",
        "accent": "#7C3AED",
        "accent_fg": "#FFFFFF",
        "card": "#171923",
        "subtle": "#1F2430",
        "header_bg": "#1F2430",
        "header_fg": "#FFFFFF",
        "header_fg_sub": "#C4B5FD",
        "grad_1": "#7C3AED",
        # novo
        "primary": "#7C3AED",
    },
    "neon": {
        "bg": "#0B1020",
        "fg": "#E6FFFB",
        "accent": "#22D3EE",
        "accent_fg": "#001014",
        "card": "#0F172A",
        "subtle": "#111827",
        "header_bg": "#0F172A",
        "header_fg": "#E6FFFB",
        "header_fg_sub": "#67E8F9",
        "grad_1": "#22D3EE",
        # novo
        "primary": "#22D3EE",
    },
}



class Theme:
    current = "princess"
    palette = THEMES["princess"].copy()

    @classmethod
    def apply(cls, root, name: str):
        """Aplica tema ao root e configura estilos ttk."""
        pal = THEMES.get(name, THEMES["princess"]).copy()
        cls.current = name
        cls.palette = pal

        def _get(key, default):
            return pal.get(key, default)

        bg         = _get("bg", "#FFFFFF")
        fg         = _get("fg", "#000000")
        card       = _get("card", "#FFFFFF")
        accent     = _get("accent", "#7C3AED")
        accent_fg  = _get("accent_fg", "#FFFFFF")
        subtle     = _get("subtle", "#F3F4F6")

        try:
            style = ttk.Style(root)
            style.theme_use("clam")
        except Exception:
            style = ttk.Style()

        root.configure(bg=bg)

        # Base
        style.configure(".", background=bg, foreground=fg)

        # Frames
        style.configure("Card.TFrame", background=card)
        style.map("Card.TFrame", background=[("active", card)])

        # Labels
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("Header.TLabel", background=bg, foreground=fg, font=("Segoe UI", 18, "bold"))
        style.configure("Sub.TLabel", background=bg, foreground=_get("muted", "#6B7280"))

        # Buttons
        style.configure("TButton", foreground=fg, background=subtle, padding=6)
        style.map("TButton", background=[("active", _get("btn_active", subtle))])
        style.configure("Accent.TButton", background=accent, foreground=accent_fg, padding=8)
        style.map("Accent.TButton", background=[("active", _get("accent_active", accent))])

        # Entry
        style.configure("TEntry", fieldbackground="#FFFFFF", background="#FFFFFF", foreground=fg)

        # Treeview
        style.configure("Treeview", background="#fafafa", fieldbackground="#fafafa", foreground=fg)
        style.configure("Treeview.Heading", background=subtle, foreground=fg)

        # Progressbar
        style.configure("TProgressbar", background=accent, troughcolor=subtle)

    @classmethod
    def switch_theme(cls, root, name: str):
        """Troca o tema ao vivo e repinta widgets básicos."""
        cls.apply(root, name)
        from tkinter import Frame, Canvas, Toplevel
        for w in root.winfo_children():
            if isinstance(w, (Frame, Canvas, Toplevel, ttk.Frame)):
                try:
                    w.configure(bg=cls.palette.get("bg", "#fff"))
                except Exception:
                    pass

    @classmethod
    def header(cls, parent, title="StudyHub", subtitle="produtividade • estudos • games", height=88):
        """Cria um Canvas de header estilizado."""
        import tkinter as tk
        cvs = tk.Canvas(parent, height=height, highlightthickness=0, bd=0, bg=cls.palette.get("bg", "#fff"))
        cvs.pack(fill=tk.X)

        def paint(_=None):
            pal = cls.palette or {}
            header_bg  = pal.get("header_bg", "#8B5CF6")
            header_fg  = pal.get("header_fg", "#FFFFFF")
            header_sub = pal.get("header_fg_sub", "#E9D5FF")
            grad_1     = pal.get("grad_1", "#A78BFA")

            w = cvs.winfo_width()
            h = height
            cvs.delete("all")
            cvs.create_rectangle(0, 0, w, h, fill=header_bg, outline="")
            cvs.create_polygon(0, h, 220, 0, w, 0, w, h, fill=grad_1, outline="")
            cvs.create_text(18, int(h*0.62), anchor="w", text=title,
                            font=("Segoe UI", 26, "bold"), fill=header_fg)
            cvs.create_text(215, int(h*0.70), anchor="w", text=subtitle,
                            font=("Segoe UI", 12), fill=header_sub)

        cvs.bind("<Configure>", paint)
        paint()
        return cvs
