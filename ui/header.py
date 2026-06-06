"""
ui/header.py – Application header bar.
"""
import tkinter as tk
from theme import BG, ACCENT, ACCENT_LT, TEXT, SUBTEXT, DIMTEXT, FONT_TITLE, FONT_LABEL


class HeaderBar(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG, pady=18, **kw)
        self._build()

    def _build(self):
        left = tk.Frame(self, bg=BG)
        left.pack(side="left")

        # Play icon
        c = tk.Canvas(left, width=46, height=46, bg=BG, highlightthickness=0)
        c.pack(side="left", padx=(0, 14))
        # Outer glow ring (faked with stacked ovals)
        c.create_oval(1, 1, 45, 45, fill="#2a0a0a", outline="")
        c.create_oval(3, 3, 43, 43, fill=ACCENT, outline="")
        # Triangle
        c.create_polygon(17, 12, 17, 34, 37, 23, fill="white", outline="")

        title_col = tk.Frame(left, bg=BG)
        title_col.pack(side="left")
        tk.Label(
            title_col,
            text="YouTube  →  MP3 / MP4",
            font=FONT_TITLE,
            fg=TEXT, bg=BG, anchor="w",
        ).pack(anchor="w")
        tk.Label(
            title_col,
            text="Powered by yt-dlp  ·  single videos & playlists",
            font=FONT_LABEL,
            fg=SUBTEXT, bg=BG, anchor="w",
        ).pack(anchor="w")

        # Right: version badge
        badge = tk.Frame(self, bg="#14141e",
                         highlightbackground="#2e2e42", highlightthickness=1,
                         padx=12, pady=5)
        badge.pack(side="right", padx=4)
        tk.Label(
            badge, text="v3.0",
            font=(FONT_LABEL[0], 9, "bold"),
            fg=ACCENT, bg="#14141e",
        ).pack()
