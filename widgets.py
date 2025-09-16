# widgets.py
# Importa o módulo tkinter para criar interfaces gráficas e o módulo math para cálculos matemáticos
import tkinter as tk
import math
from tkinter import ttk

# Tenta importar o módulo winsound para emitir sons no Windows
try:
    import winsound
    def _beep_ok():
        winsound.MessageBeep(winsound.MB_ICONASTERISK)  # Emite um som padrão
except Exception:
    def _beep_ok():
        # Fallback silencioso caso o winsound não esteja disponível
        pass

# Classe CircularProgress: Representa um widget de progresso circular
class CircularProgress(tk.Canvas):
    def __init__(self, master, size=160, thickness=14, **kw):
        super().__init__(master, width=size, height=size, highlightthickness=0, **kw)
        self.size = size  # Tamanho do widget
        self.thickness = thickness  # Espessura do círculo
        # Círculo de fundo
        self.bg_circle = self.create_oval(thickness, thickness, size-thickness, size-thickness,
                                          outline="#E6E6EA", width=thickness)
        # Arco de progresso
        self.fg_arc = self.create_arc(thickness, thickness, size-thickness, size-thickness,
                                      start=90, extent=0, style=tk.ARC, width=thickness)
        # Texto central
        self.text = self.create_text(size/2, size/2, text="00:00", font=("TkDefaultFont", 14, "bold"))

    def set_progress(self, ratio: float):
        # Define o progresso (0 a 1)
        self.itemconfig(self.fg_arc, extent=-360*max(0.0, min(1.0, ratio)))

    def set_time_text(self, s: str):
        # Define o texto central
        self.itemconfig(self.text, text=s)

# Classe BarChart: Representa um gráfico de barras
class BarChart(tk.Canvas):
    def __init__(self, master, width=520, height=200, **kw):
        super().__init__(master, width=width, height=height, highlightthickness=0, **kw)
        self.width = width  # Largura do gráfico
        self.height = height  # Altura do gráfico

    def draw(self, values, labels=None, bar_fill="#8B5CF6"):
        self.delete("all")  # Limpa o canvas
        if not values: return
        n = len(values)  # Número de barras
        w = self.width / (n * 1.5)  # Largura de cada barra
        maxv = max(values) or 1  # Valor máximo para normalização
        for i, v in enumerate(values):
            x = (i+1) * self.width / (n+1)  # Posição horizontal da barra
            h = (v / maxv) * (self.height - 30)  # Altura da barra
            # Desenha a barra
            self.create_rectangle(x-w/2, self.height-20-h, x+w/2, self.height-20,
                                  fill=bar_fill, width=0)
            if labels:
                # Adiciona rótulos abaixo das barras
                self.create_text(x, self.height-8, text=labels[i], font=("TkDefaultFont", 9), fill="#6B6B7A")
            # Adiciona valores acima das barras
            self.create_text(x, self.height-30-h-10, text=str(v), font=("TkDefaultFont", 9))

