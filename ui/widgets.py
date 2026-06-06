"""
ui/widgets.py – Reusable themed widget factories.
"""
import tkinter as tk
from tkinter import ttk
from theme import (
    BG, PANEL, CARD, CARD2, BORDER, BORDER2, BORDER_HI,
    ACCENT, ACCENT_DK, ACCENT_LT,
    PURPLE, PURPLE_DK,
    TEXT, SUBTEXT, DIMTEXT,
    FONT_LABEL, FONT_BODY, FONT_MONO,
)


# ── Card ──────────────────────────────────────────────────────────────────────

def make_card(parent: tk.Widget, title: str,
              accent_color: str = None) -> tuple:
    accent_color = accent_color or ACCENT
    outer = tk.Frame(
        parent, bg=PANEL, bd=0,
        highlightbackground=BORDER2,
        highlightthickness=1,
    )
    tk.Frame(outer, bg=accent_color, width=3).pack(side="left", fill="y")

    right = tk.Frame(outer, bg=PANEL)
    right.pack(side="left", fill="both", expand=True)

    hdr = tk.Frame(right, bg="#0f0f18")   # slightly darker header band
    hdr.pack(fill="x")
    tk.Label(
        hdr, text=title.upper(),
        font=(FONT_LABEL[0], 7, "bold"),
        fg="#555570", bg="#0f0f18",
        anchor="w", padx=16, pady=10,
    ).pack(side="left", fill="x", expand=True)

    tk.Frame(right, bg=BORDER2, height=1).pack(fill="x")

    inner = tk.Frame(right, bg=PANEL, padx=16, pady=14)
    inner.pack(fill="both", expand=True)

    return outer, inner


# ── Styled entry ──────────────────────────────────────────────────────────────

def styled_entry(parent, textvariable=None, font=None, **kw):
    e = tk.Entry(
        parent,
        textvariable=textvariable,
        bg="#1a1a28", fg=TEXT,
        insertbackground=TEXT,
        relief="flat", bd=0,
        highlightbackground=BORDER2,
        highlightcolor=BORDER_HI,
        highlightthickness=1,
        font=font or FONT_BODY,
        **kw,
    )
    e.bind("<Enter>",    lambda _: e.config(highlightbackground=BORDER_HI))
    e.bind("<Leave>",    lambda _: e.config(highlightbackground=BORDER2))
    e.bind("<FocusIn>",  lambda _: e.config(highlightbackground=ACCENT_DK,
                                             highlightthickness=1))
    e.bind("<FocusOut>", lambda _: e.config(highlightbackground=BORDER2,
                                             highlightthickness=1))
    return e


# ── Styled button ─────────────────────────────────────────────────────────────

def styled_button(parent, text, command=None, accent=False,
                  color=None, **kw):
    if color:
        bg  = color
        abg = _darken(color)
        fg  = "white"
    elif accent:
        bg  = ACCENT
        abg = ACCENT_DK
        fg  = "white"
    else:
        bg  = "#222235"
        abg = "#2e2e48"
        fg  = SUBTEXT

    btn = tk.Button(
        parent, text=text,
        bg=bg, fg=fg,
        activebackground=abg,
        activeforeground="white",
        relief="flat",
        font=(FONT_LABEL[0], 9),
        cursor="hand2",
        command=command,
        **kw,
    )
    btn.bind("<Enter>", lambda _: btn.config(bg=abg, fg="white"))
    btn.bind("<Leave>", lambda _: btn.config(bg=bg,  fg=fg))
    return btn


