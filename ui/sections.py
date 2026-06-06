"""
ui/sections.py – Individual section widgets for the main form.
"""
import tkinter as tk
from tkinter import ttk, filedialog

from theme import (
    BG, PANEL, CARD, CARD2, BORDER, BORDER2, BORDER_HI,
    ACCENT, ACCENT_DK, ACCENT_LT, PURPLE, PURPLE_DK, PURPLE_LT,
    TEXT, SUBTEXT, DIMTEXT,
    BROWSERS, FONT_LABEL, FONT_BODY, FONT_SMALL, FONT_BTN,
)
from ui.widgets import (
    make_card, styled_entry, styled_button,
    styled_spinbox, apply_combobox_style, DarkCombo,
)

PLACEHOLDER = "https://www.youtube.com/watch?v=…  or  playlist URL"


# ── URL section ───────────────────────────────────────────────────────────────

class UrlSection(tk.Frame):
    def __init__(self, parent, url_var, on_fetch, **kw):
        super().__init__(parent, bg=BG, **kw)
        self.url_var  = url_var
        self.on_fetch = on_fetch
        outer, inner = make_card(self, "YouTube URL")
        outer.pack(fill="x")
        self._build(inner)

    def _build(self, inner):
        row = tk.Frame(inner, bg=PANEL)
        row.pack(fill="x")

        self._entry = styled_entry(
            row, textvariable=self.url_var,
            font=(FONT_BODY[0], 11),
        )
        self._entry.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 10))
        self._entry.insert(0, PLACEHOLDER)
        self._entry.config(fg=SUBTEXT)
        self._entry.bind("<FocusIn>",  self._clear_ph)
        self._entry.bind("<FocusOut>", self._restore_ph)

        styled_button(
            row, text="  Fetch Info  ",
            command=self.on_fetch,
        ).pack(side="left", ipady=7, ipadx=6)

    def _clear_ph(self, _=None):
        if self._entry.get() == PLACEHOLDER:
            self._entry.delete(0, "end")
            self._entry.config(fg=TEXT)

    def _restore_ph(self, _=None):
        if not self._entry.get().strip():
            self._entry.insert(0, PLACEHOLDER)
            self._entry.config(fg=SUBTEXT)

    def get_url(self):
        v = self.url_var.get().strip()
        return "" if v == PLACEHOLDER else v


# ── Format section ────────────────────────────────────────────────────────────

