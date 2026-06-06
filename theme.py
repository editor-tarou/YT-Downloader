"""
theme.py – Color palette, fonts, and shared style constants.
"""
import sys

# ── Colours ───────────────────────────────────────────────────────────────────
BG        = "#0a0a0f"       # near-black with a slight blue tint
PANEL     = "#111118"
CARD      = "#16161f"
CARD2     = "#1d1d28"
BORDER    = "#252535"
BORDER2   = "#2e2e42"
BORDER_HI = "#3d3d58"

# Red/accent
ACCENT    = "#e53935"
ACCENT_DK = "#b71c1c"
ACCENT_LT = "#ff5252"

# Blue (pause)
BLUE      = "#3d7dff"
BLUE_DK   = "#1a56d6"

# Purple (MP4)
PURPLE    = "#7c4dff"
PURPLE_DK = "#5528cc"
PURPLE_LT = "#aa80ff"

# Text
TEXT      = "#f0f0f8"
SUBTEXT   = "#7878a0"
DIMTEXT   = "#44445a"

# Status
SUCCESS   = "#00e676"
WARNING   = "#ffab00"
ERROR     = "#ff5252"

# Legacy aliases used in app.py / widgets
RED       = ACCENT
RED_DARK  = ACCENT_DK
RED_GLOW  = ACCENT_LT

# ── Fonts ─────────────────────────────────────────────────────────────────────
if sys.platform == "win32":
    FONT_UI   = "Segoe UI"
    FONT_MONO = ("Consolas", 9)
elif sys.platform == "darwin":
    FONT_UI   = "SF Pro Display"
    FONT_MONO = ("Menlo", 10)
else:
    FONT_UI   = "Ubuntu"
    FONT_MONO = ("Monospace", 9)

FONT_BODY  = (FONT_UI, 10)
FONT_LABEL = (FONT_UI, 9)
FONT_SMALL = (FONT_UI, 8)
FONT_TITLE = (FONT_UI, 18, "bold")
FONT_SUB   = (FONT_UI, 10)
FONT_BTN   = (FONT_UI, 11, "bold")
FONT_BTN2  = (FONT_UI, 10)

# ── Misc ──────────────────────────────────────────────────────────────────────
BROWSERS = ["none", "chrome", "firefox", "edge", "safari",
            "brave", "opera", "chromium"]

ARCHIVE_FILE = ".yt-dlp-archive.txt"