def _darken(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r, g, b = max(0, int(r*0.75)), max(0, int(g*0.75)), max(0, int(b*0.75))
    return f"#{r:02x}{g:02x}{b:02x}"


# ── Dark combobox popup (replacement using tk.OptionMenu) ─────────────────────

class DarkCombo(tk.Frame):
    """
    A fully dark-themed dropdown that replaces ttk.Combobox.
    The popup listbox uses a black background so items are always readable.
    """
    POPUP_BG   = "#0d0d14"
    POPUP_FG   = "#e8e8f8"
    POPUP_SEL  = "#1e1e35"
    POPUP_HL   = ACCENT

    def __init__(self, parent, variable: tk.StringVar, values: list,
                 width: int = 14, font=None, **kw):
        super().__init__(parent, bg=PANEL, **kw)
        self._var    = variable
        self._values = values
        self._font   = font or (FONT_BODY[0], 10)
        self._open   = False

        # Current-value display button
        self._btn = tk.Button(
            self,
            textvariable=variable,
            bg="#1a1a28", fg=TEXT,
            activebackground="#22223a", activeforeground=TEXT,
            relief="flat",
            font=self._font,
            anchor="w",
            padx=10, pady=5,
            width=width,
            cursor="hand2",
            highlightbackground=BORDER2,
            highlightthickness=1,
            command=self._toggle,
        )
        self._btn.pack(side="left")

        # Arrow indicator
        self._arrow = tk.Label(
            self, text="▾", bg="#1a1a28", fg=SUBTEXT,
            font=(FONT_LABEL[0], 9), padx=6, pady=5, cursor="hand2",
        )
        self._arrow.pack(side="left")
        self._arrow.bind("<Button-1>", lambda _: self._toggle())

        self._popup: tk.Toplevel | None = None

    def _toggle(self):
        if self._open:
            self._close()
        else:
            self._show()

    def _show(self):
        self._open = True
        self._arrow.config(text="▴")

        p = tk.Toplevel(self)
        p.overrideredirect(True)
        p.configure(bg=self.POPUP_BG)
        p.attributes("-topmost", True)

        # Position below the button
        self.update_idletasks()
        x = self._btn.winfo_rootx()
        y = self._btn.winfo_rooty() + self._btn.winfo_height() + 2
        p.geometry(f"+{x}+{y}")

        # Outer border frame
        border = tk.Frame(p, bg=BORDER_HI, padx=1, pady=1)
        border.pack(fill="both", expand=True)

        inner = tk.Frame(border, bg=self.POPUP_BG)
        inner.pack(fill="both", expand=True)

        btn_width = self._btn.winfo_width() + self._arrow.winfo_width()

        for val in self._values:
            row = tk.Frame(inner, bg=self.POPUP_BG, cursor="hand2")
            row.pack(fill="x")
            lbl = tk.Label(
                row, text=val,
                bg=self.POPUP_BG, fg=self.POPUP_FG,
                font=self._font,
                anchor="w", padx=12, pady=6,
                width=btn_width // 8,   # rough char width
            )
            lbl.pack(fill="x")

            def _on_enter(e, r=row, l=lbl):
                r.config(bg=self.POPUP_SEL)
                l.config(bg=self.POPUP_SEL)

            def _on_leave(e, r=row, l=lbl):
                r.config(bg=self.POPUP_BG)
                l.config(bg=self.POPUP_BG)

            def _on_click(v=val):
                self._var.set(v)
                self._close()

            row.bind("<Enter>",   _on_enter)
            row.bind("<Leave>",   _on_leave)
            row.bind("<Button-1>", lambda e, v=val: _on_click(v))
            lbl.bind("<Enter>",   _on_enter)
            lbl.bind("<Leave>",   _on_leave)
            lbl.bind("<Button-1>", lambda e, v=val: _on_click(v))

        self._popup = p
        # Close when clicking anywhere else
        p.bind("<FocusOut>", lambda _: self.after(100, self._close))
        p.focus_set()

    def _close(self):
        self._open = False
        self._arrow.config(text="▾")
        if self._popup:
            try:
                self._popup.destroy()
            except Exception:
                pass
            self._popup = None

    def set(self, value):
        self._var.set(value)

    def get(self):
        return self._var.get()


# ── Combobox / progress-bar ttk style ─────────────────────────────────────────

def apply_combobox_style():
    s = ttk.Style()
    try:
        s.theme_use("default")
    except Exception:
        pass

    # Keep ttk.Combobox dark for any remaining uses (auth section browsers list)
    s.configure(
        "TCombobox",
        fieldbackground="#0d0d14",
        background="#0d0d14",
        foreground=TEXT,
        selectbackground="#1e1e35",
        selectforeground=TEXT,
        bordercolor=BORDER2,
        lightcolor=BORDER2,
        darkcolor=BORDER2,
        arrowcolor=SUBTEXT,
        padding=(8, 5),
    )
    s.map(
        "TCombobox",
        fieldbackground=[("readonly", "#0d0d14")],
        foreground=[("readonly", TEXT)],
        selectbackground=[("readonly", "#1e1e35")],
    )

    # Red progress bar
    s.configure(
        "Red.Horizontal.TProgressbar",
        troughcolor="#1a1a28",
        background=ACCENT,
        bordercolor=BORDER,
        lightcolor=ACCENT_LT,
        darkcolor=ACCENT_DK,
        thickness=8,
    )
    # Purple progress bar (MP4)
    s.configure(
        "Purple.Horizontal.TProgressbar",
        troughcolor="#1a1a28",
        background=PURPLE,
        bordercolor=BORDER,
        lightcolor=PURPLE,
        darkcolor=PURPLE_DK,
        thickness=8,
    )
    s.configure(
        "TScrollbar",
        troughcolor=CARD,
        background="#222235",
        bordercolor=PANEL,
        arrowcolor=SUBTEXT,
    )


# ── Spinbox ───────────────────────────────────────────────────────────────────

def styled_spinbox(parent, variable, lo, hi, width=5):
    return tk.Spinbox(
        parent,
        textvariable=variable,
        from_=lo, to=hi,
        width=width,
        font=FONT_BODY,
        bg="#1a1a28", fg=TEXT,
        insertbackground=TEXT,
        buttonbackground="#222235",
        relief="flat",
        highlightbackground=BORDER2,
        highlightthickness=1,
    )


# ── Log text widget ───────────────────────────────────────────────────────────

def make_log(parent) -> tk.Text:
    from theme import SUCCESS, WARNING, ERROR, SUBTEXT, BLUE, ACCENT
    sb = ttk.Scrollbar(parent, style="TScrollbar")
    sb.pack(side="right", fill="y")
    log = tk.Text(
        parent,
        bg="#0d0d14", fg=TEXT,
        font=FONT_MONO,
        relief="flat", bd=0,
        yscrollcommand=sb.set,
        state="disabled",
        wrap="word",
        insertbackground=TEXT,
        padx=12, pady=10,
        spacing1=3, spacing3=3,
    )
    log.pack(fill="both", expand=True, padx=1, pady=1)
    sb.config(command=log.yview)

    log.tag_config("ok",   foreground=SUCCESS)
    log.tag_config("warn", foreground=WARNING)
    log.tag_config("err",  foreground=ERROR)
    log.tag_config("dim",  foreground=SUBTEXT)
    log.tag_config("info", foreground=BLUE)
    return log