class FormatSection(tk.Frame):
    def __init__(self, parent, output_dir_var, format_var, quality_var,
                 codec_var, resolution_var,
                 embed_subs_var, embed_thumb_var, write_subs_var,
                 **kw):
        super().__init__(parent, bg=BG, **kw)
        self.output_dir_var  = output_dir_var
        self.format_var      = format_var
        self.quality_var     = quality_var
        self.codec_var       = codec_var
        self.resolution_var  = resolution_var
        self.embed_subs_var  = embed_subs_var
        self.embed_thumb_var = embed_thumb_var
        self.write_subs_var  = write_subs_var

        outer, inner = make_card(self, "Download Settings")
        outer.pack(fill="x")
        self._inner = inner
        self._build(inner)

    def _build(self, inner):
        apply_combobox_style()

        # ── Folder row ────────────────────────────────────────────────────────
        folder_row = tk.Frame(inner, bg=PANEL)
        folder_row.pack(fill="x", pady=(0, 14))

        tk.Label(folder_row, text="Save to:", fg=SUBTEXT, bg=PANEL,
                 font=FONT_LABEL).pack(side="left", padx=(0, 8))
        styled_entry(folder_row, textvariable=self.output_dir_var).pack(
            side="left", fill="x", expand=True, ipady=7, padx=(0, 8)
        )
        styled_button(folder_row, text="Browse…",
                      command=self._browse).pack(side="left", ipady=5, ipadx=6)

        tk.Frame(inner, bg=BORDER2, height=1).pack(fill="x", pady=(0, 14))

        # ── Format pill toggle ────────────────────────────────────────────────
        toggle_row = tk.Frame(inner, bg=PANEL)
        toggle_row.pack(fill="x", pady=(0, 16))

        tk.Label(toggle_row, text="Format", fg=SUBTEXT, bg=PANEL,
                 font=(FONT_LABEL[0], 8)).pack(side="left", padx=(0, 14))

        # Pill container
        pill_wrap = tk.Frame(toggle_row,
                             bg=BORDER2, highlightbackground=BORDER_HI,
                             highlightthickness=1)
        pill_wrap.pack(side="left")

        self._mp3_btn = tk.Button(
            pill_wrap, text="  🎵  MP3  ",
            font=(FONT_LABEL[0], 9, "bold"),
            relief="flat", cursor="hand2", bd=0,
            padx=14, pady=7,
            command=lambda: self._set_fmt("mp3"),
        )
        self._mp3_btn.pack(side="left")

        # Divider between pills
        tk.Frame(pill_wrap, bg=BORDER_HI, width=1).pack(side="left", fill="y")

        self._mp4_btn = tk.Button(
            pill_wrap, text="  🎬  MP4  ",
            font=(FONT_LABEL[0], 9, "bold"),
            relief="flat", cursor="hand2", bd=0,
            padx=14, pady=7,
            command=lambda: self._set_fmt("mp4"),
        )
        self._mp4_btn.pack(side="left")

        self._update_pill()
        self.format_var.trace_add("write", lambda *_: self._update_pill())

        # ── Options area ──────────────────────────────────────────────────────
        self._options_frame = tk.Frame(inner, bg=PANEL)
        self._options_frame.pack(fill="x")
        self._build_options()

    def _set_fmt(self, fmt):
        self.format_var.set(fmt)
        self._build_options()

    def _update_pill(self):
        fmt = self.format_var.get()
        if fmt == "mp3":
            self._mp3_btn.config(bg=ACCENT,   fg="white",
                                  activebackground=ACCENT_DK, activeforeground="white")
            self._mp4_btn.config(bg=BORDER2,  fg=SUBTEXT,
                                  activebackground="#2e2e48",  activeforeground=TEXT)
        else:
            self._mp3_btn.config(bg=BORDER2,  fg=SUBTEXT,
                                  activebackground="#2e2e48",  activeforeground=TEXT)
            self._mp4_btn.config(bg=PURPLE,   fg="white",
                                  activebackground=PURPLE_DK, activeforeground="white")

    def _build_options(self):
        for w in self._options_frame.winfo_children():
            w.destroy()
        if self.format_var.get() == "mp3":
            self._build_mp3_opts()
        else:
            self._build_mp4_opts()

    # ── MP3 options ───────────────────────────────────────────────────────────

    def _build_mp3_opts(self):
        f = self._options_frame
        row = tk.Frame(f, bg=PANEL)
        row.pack(fill="x")

        tk.Label(row, text="Bitrate", fg=SUBTEXT, bg=PANEL,
                 font=(FONT_LABEL[0], 8)).pack(side="left", padx=(0, 10))

        DarkCombo(
            row, variable=self.quality_var,
            values=["64", "96", "128", "160", "192", "256", "320"],
            width=6,
        ).pack(side="left")

        tk.Label(row, text="kbps", fg=DIMTEXT, bg=PANEL,
                 font=FONT_SMALL).pack(side="left", padx=(8, 0))

    # ── MP4 options ───────────────────────────────────────────────────────────

    def _build_mp4_opts(self):
        f = self._options_frame

        # Row 1: resolution + codec side by side
        row1 = tk.Frame(f, bg=PANEL)
        row1.pack(fill="x", pady=(0, 12))

        # Resolution
        res_card = _mini_card(row1, "Resolution")
        res_card.pack(side="left", padx=(0, 16))
        DarkCombo(
            res_card, variable=self.resolution_var,
            values=[
                "best",
                "4320p  (8K)",
                "2160p  (4K)",
                "1440p  (2K)",
                "1080p  (FHD)",
                "720p   (HD)",
                "480p",
                "360p",
                "240p",
                "144p",
            ],
            width=14,
        ).pack()

        # Codec
        codec_card = _mini_card(row1, "Codec preference")
        codec_card.pack(side="left")
        DarkCombo(
            codec_card, variable=self.codec_var,
            values=["any", "H.264 (avc1)", "VP9", "AV1 (av01)"],
            width=14,
        ).pack()

        # Row 2: checkboxes
        row2 = tk.Frame(f, bg=PANEL)
        row2.pack(fill="x")

        for var, label in [
            (self.embed_subs_var,  "Embed subtitles"),
            (self.embed_thumb_var, "Embed thumbnail"),
            (self.write_subs_var,  "Save .srt file"),
        ]:
            _toggle_chip(row2, var, label).pack(side="left", padx=(0, 8))

    def _browse(self):
        d = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if d:
            self.output_dir_var.set(d)


