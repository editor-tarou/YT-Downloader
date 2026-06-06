"""
app.py – Main application window.
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

from theme import (
    BG, PANEL, CARD, BORDER, BORDER2, BORDER_HI,
    ACCENT, ACCENT_DK, ACCENT_LT,
    PURPLE, PURPLE_DK,
    BLUE, BLUE_DK,
    TEXT, SUBTEXT, DIMTEXT,
    FONT_BTN, FONT_BTN2, FONT_LABEL, FONT_SMALL,
    ARCHIVE_FILE,
)
from ui.header import HeaderBar
from ui.sections import (
    UrlSection, FormatSection,
    AuthSection, RateLimitSection, ProgressSection,
)
from ui.widgets import make_card, make_log, apply_combobox_style
from core.fetcher import fetch_info
from core.downloader import DownloadSession


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YT → MP3 / MP4")
        self.geometry("960x980")
        self.minsize(780, 740)
        self.configure(bg=BG)

        self._set_icon()
        apply_combobox_style()

        # ── tk variables ──────────────────────────────────────────────────────
        self.output_dir      = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.url_var         = tk.StringVar()
        self.format_var      = tk.StringVar(value="mp3")
        self.quality_var     = tk.StringVar(value="192")
        self.status_var      = tk.StringVar(value="Ready.")
        self.browser_var     = tk.StringVar(value="none")
        self.cookie_file     = tk.StringVar(value="")
        self.sleep_min       = tk.IntVar(value=3)
        self.sleep_max       = tk.IntVar(value=8)
        self.sleep_req       = tk.IntVar(value=1)
        self.use_archive     = tk.BooleanVar(value=True)
        self.codec_var       = tk.StringVar(value="any")
        self.resolution_var  = tk.StringVar(value="best")
        self.embed_subs_var  = tk.BooleanVar(value=False)
        self.embed_thumb_var = tk.BooleanVar(value=False)
        self.write_subs_var  = tk.BooleanVar(value=False)

        self._session: DownloadSession | None = None
        self._build_ui()

    # ── Icon ──────────────────────────────────────────────────────────────────

    def _set_icon(self):
        try:
            from assets.icon import get_icon_png_bytes
            import tempfile
            png = get_icon_png_bytes()
            tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            tmp.write(png); tmp.close()
            img = tk.PhotoImage(file=tmp.name)
            self.iconphoto(True, img)
            self._icon_img = img
            os.unlink(tmp.name)
        except Exception:
            pass

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        HeaderBar(self).pack(fill="x", padx=20)
        tk.Frame(self, bg=BORDER2, height=1).pack(fill="x", padx=20, pady=(0, 4))

        # Scrollable body
        body_wrap = tk.Frame(self, bg=BG)
        body_wrap.pack(fill="both", expand=True)

        canvas = tk.Canvas(body_wrap, bg=BG, highlightthickness=0)
        vbar   = ttk.Scrollbar(body_wrap, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vbar.set)
        vbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        body = tk.Frame(canvas, bg=BG)
        cw = canvas.create_window((0, 0), window=body, anchor="nw")

        body.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(cw, width=e.width))
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))
        canvas.bind_all("<Button-4>",
            lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>",
            lambda e: canvas.yview_scroll(1, "units"))

        P = dict(fill="x", padx=20, pady=(0, 10))

        # ── Sections ──────────────────────────────────────────────────────────
        self.url_sec = UrlSection(body, url_var=self.url_var,
                                  on_fetch=self._fetch_info)
        self.url_sec.pack(**P)

        self.fmt_sec = FormatSection(
            body,
            output_dir_var=self.output_dir,
            format_var=self.format_var,
            quality_var=self.quality_var,
            codec_var=self.codec_var,
            resolution_var=self.resolution_var,
            embed_subs_var=self.embed_subs_var,
            embed_thumb_var=self.embed_thumb_var,
            write_subs_var=self.write_subs_var,
        )
        self.fmt_sec.pack(**P)

        self.auth_sec = AuthSection(body, browser_var=self.browser_var,
                                    cookie_file_var=self.cookie_file)
        self.auth_sec.pack(**P)

        self.rate_sec = RateLimitSection(
            body,
            sleep_min_var=self.sleep_min,
            sleep_max_var=self.sleep_max,
            sleep_req_var=self.sleep_req,
            use_archive_var=self.use_archive,
        )
        self.rate_sec.pack(**P)

        self.prog_sec = ProgressSection(body, format_var=self.format_var)
        self.prog_sec.pack(**P)

        # ── Action buttons ────────────────────────────────────────────────────
        btn_row = tk.Frame(body, bg=BG)
        btn_row.pack(fill="x", padx=20, pady=(4, 14))

        self.dl_btn = tk.Button(
            btn_row, text="⬇   Download",
            font=FONT_BTN,
            bg=ACCENT, fg="white",
            activebackground=ACCENT_DK, activeforeground="white",
            relief="flat", padx=28, pady=12,
            cursor="hand2", command=self._start,
        )
        self.dl_btn.pack(side="left")
        self.dl_btn.bind("<Enter>", lambda _: self._btn_hover(self.dl_btn, ACCENT_DK))
        self.dl_btn.bind("<Leave>", lambda _: self._btn_hover(self.dl_btn, ACCENT))

        # update dl button colour when format changes
        self.format_var.trace_add("write", self._on_format_change)

        self.pause_btn = tk.Button(
            btn_row, text="⏸   Pause",
            font=FONT_BTN2, bg=BORDER2, fg=SUBTEXT,
            activebackground=BORDER_HI, activeforeground="white",
            relief="flat", padx=18, pady=12,
            cursor="hand2", state="disabled",
            command=self._toggle_pause,
        )
        self.pause_btn.pack(side="left", padx=10)

        self.stop_btn = tk.Button(
            btn_row, text="⏹   Stop",
            font=FONT_BTN2, bg=BORDER2, fg=SUBTEXT,
            activebackground=BORDER_HI, activeforeground="white",
            relief="flat", padx=18, pady=12,
            cursor="hand2", state="disabled",
            command=self._stop,
        )
        self.stop_btn.pack(side="left")

        tk.Label(btn_row, textvariable=self.status_var,
                 font=FONT_SMALL, fg=SUBTEXT, bg=BG).pack(side="right", padx=4)

        # ── Log ───────────────────────────────────────────────────────────────
        log_o, log_i = make_card(body, "Log")
        log_o.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.log_box = make_log(log_i)

    # ── Format-aware button colour ────────────────────────────────────────────

    def _on_format_change(self, *_):
        fmt  = self.format_var.get()
        col  = PURPLE if fmt == "mp4" else ACCENT
        cold = PURPLE_DK if fmt == "mp4" else ACCENT_DK
        self.dl_btn.config(bg=col, activebackground=cold)
        self.dl_btn.bind("<Enter>", lambda _: self._btn_hover(self.dl_btn, cold))
        self.dl_btn.bind("<Leave>", lambda _: self._btn_hover(self.dl_btn, col))

    def _btn_hover(self, btn, color):
        btn.config(bg=color)

    # ── Fetch info ────────────────────────────────────────────────────────────

    def _fetch_info(self):
        url = self.url_sec.get_url()
        if not url:
            messagebox.showwarning("No URL", "Please paste a URL first.")
            return
        self._log("Fetching info…", "dim")
        fetch_info(
            url, self._auth_opts(),
            on_playlist=lambda t, n: self.after(0, self._log,
                f'Playlist: "{t}"  —  {n} videos', "ok"),
            on_video=lambda t, d: self.after(0, self._log,
                f'Video: "{t}"' + (f"  [{d}]" if d else ""), "ok"),
            on_error=lambda m: self.after(0, self._log,
                f"Error: {m}", "err"),
        )

    # ── Download ──────────────────────────────────────────────────────────────

    def _start(self):
        url = self.url_sec.get_url()
        if not url:
            messagebox.showwarning("No URL", "Please paste a URL first.")
            return
        out = self.output_dir.get().strip()
        if not out:
            messagebox.showwarning("No Folder", "Please choose a download folder.")
            return

        self.prog_sec.reset()
        self._set_downloading(True)

        self._session = DownloadSession(
            url=url,
            output_dir=out,
            format=self.format_var.get(),
            quality=self.quality_var.get(),
            auth_opts=self._auth_opts(),
            sleep_min=self.sleep_min.get(),
            sleep_max=self.sleep_max.get(),
            sleep_req=self.sleep_req.get(),
            use_archive=self.use_archive.get(),
            archive_path=os.path.join(out, ARCHIVE_FILE),
            codec=self.codec_var.get(),
            resolution=self.resolution_var.get(),
            embed_subs=self.embed_subs_var.get(),
            embed_thumb=self.embed_thumb_var.get(),
            write_subs=self.write_subs_var.get(),
            on_log=lambda m, t: self.after(0, self._log, m, t),
            on_progress=lambda title, pct, speed, eta: self.after(
                0, self.prog_sec.update,
                title, pct, speed, eta,
                self._session.done  if self._session else 0,
                self._session.total if self._session else 0,
                None,
            ),
            on_track_done=lambda done, total, _: self.after(
                0, self._on_track_done, done, total),
            on_finished=lambda c, f: self.after(0, self._on_finished, c, f),
            on_status=lambda m: self.after(0, self._status, m),
        )
        self._session.start()

    def _toggle_pause(self):
        if not self._session:
            return
        if self._session.is_paused:
            self._session.resume()
            self.pause_btn.config(text="⏸   Pause", bg=BORDER2, fg=SUBTEXT)
            self._log("Resumed.", "info")
            self._status("Downloading…")
        else:
            self._session.pause()
            self.pause_btn.config(text="▶   Resume", bg=BLUE, fg="white")
            self._log("Paused — will hold after current chunk.", "warn")
            self._status("Paused.")

    def _stop(self):
        if self._session:
            self._session.stop()
        self._log("Stop requested…", "warn")
        self._status("Stopping…")

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_track_done(self, done, total):
        pct = int(done / total * 100) if total > 0 else 0
        self.prog_sec.update(done=done, total=total, value=pct)

    def _on_finished(self, completed, failed):
        self._set_downloading(False)
        self.prog_sec.finish()
        summary = (f"Finished!  {len(completed)} downloaded"
                   + (f",  {len(failed)} failed." if failed else "."))
        self._status(summary)
        self._log("─" * 52, "dim")
        self._log(summary, "ok" if not failed else "warn")
        for item in failed:
            self._log(f"   {item}", "err")
        if self.use_archive.get():
            self._log(
                f"Archive: {os.path.join(self.output_dir.get(), ARCHIVE_FILE)}",
                "dim",
            )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _set_downloading(self, active):
        fmt  = self.format_var.get()
        col  = PURPLE if fmt == "mp4" else ACCENT
        cold = PURPLE_DK if fmt == "mp4" else ACCENT_DK
        if active:
            self.dl_btn.config(state="disabled")
            self.pause_btn.config(state="normal", text="⏸   Pause",
                                  bg=BORDER2, fg=SUBTEXT)
            self.stop_btn.config(state="normal")
        else:
            self.dl_btn.config(state="normal", bg=col)
            self.pause_btn.config(state="disabled", text="⏸   Pause",
                                  bg=BORDER2, fg=SUBTEXT)
            self.stop_btn.config(state="disabled")

    def _auth_opts(self):
        opts = {}
        cp = self.cookie_file.get().strip()
        br = self.browser_var.get()
        if cp and os.path.isfile(cp):
            opts["cookiefile"] = cp
        elif br and br != "none":
            opts["cookiesfrombrowser"] = (br,)
        return opts

    def _log(self, msg, tag=""):
        self.log_box.config(state="normal")
        self.log_box.insert("end", msg + "\n", tag)
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def _status(self, msg):
        self.status_var.set(msg)
