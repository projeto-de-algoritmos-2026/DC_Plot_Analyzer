import tkinter as tk
from tkinter import messagebox, filedialog
import re
from interp_text import interp_text

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

from count_inversions import count_inversions
from parser import parse_file
from point import Point
from stats import kendall_tau, spearman_rho

# ── Paleta ──────────────────────────────────────────────────────────────────
BG       = "#f0f2f5"
CARD     = "#ffffff"
HEADER   = "#1e272e"
ACCENT   = "#0984e3"
TEXT     = "#2d3436"
MUTED    = "#636e72"
BORDER   = "#dfe6e9"


def _metric_color(tau):
    if tau > 0.7:  return "#00b894"
    if tau > 0.3:  return "#55c599"
    if tau > -0.3: return "#fdcb6e"
    if tau > -0.7: return "#e17055"
    return "#d63031"


# ── Componentes ──────────────────────────────────────────────────────────────

class _Card(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=CARD, highlightthickness=1,
                         highlightbackground=BORDER, **kw)


class MetricCard(_Card):
    def __init__(self, parent, label, **kw):
        super().__init__(parent, **kw)
        tk.Label(self, text=label, font=("Segoe UI", 8), bg=CARD,
                 fg=MUTED).pack(anchor=tk.W, padx=10, pady=(8, 0))
        self._val = tk.Label(self, text="—", font=("Segoe UI", 20, "bold"),
                             bg=CARD, fg=TEXT)
        self._val.pack(anchor=tk.W, padx=10, pady=(0, 8))

    def set(self, text, color=TEXT):
        self._val.config(text=text, fg=color)


