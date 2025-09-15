from tkinter import ttk


PALETTE = {
"bg": "#F7F1FF", "card": "#FAFAFF", "primary": "#B388EB",
"accent": "#FFB3C1", "success": "#A7F3D0", "text": "#2D2235"
}


def apply(root):
    style = ttk.Style(root)
    root.configure(bg=PALETTE["bg"])
    style.theme_use("clam")
    style.configure("TFrame", background=PALETTE["bg"])
    style.configure("TLabel", background=PALETTE["bg"], foreground=PALETTE["text"])
    style.configure("TButton", padding=8)
    style.map("TButton", background=[("active", PALETTE["accent"])])
    style.configure("Accent.TButton", background=PALETTE["primary"], foreground="white")
    style.map("Accent.TButton", background=[("active", PALETTE["accent"])])