# ── Small helpers for MP4 option layout ───────────────────────────────────────

def _mini_card(parent, label):
    """A tiny labelled container for grouping a control."""
    wrap = tk.Frame(parent, bg=PANEL)
    tk.Label(wrap, text=label, fg=DIMTEXT, bg=PANEL,
             font=(FONT_LABEL[0], 7, "bold")).pack(anchor="w", pady=(0, 4))
    return wrap


def _toggle_chip(parent, var: tk.BooleanVar, label: str) -> tk.Frame:
    """A toggle chip button — looks like a pill, acts like a checkbox."""
    wrap = tk.Frame(parent, bg=PANEL)

    def _refresh(*_):
        on = var.get()
        btn.config(
            bg=PURPLE if on else "#1e1e30",
            fg="white"  if on else SUBTEXT,
            highlightbackground=PURPLE_DK if on else BORDER2,
        )

    btn = tk.Button(
        wrap, text=label,
        relief="flat", cursor="hand2",
        font=(FONT_LABEL[0], 8),
        padx=10, pady=5,
        highlightthickness=1,
        command=lambda: (var.set(not var.get()), _refresh()),
    )
    btn.pack()
    var.trace_add("write", _refresh)
    _refresh()
    return wrap


# ── Auth section ──────────────────────────────────────────────────────────────

class AuthSection(tk.Frame):
    def __init__(self, parent, browser_var, cookie_file_var, **kw):
        super().__init__(parent, bg=BG, **kw)
        self.browser_var     = browser_var
        self.cookie_file_var = cookie_file_var
        outer, inner = make_card(self, "Authentication  ·  private / age-restricted videos")
        outer.pack(fill="x")
        self._build(inner)

    def _build(self, inner):
        apply_combobox_style()
        row = tk.Frame(inner, bg=PANEL)
        row.pack(fill="x", pady=(0, 6))
        row.columnconfigure(3, weight=1)

        tk.Label(row, text="Browser cookies:", fg=TEXT, bg=PANEL,
                 font=FONT_LABEL).grid(row=0, column=0, sticky="w", pady=2)

        # Auth uses ttk.Combobox (long list, searchable behaviour expected)
        ttk.Combobox(
            row, textvariable=self.browser_var,
            values=BROWSERS, state="readonly",
            font=(FONT_BODY[0], 10), width=12,
        ).grid(row=0, column=1, sticky="w", padx=(8, 16), pady=2)

        tk.Label(row, text="— or cookies.txt:", fg=SUBTEXT, bg=PANEL,
                 font=FONT_LABEL).grid(row=0, column=2, sticky="w", pady=2)
        styled_entry(row, textvariable=self.cookie_file_var,
                     font=(FONT_BODY[0], 9)).grid(
            row=0, column=3, sticky="ew", ipady=5, padx=(8, 8), pady=2
        )
        styled_button(row, text="Browse…", command=self._browse_cookie).grid(
            row=0, column=4, sticky="w", pady=2, ipady=4, ipadx=4,
        )
        tk.Label(
            inner,
            text="Tip: pick a browser to pull its cookies automatically, "
                 "or export cookies.txt via a browser extension.",
            fg=DIMTEXT, bg=PANEL, font=FONT_SMALL, wraplength=760, justify="left",
        ).pack(anchor="w", pady=(2, 0))

    def _browse_cookie(self):
        f = filedialog.askopenfilename(
            title="Select cookies.txt",
            filetypes=[("Text files", "*.txt"), ("All", "*.*")],
        )
        if f:
            self.cookie_file_var.set(f)
            self.browser_var.set("none")


# ── Rate limit section ────────────────────────────────────────────────────────