# Classe CoinFloat: Mostra um texto flutuante (ex.: '+10 🪙') que sobe e desaparece
class CoinFloat(tk.Toplevel):
    """
    Toplevel minimalista que mostra um texto (ex.: '+10 🪙') subindo e desaparecendo.
    Uso: CoinFloat.show(parent, '+10 🪙', near_widget=<widget>, offset=(0, -30))
    """
    def __init__(self, parent, text="+10 🪙", x=100, y=100, fg="#FFD166", bg=None):
        super().__init__(parent)
        self.overrideredirect(True)  # Remove bordas da janela
        self.attributes("-topmost", True)  # Garante que a janela fique no topo

        # Define a posição inicial
        self.geometry(f"+{x}+{y}")

        # Define o fundo da janela
        if bg is None:
            try:
                bg = parent.cget("bg")
            except Exception:
                bg = "#000000"  # Fallback neutro
        self.configure(bg=bg)

        # Canvas para desenhar o texto
        self.canvas = tk.Canvas(self, width=140, height=44, bg=bg, highlightthickness=0, bd=0)
        self.canvas.pack()

        # Texto flutuante
        self.item = self.canvas.create_text(70, 22, text=text,
                                            font=("TkDefaultFont", 14, "bold"),
                                            fill=fg)

        # Configurações da animação
        self.dy = -2  # Velocidade vertical (sobe 2px por frame)
        self.alpha = 0.98  # Transparência inicial
        self.attributes("-alpha", self.alpha)

        _beep_ok()  # Emite som (se disponível)
        self.after(0, self._step)  # Inicia a animação

    def _step(self):
        # Move o texto para cima
        self.canvas.move(self.item, 0, self.dy)

        # Reduz a transparência
        self.alpha -= 0.03
        if self.alpha <= 0.02:
            self.destroy()  # Destroi a janela quando invisível
            return
        try:
            self.attributes("-alpha", self.alpha)
        except Exception:
            self.destroy()
            return

        self.after(16, self._step)  # Atualiza a cada ~16ms (~60 FPS)

    @staticmethod
    def show(parent, text, near_widget=None, offset=(0, -30), fg="#FFD166"):
        # Calcula a posição inicial perto de um widget, se fornecido
        if near_widget is not None:
            nx = near_widget.winfo_rootx() + near_widget.winfo_width() // 2 + offset[0]
            ny = near_widget.winfo_rooty() + offset[1]
        else:
            nx = parent.winfo_rootx() + parent.winfo_width() // 2 + offset[0]
            ny = parent.winfo_rooty() + parent.winfo_height() // 2 + offset[1]
        # Usa o mesmo fundo do parent
        try:
            bg = parent.cget("bg")
        except Exception:
            bg = None
        CoinFloat(parent, text=text, x=nx, y=ny, fg=fg, bg=bg)

# Classe PlaceholderEntry: Entry com placeholder (cinza), que some ao focar
class PlaceholderEntry(ttk.Entry):
    """
    Entry com placeholder (cinza), que some ao focar.
    Use: PlaceholderEntry(parent, textvariable=..., placeholder="Digite aqui...")
    """
    def __init__(self, master=None, placeholder="", foreground=None, **kw):
        super().__init__(master, **kw)
        self.placeholder = placeholder
        self._ph_color = "#9AA0A6"
        self._fg_color = foreground
        self._has_placeholder = False
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        self._show_placeholder()

    def _show_placeholder(self):
        if (self.get() or "").strip(): 
            return
        self._has_placeholder = True
        self.configure(foreground=self._ph_color)
        self.delete(0, tk.END)
        self.insert(0, self.placeholder)

    def _clear_placeholder(self):
        if self._has_placeholder:
            self._has_placeholder = False
            self.configure(foreground=self._fg_color or "black")
            self.delete(0, tk.END)

    def _on_focus_in(self, _):
        self._clear_placeholder()

    def _on_focus_out(self, _):
        if not (self.get() or "").strip():
            self._show_placeholder()

    def get_value(self):
        return "" if self._has_placeholder else self.get()

# widgets.py — SUBSTITUIR TagChip e TagInput por estas versões

import tkinter as tk
from tags_repo import TagsRepo
import colorsys
import hashlib

def _hash_color(text: str) -> str:
    """
    Gera uma cor hex estável a partir do texto:
    - Hue vem do hash, Saturation/Vary controladas para cores fofas legíveis.
    """
    h = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
    hue = (h % 360) / 360.0
    sat = 0.45 + ((h >> 8) % 30) / 100.0   # 0.45..0.75
    val = 0.85                             # claro
    r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
    return "#%02x%02x%02x" % (int(r*255), int(g*255), int(b*255))

def _contrast_fg(hex_color: str) -> str:
    """Escolhe preto ou branco conforme luminância da cor de fundo."""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    # luminância relativa
    L = (0.2126*(r/255)**2.2 + 0.7152*(g/255)**2.2 + 0.0722*(b/255)**2.2)
    return "#000000" if L > 0.5 else "#FFFFFF"

# widgets.py — TAGS FOFOFAS (pílulas arredondadas com hover e cor)
import tkinter as tk
from tags_repo import TagsRepo
import colorsys, hashlib, re

def _hash_color(text: str) -> str:
    """Cor pastel estável por tag."""
    h = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
    hue = (h % 360) / 360
    sat = 0.42 + ((h >> 8) % 18) / 100.0   # 0.42..0.60
    val = 0.90                             # claro
    r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
    return "#%02x%02x%02x" % (int(r*255), int(g*255), int(b*255))