# ── Janela principal ─────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analisador de Inversões")
        self.geometry("980x640")
        self.minsize(760, 500)
        self.configure(bg=BG)
        self._build_ui()

    # ── Layout ───────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Cabeçalho
        hdr = tk.Frame(self, bg=HEADER)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="Analisador de Inversões",
                 font=("Segoe UI", 13, "bold"), bg=HEADER, fg="white",
                 padx=16, pady=10).pack(side=tk.LEFT)
        tk.Label(hdr, text="Kendall τ  ·  Spearman ρ  ·  D&C",
                 font=("Segoe UI", 9), bg=HEADER, fg="#b2bec3",
                 padx=16).pack(side=tk.RIGHT, pady=10)

        # Corpo
        body = tk.Frame(self, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

        left = tk.Frame(body, bg=BG, width=288)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        left.pack_propagate(False)

        right = tk.Frame(body, bg=BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_input(left)
        self._build_metrics(left)
        self._build_graph(right)

    def _build_input(self, parent):
        card = _Card(parent)
        card.pack(fill=tk.X, pady=(0, 10))

        tk.Label(card, text="Sequência de entrada",
                 font=("Segoe UI", 10, "bold"), bg=CARD, fg=TEXT
                 ).pack(anchor=tk.W, padx=10, pady=(10, 4))

        self._mode = tk.StringVar(value="simple")
        row = tk.Frame(card, bg=CARD)
        row.pack(anchor=tk.W, padx=10, pady=(0, 6))
        for label, val in [("Valores simples", "simple"), ("Pares X, Y", "pairs")]:
            tk.Radiobutton(row, text=label, variable=self._mode, value=val,
                           bg=CARD, fg=TEXT, font=("Segoe UI", 9),
                           activebackground=CARD, selectcolor=CARD
                           ).pack(side=tk.LEFT, padx=(0, 8))

        self._txt = tk.Text(card, height=5, font=("Consolas", 10),
                            relief=tk.FLAT, bd=0, bg="#f8f9fa", fg=TEXT,
                            insertbackground=TEXT, padx=6, pady=6,
                            highlightthickness=1, highlightbackground=BORDER)
        self._txt.pack(fill=tk.X, padx=10, pady=(0, 4))
        self._txt.insert("1.0", "5 3 1 4 2")

        tk.Label(card, text="Separe por espaços ou vírgulas",
                 font=("Segoe UI", 8), bg=CARD, fg=MUTED
                 ).pack(anchor=tk.W, padx=10, pady=(0, 4))

        btn_row = tk.Frame(card, bg=CARD)
        btn_row.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Button(btn_row, text="Analisar",
                  font=("Segoe UI", 10, "bold"),
                  bg=ACCENT, fg="white", relief=tk.FLAT,
                  padx=14, pady=5, cursor="hand2", bd=0,
                  activebackground="#0773c5", activeforeground="white",
                  command=self._analyze).pack(side=tk.LEFT)

        tk.Button(btn_row, text="Carregar arquivo",
                  font=("Segoe UI", 9),
                  bg=BORDER, fg=TEXT, relief=tk.FLAT,
                  padx=10, pady=5, cursor="hand2", bd=0,
                  command=self._load_file).pack(side=tk.LEFT, padx=(8, 0))

    def _build_metrics(self, parent):
        tk.Label(parent, text="MÉTRICAS", font=("Segoe UI", 8, "bold"),
                 bg=BG, fg=MUTED).pack(anchor=tk.W, pady=(0, 4))

        self._c_inv = MetricCard(parent, "Inversões")
        self._c_inv.pack(fill=tk.X, pady=(0, 8))

        row = tk.Frame(parent, bg=BG)
        row.pack(fill=tk.X, pady=(0, 8))
        row.columnconfigure(0, weight=1)
        row.columnconfigure(1, weight=1)

        self._c_tau = MetricCard(row, "Kendall τ (tau)")
        self._c_tau.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        self._c_rho = MetricCard(row, "Spearman ρ (rho)")
        self._c_rho.grid(row=0, column=1, sticky="ew")

        self._lbl_interp = tk.Label(parent, text="",
                                    font=("Segoe UI", 9, "italic"),
                                    bg=BG, fg=MUTED,
                                    wraplength=264, justify=tk.LEFT)
        self._lbl_interp.pack(anchor=tk.W)

    def _build_graph(self, parent):
        if not HAS_MPL:
            tk.Label(parent,
                     text="matplotlib não instalado.\n\npip install matplotlib",
                     bg=BG, fg="#d63031", font=("Segoe UI", 11)
                     ).pack(expand=True)
            return

        self._fig = Figure(dpi=100, facecolor=BG)
        self._canvas = FigureCanvasTkAgg(self._fig, master=parent)
        widget = self._canvas.get_tk_widget()
        widget.pack(fill=tk.BOTH, expand=True)
        widget.bind("<Configure>", self._on_resize)
        self._draw_empty()

    # ── Eventos ──────────────────────────────────────────────────────────────

    def _on_resize(self, event):
        if not HAS_MPL:
            return
        w, h = event.width, event.height
        if w < 50 or h < 50:
            return
        dpi = self._fig.dpi
        new_w, new_h = w / dpi, h / dpi
        cur_w, cur_h = self._fig.get_size_inches()
        if abs(new_w - cur_w) < 0.1 and abs(new_h - cur_h) < 0.1:
            return
        self._fig.set_size_inches(new_w, new_h, forward=False)
        if self._fig.get_axes():
            self._fig.tight_layout()
        self._canvas.draw()

    def _load_file(self):
        path = filedialog.askopenfilename(
            title="Abrir arquivo de entrada",
            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")]
        )
        if not path:
            return
        try:
            pts = parse_file(path)
            self._txt.delete("1.0", tk.END)
            self._txt.insert("1.0", "\n".join(f"{p.x},{p.y}" for p in pts))
            self._mode.set("pairs")
        except Exception as exc:
            messagebox.showerror("Erro ao carregar", str(exc))

    def _analyze(self):
        try:
            pts = self._parse_input()
        except ValueError as exc:
            messagebox.showerror("Entrada inválida", str(exc))
            return

        y = [p.y for p in pts]
        if len(y) < 2:
            messagebox.showwarning("Aviso", "Mínimo de 2 elementos.")
            return

        n = len(y)
        inv = count_inversions(list(y))
        max_inv = n * (n - 1) // 2
        x_vals = [p.x for p in pts]
        tau = kendall_tau(y, x_vals)
        rho = spearman_rho(y, x_vals)
        color = _metric_color(tau)

        self._c_inv.set(f"{inv} / {max_inv}")
        self._c_tau.set(f"{tau:.4f}", color)
        self._c_rho.set(f"{rho:.4f}", color)
        self._lbl_interp.config(text=interp_text(tau))

        if HAS_MPL:
            self._draw_plot(pts, y, inv, tau, rho)

    # ── Parsing ──────────────────────────────────────────────────────────────

    def _parse_input(self):
        raw = self._txt.get("1.0", tk.END).strip()
        if not raw:
            raise ValueError("Entrada vazia.")

        if self._mode.get() == "simple":
            tokens = [t for t in re.split(r"[\s,]+", raw) if t]
            try:
                vals = [float(t) for t in tokens]
            except ValueError:
                raise ValueError("Todos os valores devem ser numéricos.")
            return [Point(float(i + 1), v) for i, v in enumerate(vals)]

        pts = []
        for i, line in enumerate(raw.splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            parts = [p for p in re.split(r"[\s,]+", line) if p]
            if len(parts) != 2:
                raise ValueError(
                    f"Linha {i}: esperado 2 valores, encontrado {len(parts)}."
                )
            try:
                pts.append(Point(float(parts[0]), float(parts[1])))
            except ValueError:
                raise ValueError(f"Linha {i}: valor não numérico.")
        if not pts:
            raise ValueError("Nenhum par encontrado.")
        pts.sort(key=lambda p: p.x)
        return pts

    # ── Gráfico ──────────────────────────────────────────────────────────────

    def _draw_empty(self):
        self._fig.clear()
        ax = self._fig.add_subplot(111)
        ax.set_facecolor(CARD)
        ax.text(0.5, 0.5,
                "Insira uma sequência e clique em Analisar",
                ha="center", va="center", fontsize=11,
                color="#b2bec3", transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        self._fig.tight_layout()
        self._canvas.draw()

    def _draw_plot(self, pts, y, inv, tau, rho):
        self._fig.clear()
        ax = self._fig.add_subplot(111)
        ax.set_facecolor(CARD)

        xs = [p.x for p in pts]
        sorted_y = sorted(y)
        color = _metric_color(tau)

        # Linha de referência (ordenada)
        ax.plot(xs, sorted_y,
                color="#b2bec3", linestyle="--", linewidth=1.5,
                label="Ordenada  (τ = 1.0)", zorder=1)

        # Sequência atual (apenas pontos, sem linha)
        ax.scatter(xs, y,
                   color=ACCENT, s=70, zorder=3,
                   label="Sequência atual")

        # Anotação dos valores se n ≤ 15
        if len(xs) <= 15:
            for xi, yi in zip(xs, y):
                ax.annotate(
                    f"{yi:g}",
                    (xi, yi),
                    textcoords="offset points",
                    xytext=(0, 8),
                    ha="center", fontsize=8, color=TEXT
                )

        xlabel = "X" if self._mode.get() == "pairs" else "Posição"
        ylabel = "Y" if self._mode.get() == "pairs" else "Valor"
        ax.set_xlabel(xlabel, fontsize=10, color=MUTED)
        ax.set_ylabel(ylabel, fontsize=10, color=MUTED)
        ax.set_title(
            f"Inversões: {inv}    ·    τ = {tau:.3f}    ·    ρ = {rho:.3f}",
            fontsize=11, fontweight="bold", color=TEXT, pad=10
        )

        legend = ax.legend(fontsize=9, framealpha=0.9, edgecolor=BORDER)
        legend.get_frame().set_facecolor(CARD)

        ax.grid(axis="y", linestyle="--", alpha=0.35, color=MUTED)
        ax.tick_params(colors=MUTED, labelsize=9)
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        for spine in ["bottom", "left"]:
            ax.spines[spine].set_color(BORDER)

        self._fig.tight_layout()
        self._canvas.draw()


if __name__ == "__main__":
    App().mainloop()
