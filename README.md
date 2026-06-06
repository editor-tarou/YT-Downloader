# YT → MP3  `v2.0`

A polished desktop app for downloading YouTube videos and playlists as MP3 files.  
Built on **yt-dlp** + **tkinter**. No browser extension. No account needed.

---

## Quick Start

```bash
# 1. Install dependencies + create a launcher
python install.py

# 2. Run
python main.py
```

---

## Requirements

| Dependency | Why |
|---|---|
| Python 3.10+ | Runtime |
| tkinter | GUI (bundled with most Python installs) |
| yt-dlp | YouTube download engine — `pip install yt-dlp` |
| ffmpeg | MP3 conversion — install via your package manager |

`install.py` handles yt-dlp automatically. ffmpeg must be installed manually.

---

## Project Structure

```
ytmp3/
├── main.py          ← entry point (run this)
├── app.py           ← main window + wiring
├── theme.py         ← colours, fonts, palette
├── install.py       ← installer / launcher creator
│
├── ui/
│   ├── header.py    ← top header bar
│   ├── sections.py  ← URL, folder, auth, rate-limit, progress cards
│   └── widgets.py   ← reusable themed widget factories
│
├── core/
│   ├── downloader.py ← yt-dlp download session (no UI dependency)
│   └── fetcher.py   ← yt-dlp metadata fetching (no UI dependency)
│
└── assets/
    └── icon.py      ← programmatic app icon (no external files)
```

---

## Features

- Download single videos **or** entire playlists
- Configurable MP3 quality (64 – 320 kbps)
- Pause / Resume mid-download
- Rate limiting (sleep between tracks) to avoid bans
- Cookie-based auth for age-restricted / private videos
- Archive file to skip already-downloaded tracks (resumable playlists)
- Real-time progress bar + log

---

## Authentication

For private or age-restricted videos, either:
- **Browser cookies** – pick your browser from the dropdown (Chrome, Firefox, etc.)
- **cookies.txt** – export from your browser using an extension like *Get cookies.txt*

---

## ffmpeg

Without ffmpeg the download will produce an audio-only container (webm/m4a) instead of MP3.

| OS | Install command |
|---|---|
| Windows | `winget install ffmpeg` |
| macOS | `brew install ffmpeg` |
| Ubuntu/Debian | `sudo apt install ffmpeg` |