def _mix(hex1: str, hex2: str, a: float) -> str:
    """Mistura duas cores hex (0..1)."""
    def _c(h): return int(h,16)
    h1 = hex1.lstrip("#"); h2 = hex2.lstrip("#")
    r = int(_c(h1[0:2])*(1-a) + _c(h2[0:2])*a)
    g = int(_c(h1[2:4])*(1-a) + _c(h2[2:4])*a)
    b = int(_c(h1[4:6])*(1-a) + _c(h2[4:6])*a)
    return f"#{r:02x}{g:02x}{b:02x}"

def _contrast_fg(hex_color: str) -> str:
    """Preto ou branco conforme luminância."""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)/255
    g = int(hex_color[2:4], 16)/255
    b = int(hex_color[4:6], 16)/255
    # luminância perceptual simples
    L = 0.2126*r*r + 0.7152*g*g + 0.0722*b*b
    return "#000000" if L > 0.46 else "#FFFFFF"

def _rounded_rect(canvas: tk.Canvas, x1, y1, x2, y2, r, **kw):
    """Desenha retângulo arredondado no Canvas."""
    # corpo
    items = []
    items.append(canvas.create_rectangle(x1+r, y1, x2-r, y2, **kw))
    items.append(canvas.create_rectangle(x1, y1+r, x2, y2-r, **kw))
    # cantos
    items.append(canvas.create_oval(x1, y1, x1+2*r, y1+2*r, **kw))
    items.append(canvas.create_oval(x2-2*r, y1, x2, y1+2*r, **kw))
    items.append(canvas.create_oval(x1, y2-2*r, x1+2*r, y2, **kw))
    items.append(canvas.create_oval(x2-2*r, y2-2*r, x2, y2, **kw))
    return items

