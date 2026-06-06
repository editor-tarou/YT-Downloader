"""
core/fetcher.py – Fetch video / playlist metadata via yt-dlp.
All logic is UI-agnostic; results are delivered via callbacks.
"""

import threading
from typing import Callable, Optional


def fetch_info(
    url: str,
    auth_opts: dict,
    on_playlist: Callable[[str, int], None],
    on_video: Callable[[str, str], None],
    on_error: Callable[[str], None],
) -> None:
    """
    Spawn a background thread that fetches yt-dlp metadata for *url*.

    Callbacks (called on the background thread – caller must dispatch to UI thread):
        on_playlist(title, count)
        on_video(title, duration_str)
        on_error(message)
    """
    import yt_dlp

    def _run():
        opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
            "skip_download": True,
        }
        opts.update(auth_opts)
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
            if info.get("_type") == "playlist":
                entries = [e for e in info.get("entries", []) if e]
                on_playlist(info.get("title", "Unknown Playlist"), len(entries))
            else:
                on_video(
                    info.get("title", "video"),
                    info.get("duration_string", ""),
                )
        except Exception as exc:
            on_error(str(exc))

    threading.Thread(target=_run, daemon=True).start()