class RateLimitSection(tk.Frame):
    def __init__(self, parent, sleep_min_var, sleep_max_var,
                 sleep_req_var, use_archive_var, **kw):
        super().__init__(parent, bg=BG, **kw)
        outer, inner = make_card(self, "Rate Limiting  ·  avoids bans on large playlists")
        outer.pack(fill="x")
        self._build(inner, sleep_min_var, sleep_max_var, sleep_req_var, use_archive_var)

    def _build(self, inner, smn, smx, srq, arc):
        g = tk.Frame(inner, bg=PANEL)
        g.pack(fill="x", pady=(0, 10))

        tk.Label(g, text="Delay between tracks:", fg=TEXT, bg=PANEL,
                 font=FONT_LABEL).grid(row=0, column=0, sticky="w", pady=4)
        styled_spinbox(g, smn, 0, 120).grid(row=0, column=1, padx=(10, 4), pady=4)
        tk.Label(g, text="–", fg=SUBTEXT, bg=PANEL,
                 font=FONT_LABEL).grid(row=0, column=2, pady=4)
        styled_spinbox(g, smx, 0, 300).grid(row=0, column=3, padx=(4, 8), pady=4)
        tk.Label(g, text="seconds  (random range)", fg=SUBTEXT, bg=PANEL,
                 font=FONT_LABEL).grid(row=0, column=4, sticky="w", pady=4)

        tk.Label(g, text="Delay between requests:", fg=TEXT, bg=PANEL,
                 font=FONT_LABEL).grid(row=1, column=0, sticky="w", pady=4)
        styled_spinbox(g, srq, 0, 30).grid(row=1, column=1, padx=(10, 4), pady=4)
        tk.Label(g, text="seconds", fg=SUBTEXT, bg=PANEL,
                 font=FONT_LABEL).grid(row=1, column=2, columnspan=3,
                                       sticky="w", padx=(4, 0), pady=4)

        tk.Checkbutton(
            inner,
            text="  Skip already-downloaded videos  (enables playlist resume)",
            variable=arc,
            bg=PANEL, fg=TEXT, selectcolor="#1a1a28",
            activebackground=PANEL, activeforeground=TEXT,
            font=FONT_LABEL, cursor="hand2",
        ).pack(anchor="w", pady=(4, 2))
        tk.Label(
            inner,
            text="Archive saved as  .yt-dlp-archive.txt  in your output folder. "
                 "Delete it to re-download everything.",
            fg=DIMTEXT, bg=PANEL, font=FONT_SMALL,
            wraplength=760, justify="left",
        ).pack(anchor="w")


# ── Progress section ──────────────────────────────────────────────────────────

class ProgressSection(tk.Frame):
    def __init__(self, parent, format_var=None, **kw):
        super().__init__(parent, bg=BG, **kw)
        self._format_var = format_var
        outer, inner = make_card(self, "Progress")
        outer.pack(fill="x")
        self._build(inner)

    def _bar_style(self):
        fmt = self._format_var.get() if self._format_var else "mp3"
        return "Purple.Horizontal.TProgressbar" if fmt == "mp4" \
               else "Red.Horizontal.TProgressbar"

    def _build(self, inner):
        apply_combobox_style()
        self.track_lbl = tk.Label(
            inner, text="—",
            font=(FONT_LABEL[0], 10), fg=TEXT, bg=PANEL, anchor="w",
        )
        self.track_lbl.pack(fill="x", pady=(0, 10))

        self.prog_bar = ttk.Progressbar(
            inner, style=self._bar_style(),
            orient="horizontal", mode="determinate",
        )
        self.prog_bar.pack(fill="x")

        info_row = tk.Frame(inner, bg=PANEL)
        info_row.pack(fill="x", pady=(5, 0))

        self.speed_lbl = tk.Label(
            info_row, text="",
            font=FONT_SMALL, fg=SUBTEXT, bg=PANEL, anchor="w",
        )
        self.speed_lbl.pack(side="left")

        self.count_lbl = tk.Label(
            info_row, text="0 / 0",
            font=FONT_SMALL, fg=SUBTEXT, bg=PANEL, anchor="e",
        )
        self.count_lbl.pack(side="right")

    def update(self, title="", pct="", speed="", eta="",
               done=0, total=0, value=0):
        self.prog_bar.config(style=self._bar_style())
        if title:
            self.track_lbl.config(text=f"{title[:72]}   {pct}")
        if speed or eta:
            parts = []
            if speed: parts.append(speed)
            if eta:   parts.append(f"ETA {eta}")
            self.speed_lbl.config(text="  ".join(parts))
        if total:
            self.count_lbl.config(text=f"{done} / {total}")
        if value is not None:
            self.prog_bar["value"] = value

    def reset(self):
        self.prog_bar["value"] = 0
        self.prog_bar.config(style=self._bar_style())
        self.count_lbl.config(text="0 / ?")
        self.track_lbl.config(text="—")
        self.speed_lbl.config(text="")

    def finish(self):
        self.prog_bar["value"] = 100
        self.track_lbl.config(text="Done.")
        self.speed_lbl.config(text="")