class TagChip(tk.Canvas):
    """
    Pílula fofinha com cor pastel, hover glow e botão 'x'.
    on_remove(tag), on_drag_start(tag), on_drag_over(tag), on_drag_end(tag) são callbacks do TagInput.
    """
    def __init__(self, master, text, on_remove, on_drag_start=None, on_drag_over=None, on_drag_end=None):
        self.text = text
        self.bg = _hash_color(text)
        self.fg = _contrast_fg(self.bg)
        super().__init__(master, width=1, height=1, bg=master.cget("bg"), highlightthickness=0, bd=0)
        self.on_remove = on_remove
        self._drag_start_cb = on_drag_start
        self._drag_over_cb  = on_drag_over
        self._drag_end_cb   = on_drag_end

        # desenha
        padx, pady = 10, 6
        txt_id = self.create_text(0, 0, text=text, fill=self.fg, font=("Segoe UI", 9, "bold"), anchor="w")
        bbox = self.bbox(txt_id)
        w_text = bbox[2]-bbox[0]
        h_text = bbox[3]-bbox[1]
        pill_w = w_text + 2*padx + 18   # espaço pro 'x'
        pill_h = h_text + 2*pady

        self.config(width=pill_w, height=pill_h)
        # sombra (bem leve)
        _rounded_rect(self, 2, 2, pill_w, pill_h, 12, fill=_mix(self.bg, "#000000", 0.08), outline="")
        # pílula
        self.pill = _rounded_rect(self, 0, 0, pill_w-2, pill_h-2, 12, fill=self.bg, outline="")
        # texto centralizado vertical
        self.coords(txt_id, padx, pill_h//2)
        self.itemconfigure(txt_id, anchor="w")

        # botão 'x' circular
        x_r = 9
        cx = pill_w - (x_r + 6)
        cy = pill_h//2
        self.btn_circle = self.create_oval(cx-x_r, cy-x_r, cx+x_r, cy+x_r, fill=_mix(self.bg, "#000000", 0.12), outline="")
        self.btn_x = self.create_text(cx, cy, text="×", fill=self.fg, font=("Segoe UI", 9, "bold"))

        # binds
        for tag in ("<Enter>", "<Leave>"):
            self.bind(tag, self._hover)
        for ev in ("<Button-1>", "<B1-Motion>", "<ButtonRelease-1>"):
            self.bind(ev, self._drag_events)
        # clique no x
        self.tag_bind(self.btn_circle, "<Button-1>", lambda e: self.on_remove(self.text))
        self.tag_bind(self.btn_x,      "<Button-1>", lambda e: self.on_remove(self.text))

    def _hover(self, e):
        if e.type == "7":  # Enter
            # brilho leve
            for it in self.pill:
                self.itemconfigure(it, fill=_mix(self.bg, "#FFFFFF", 0.10))
        else:  # Leave
            for it in self.pill:
                self.itemconfigure(it, fill=self.bg)

    def _drag_events(self, e):
        # notifica o container (swap simples ao passar por cima)
        if e.type == tk.EventType.ButtonPress:
            if self._drag_start_cb: self._drag_start_cb(self.text)
        elif e.type == tk.EventType.Motion:
            if self._drag_over_cb:  self._drag_over_cb(self.text)
        elif e.type == tk.EventType.ButtonRelease:
            if self._drag_end_cb:   self._drag_end_cb(self.text)

class TagInput(ttk.Frame):
    """
    Caixa de tags estilo Notion:
      • chips fofas (TagChip) com cores;
      • Enter/',' cria, clique no '×' remove;
      • sugestões globais (TagsRepo) com drop-down;
      • arrastar um chip por cima de outro troca a ordem.
    """
    def __init__(self, master, initial=None, repo: TagsRepo | None = None):
        super().__init__(master, style="Card.TFrame")
        self.repo = repo or TagsRepo()
        self.tags: list[str] = []
        self.dragging: str | None = None

        # caixa externa com borda fininha
        self.box = tk.Frame(self, bg=self.master.cget("background"),
                            highlightthickness=1, highlightbackground="#D9D9EC")
        self.box.pack(fill=tk.X, padx=2, pady=2)

        # linha de chips
        self.chips = tk.Frame(self.box, bg=self.master.cget("background"))
        self.chips.pack(fill=tk.X, padx=8, pady=(6, 2))

        # linha de input
        inp = tk.Frame(self.box, bg=self.master.cget("background"))
        inp.pack(fill=tk.X, padx=8, pady=(0, 6))
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(inp, textvariable=self.entry_var, bd=0, highlightthickness=0)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_ph = "ex.: estudo, java, prova"
        self._ph_on = False
        self._show_ph()
        self.entry.bind("<FocusIn>", lambda e: self._clear_ph())
        self.entry.bind("<FocusOut>", lambda e: (self._create_from_entry(), self._show_ph()))
        self.entry.bind("<Return>", self._create_from_entry)
        self.entry.bind("<KP_Enter>", self._create_from_entry)
        self.entry.bind(",", self._create_from_entry)
        self.entry.bind("<KeyRelease>", self._on_typing)

        # dropdown de sugestões
        self.dropdown = None

        self.set_tags(initial or [])

    # ---------- placeholder ----------
    def _show_ph(self):
        if (self.entry_var.get() or "").strip(): return
        self.entry.configure(fg="#9AA0A6")
        self.entry_var.set(self.entry_ph); self._ph_on = True

    def _clear_ph(self):
        if self._ph_on:
            self.entry.configure(fg="black")
            self.entry_var.set(""); self._ph_on = False

    # ---------- sugestões ----------
    def _on_typing(self, _=None):
        if self._ph_on: self._close_dropdown(); return
        txt = self.entry_var.get().strip()
        if not txt:
            self._close_dropdown(); return
        sugg = [s for s in self.repo.suggestions(txt) if s not in self.tags]
        if not sugg:
            self._close_dropdown(); return
        self._open_dropdown(sugg)

    def _open_dropdown(self, items):
        self._close_dropdown()
        self.dropdown = tk.Toplevel(self)
        self.dropdown.overrideredirect(True); self.dropdown.attributes("-topmost", True)

        self.update_idletasks()
        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height()
        self.dropdown.geometry(f"+{x}+{y}")

        lb = tk.Listbox(self.dropdown, height=min(8, len(items)))
        for it in items: lb.insert(tk.END, it)
        lb.pack()
        lb.bind("<Button-1>", lambda e, lb=lb: self._pick_from_list(lb))
        lb.bind("<Return>",   lambda e, lb=lb: self._pick_from_list(lb))

    def _close_dropdown(self):
        if self.dropdown and self.dropdown.winfo_exists(): self.dropdown.destroy()
        self.dropdown = None

    def _pick_from_list(self, lb):
        try:
            idx = lb.curselection()[0]; value = lb.get(idx)
        except Exception:
            return
        self._add_tag(value); self._close_dropdown()
        self.entry_var.set(""); self._ph_on = False

    # ---------- criar/remover ----------
    def _create_from_entry(self, _=None):
        if self._ph_on: return
        raw = self.entry_var.get().strip().strip(",")
        if not raw: return
        parts = [p.strip() for p in re.split(r"[,\s]+", raw) if p.strip()]
        for p in parts: self._add_tag(p)
        self.entry_var.set(""); self._ph_on = False; self._close_dropdown()

    def _add_tag(self, t: str):
        if t in self.tags: return
        self.tags.append(t)
        chip = TagChip(self.chips, t,
                       on_remove=self._remove_tag,
                       on_drag_start=self._drag_start,
                       on_drag_over=self._drag_over,
                       on_drag_end=self._drag_end)
        chip.pack(side=tk.LEFT, padx=4, pady=2)
        self.repo.add_many([t])

    def _remove_tag(self, t: str):
        self.tags = [x for x in self.tags if x != t]
        for w in self.chips.winfo_children(): w.destroy()
        for t2 in self.tags:
            TagChip(self.chips, t2,
                    on_remove=self._remove_tag,
                    on_drag_start=self._drag_start,
                    on_drag_over=self._drag_over,
                    on_drag_end=self._drag_end)\
                .pack(side=tk.LEFT, padx=4, pady=2)

    # ---------- drag & drop (swap ao passar por cima) ----------
    def _drag_start(self, tag: str):
        self.dragging = tag

    def _drag_over(self, target_tag: str):
        if not self.dragging or target_tag == self.dragging: return
        try:
            i = self.tags.index(self.dragging); j = self.tags.index(target_tag)
        except ValueError:
            return
        if i == j: return
        self.tags[i], self.tags[j] = self.tags[j], self.tags[i]
        for w in self.chips.winfo_children(): w.destroy()
        for t in self.tags:
            TagChip(self.chips, t,
                    on_remove=self._remove_tag,
                    on_drag_start=self._drag_start,
                    on_drag_over=self._drag_over,
                    on_drag_end=self._drag_end)\
                .pack(side=tk.LEFT, padx=4, pady=2)

    def _drag_end(self, _=None):
        self.dragging = None

    # ---------- API ----------
    def set_tags(self, tags):
        self.tags = []
        for w in self.chips.winfo_children(): w.destroy()
        for t in tags: self._add_tag(t)

    def get_tags(self):
        return list(self.tags)

import tkinter as tk
from tkinter import ttk

class ScrollableFrame(ttk.Frame):
    def __init__(self, master, height=420):
        super().__init__(master)
        # Canvas para rolagem
        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, height=height)
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vsb.grid(row=0, column=1, sticky="ns")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Frame interno para conteúdo
        self.body = ttk.Frame(self.canvas)
        self._window = self.canvas.create_window((0, 0), window=self.body, anchor="nw")

        # Atualiza a região de rolagem quando o conteúdo muda
        self.body.bind("<Configure>", self._on_body_configure)
        # Ajusta a largura do conteúdo ao canvas
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Configura rolagem do mouse
        self.body.bind("<Enter>", self._bind_mouse)
        self.body.bind("<Leave>", self._unbind_mouse)

    def _on_body_configure(self, _):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, evt):
        self.canvas.itemconfig(self._window, width=evt.width)

    def _on_mousewheel(self, event):
        # Rola o conteúdo com o mouse (compatível com Windows, Mac e Linux)
        if event.num == 4:   # Linux up
            self.canvas.yview_scroll(-3, "units")
        elif event.num == 5: # Linux down
            self.canvas.yview_scroll(3, "units")
        else:                # Windows/Mac
            delta = -1 if event.delta > 0 else 1
            self.canvas.yview_scroll(delta*3, "units")

    def _bind_mouse(self, _):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)   # Win/Mac
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mouse(self, _):
        self.canvas.unbind_all("<MouseWheel>")
