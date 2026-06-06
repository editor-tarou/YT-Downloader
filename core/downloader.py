"""
core/downloader.py – yt-dlp download orchestration (MP3 + MP4).
"""
import os
import shutil
import threading
import time
from pathlib import Path
from typing import Callable, List, Optional


class DownloadSession:
    def __init__(
        self,
        url: str,
        output_dir: str,
        format: str,           # "mp3" | "mp4"
        quality: str,          # kbps for mp3; ignored for mp4
        auth_opts: dict,
        sleep_min: int,
        sleep_max: int,
        sleep_req: int,
        use_archive: bool,
        archive_path: str,
        # MP4 extras
        codec: str = "any",
        resolution: str = "best",
        embed_subs: bool = False,
        embed_thumb: bool = False,
        write_subs: bool = False,
        # callbacks
        on_log: Callable[[str, str], None] = lambda m, t: None,
        on_progress: Callable[[str, str, str, str], None] = lambda *a: None,
        on_track_done: Callable[[int, int, str], None] = lambda *a: None,
        on_finished: Callable[[List[str], List[str]], None] = lambda *a: None,
        on_status: Callable[[str], None] = lambda m: None,
    ):
        self.url          = url
        self.output_dir   = output_dir
        self.format       = format
        self.quality      = quality
        self.auth_opts    = auth_opts
        self.sleep_min    = sleep_min
        self.sleep_max    = sleep_max
        self.sleep_req    = sleep_req
        self.use_archive  = use_archive
        self.archive_path = archive_path
        self.codec        = codec
        self.resolution   = resolution
        self.embed_subs   = embed_subs
        self.embed_thumb  = embed_thumb
        self.write_subs   = write_subs

        self.on_log        = on_log
        self.on_progress   = on_progress
        self.on_track_done = on_track_done
        self.on_finished   = on_finished
        self.on_status     = on_status

        self._stop_flag   = threading.Event()
        self._pause_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

        self.done  = 0
        self.total = 0

    # ── public controls ───────────────────────────────────────────────────────

    def start(self):
        os.makedirs(self.output_dir, exist_ok=True)
        self._stop_flag.clear()
        self._pause_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def pause(self):  self._pause_event.set()
    def resume(self): self._pause_event.clear()
    def stop(self):
        self._pause_event.clear()
        self._stop_flag.set()

    @property
    def is_paused(self): return self._pause_event.is_set()

    # ── internal ──────────────────────────────────────────────────────────────

    def _run(self):
        import yt_dlp

        mode = "MP4 video" if self.format == "mp4" else f"MP3 {self.quality} kbps"
        self.on_log(
            f"Starting → {self.output_dir}  [{mode}]  "
            f"sleep {self.sleep_min}-{self.sleep_max}s",
            "dim",
        )
        if self.use_archive:
            self.on_log(f"Archive: {self.archive_path}", "dim")

        completed: List[str] = []
        failed:    List[str] = []
        idx       = [0]
        total_ref = [self.total or "?"]
        is_pl     = [False]

        def hook(d):
            while self._pause_event.is_set():
                if self._stop_flag.is_set():
                    break
                time.sleep(0.3)
            if self._stop_flag.is_set():
                raise Exception("__STOPPED__")

            if d["status"] == "downloading":
                title = d.get("info_dict", {}).get("title", "…")
                pct   = d.get("_percent_str", "").strip()
                speed = d.get("_speed_str",   "").strip()
                eta   = d.get("_eta_str",     "").strip()
                self.on_progress(title, pct, speed, eta)

            elif d["status"] == "finished":
                title    = d.get("info_dict", {}).get("title", "track")
                idx[0]  += 1
                self.done = idx[0]
                n = total_ref[0]
                self.on_track_done(idx[0], n if isinstance(n, int) else 0, title)
                self.on_log(f"[{idx[0]}/{n}]  {title}", "ok")
                self.on_status(f"{idx[0]} track(s) done…")
                completed.append(title)

        # pre-flight
        try:
            pre = {"quiet": True, "no_warnings": True,
                   "extract_flat": True, "skip_download": True}
            pre.update(self.auth_opts)
            with yt_dlp.YoutubeDL(pre) as ydl:
                info = ydl.extract_info(self.url, download=False)

            if info and info.get("_type") == "playlist":
                is_pl[0]     = True
                entries      = [e for e in info.get("entries", []) if e]
                total_ref[0] = len(entries)
                self.total   = total_ref[0]
            else:
                is_pl[0]     = False
                total_ref[0] = 1
                self.total   = 1

            kind = "Playlist" if is_pl[0] else "Single video"
            self.on_log(f"{kind} — {total_ref[0]} item(s) to download", "dim")

        except Exception as exc:
            self.on_log(f"Pre-flight error: {exc}", "err")

        opts = self._build_opts(is_pl[0], [hook])
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([self.url])
        except Exception as exc:
            msg = str(exc)
            if "__STOPPED__" in msg:
                self.on_log(f"Stopped after {self.done} item(s).", "warn")
            else:
                self.on_log(f"Error: {msg}", "err")
                failed.append(msg)

        self.on_finished(completed, failed)

    def _build_opts(self, is_playlist: bool, hooks: list) -> dict:
        tmpl = (
            os.path.join(self.output_dir, "%(playlist_index)02d - %(title)s.%(ext)s")
            if is_playlist
            else os.path.join(self.output_dir, "%(title)s.%(ext)s")
        )

        if self.format == "mp4":
            opts = self._mp4_opts(tmpl, hooks)
        else:
            opts = self._mp3_opts(tmpl, hooks)

        opts.update(self.auth_opts)

        ffmpeg = shutil.which("ffmpeg")
        if ffmpeg:
            opts["ffmpeg_location"] = str(Path(ffmpeg).parent)

        if self.use_archive:
            opts["download_archive"] = self.archive_path

        return opts

    # ── format-specific opts ──────────────────────────────────────────────────

    def _mp3_opts(self, tmpl, hooks) -> dict:
        return {
            "format": "bestaudio/best",
            "outtmpl": tmpl,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": self.quality,
            }],
            "quiet": True, "no_warnings": True,
            "ignoreerrors": True, "continuedl": True,
            "progress_hooks": hooks,
            "sleep_interval":          self.sleep_min,
            "max_sleep_interval":      self.sleep_max,
            "sleep_interval_requests": self.sleep_req,
        }

    def _mp4_opts(self, tmpl, hooks) -> dict:
        # Resolution → height filter
        res_map = {
            "best":        None,
            "4320p  (8K)": "4320",
            "2160p  (4K)": "2160",
            "1440p  (2K)": "1440",
            "1080p  (FHD)":"1080",
            "720p   (HD)": "720",
            "480p":        "480",
            "360p":        "360",
            "240p":        "240",
            "144p":        "144",
        }
        height = res_map.get(self.resolution)

        # Codec preference → yt-dlp vcodec filter
        codec_map = {
            "any":          "",
            "H.264 (avc1)": "[vcodec^=avc1]",
            "VP9":          "[vcodec=vp9]",
            "AV1 (av01)":   "[vcodec^=av01]",
        }
        vcodec_filter = codec_map.get(self.codec, "")

        if height:
            fmt_str = (
                f"bestvideo[height<={height}]{vcodec_filter}+bestaudio"
                f"/bestvideo[height<={height}]+bestaudio/best"
            )
        else:
            fmt_str = (
                f"bestvideo{vcodec_filter}+bestaudio/best"
            )

        postprocessors = [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}]
        if self.embed_subs:
            postprocessors.append({"key": "FFmpegEmbedSubtitle"})
        if self.embed_thumb:
            postprocessors.append({"key": "EmbedThumbnail"})

        return {
            "format":    fmt_str,
            "outtmpl":   tmpl,
            "merge_output_format": "mp4",
            "postprocessors": postprocessors,
            "writethumbnail": self.embed_thumb,
            "writesubtitles": self.write_subs or self.embed_subs,
            "subtitleslangs": ["en"],
            "quiet": True, "no_warnings": True,
            "ignoreerrors": True, "continuedl": True,
            "progress_hooks": hooks,
            "sleep_interval":          self.sleep_min,
            "max_sleep_interval":      self.sleep_max,
            "sleep_interval_requests": self.sleep_req,
        }
