#!/usr/bin/env python3
"""
install.py – YT → MP3 Installer
────────────────────────────────
Installs Python dependencies (yt-dlp), checks for ffmpeg,
and creates a platform-appropriate launcher so you can run
the app without opening a terminal.

Usage:
    python install.py            # interactive
    python install.py --silent   # no prompts, just install
"""

import sys
import os
import subprocess
import shutil
import platform
import argparse

APP_NAME    = "YT → MP3"
APP_VERSION = "2.0"
REQUIRES    = ["yt-dlp"]

HERE = os.path.dirname(os.path.abspath(__file__))

# ── ANSI colours (skipped on Windows without ANSI support) ───────────────────
if sys.platform == "win32":
    import ctypes
    ctypes.windll.kernel32.SetConsoleMode(
        ctypes.windll.kernel32.GetStdHandle(-11), 7
    )

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def _c(colour, text):
    return f"{colour}{text}{RESET}"

def _header():
    print()
    print(_c(BOLD, "=" * 60))
    print(_c(RED,  f"  ▶  {APP_NAME}  ·  Installer  v{APP_VERSION}"))
    print(_c(BOLD, "=" * 60))
    print()

def _ok(msg):   print(f"  {_c(GREEN,  '✓')}  {msg}")
def _warn(msg): print(f"  {_c(YELLOW, '!')}  {msg}")
def _err(msg):  print(f"  {_c(RED,    '✗')}  {msg}")
def _info(msg): print(f"  {_c(CYAN,   '→')}  {msg}")


# ── Checks ────────────────────────────────────────────────────────────────────

def check_python():
    v = sys.version_info
    if v < (3, 10):
        _err(f"Python 3.10+ required (you have {v.major}.{v.minor})")
        sys.exit(1)
    _ok(f"Python {v.major}.{v.minor}.{v.micro}")


def check_tkinter():
    try:
        import tkinter  # noqa: F401
        _ok("tkinter  (built-in GUI library)")
    except ModuleNotFoundError:
        _err("tkinter not found")
        if sys.platform.startswith("linux"):
            _info("Fix:  sudo apt install python3-tk")
        elif sys.platform == "darwin":
            _info("Fix:  brew install python-tk")
        else:
            _info("Re-install Python and tick 'tcl/tk' in the installer.")
        sys.exit(1)


def check_ffmpeg():
    if shutil.which("ffmpeg"):
        _ok("ffmpeg  (audio conversion)")
        return True
    _warn("ffmpeg not found — MP3 conversion will fail!")
    _info("Install it:")
    if sys.platform == "win32":
        _info("  winget install ffmpeg        — or —  choco install ffmpeg")
    elif sys.platform == "darwin":
        _info("  brew install ffmpeg")
    else:
        _info("  sudo apt install ffmpeg")
    return False


# ── Install Python packages ───────────────────────────────────────────────────

def install_packages():
    _info("Installing / upgrading Python packages…")
    for pkg in REQUIRES:
        _info(f"  pip install --upgrade {pkg}")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", pkg],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            _ok(f"{pkg} installed")
        else:
            _err(f"Failed to install {pkg}")
            print(result.stderr[-600:])
            sys.exit(1)


# ── Launchers ─────────────────────────────────────────────────────────────────

def create_launcher_windows():
    """Create a .bat file + a .vbs wrapper (no terminal flash)."""
    bat = os.path.join(HERE, "ytmp3.bat")
    vbs = os.path.join(HERE, "YT-MP3.vbs")

    with open(bat, "w") as f:
        f.write(f'@echo off\n"{sys.executable}" "{os.path.join(HERE, "main.py")}"\n')

    with open(vbs, "w") as f:
        f.write(
            f'CreateObject("WScript.Shell").Run _\n'
            f'  "cmd /c ""{bat}""", 0, False\n'
        )

    # Desktop shortcut via PowerShell
    desktop = os.path.join(os.path.expanduser("~"), "Desktop", "YT-MP3.lnk")
    try:
        ps = (
            f"$s=(New-Object -COM WScript.Shell).CreateShortcut('{desktop}');"
            f"$s.TargetPath='{vbs}';"
            f"$s.Description='YouTube to MP3 downloader';"
            f"$s.Save()"
        )
        subprocess.run(["powershell", "-Command", ps],
                       capture_output=True, check=False)
        _ok(f"Desktop shortcut: {desktop}")
    except Exception:
        pass

    _ok(f"Windows launcher: {vbs}")


def create_launcher_mac():
    """Create a simple .command file (double-clickable in Finder)."""
    cmd = os.path.join(HERE, "YT-MP3.command")
    with open(cmd, "w") as f:
        f.write("#!/bin/bash\n")
        f.write(f'cd "{HERE}"\n')
        f.write(f'"{sys.executable}" main.py\n')
    os.chmod(cmd, 0o755)
    _ok(f"macOS launcher: {cmd}  (double-click in Finder)")


def create_launcher_linux():
    """Create a .desktop entry."""
    desktop_dir = os.path.expanduser("~/.local/share/applications")
    os.makedirs(desktop_dir, exist_ok=True)
    path = os.path.join(desktop_dir, "ytmp3.desktop")
    with open(path, "w") as f:
        f.write(
            f"[Desktop Entry]\n"
            f"Name=YT → MP3\n"
            f"Comment=YouTube to MP3 Downloader\n"
            f"Exec={sys.executable} {os.path.join(HERE, 'main.py')}\n"
            f"Icon=multimedia-audio-player\n"
            f"Terminal=false\n"
            f"Type=Application\n"
            f"Categories=AudioVideo;Audio;\n"
        )
    os.chmod(path, 0o755)

    # Also drop a shell script next to the code
    sh = os.path.join(HERE, "ytmp3.sh")
    with open(sh, "w") as f:
        f.write("#!/bin/bash\n")
        f.write(f'cd "{HERE}"\n')
        f.write(f'"{sys.executable}" main.py "$@"\n')
    os.chmod(sh, 0o755)

    _ok(f"Linux .desktop entry: {path}")
    _ok(f"Shell launcher:       {sh}")


def create_launcher():
    p = sys.platform
    if p == "win32":
        create_launcher_windows()
    elif p == "darwin":
        create_launcher_mac()
    else:
        create_launcher_linux()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description=f"{APP_NAME} installer")
    parser.add_argument("--silent", action="store_true",
                        help="skip confirmation prompts")
    args = parser.parse_args()

    _header()

    print(_c(BOLD, "  Checking requirements…"))
    print()
    check_python()
    check_tkinter()
    has_ffmpeg = check_ffmpeg()
    print()

    if not args.silent:
        try:
            ans = input("  Continue with installation? [Y/n] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            ans = "n"
        if ans not in ("", "y", "yes"):
            print("  Cancelled.")
            sys.exit(0)
        print()

    install_packages()
    print()

    _info("Creating launcher…")
    try:
        create_launcher()
    except Exception as exc:
        _warn(f"Could not create launcher: {exc}")

    print()
    print(_c(BOLD, "=" * 60))
    if has_ffmpeg:
        print(_c(GREEN, f"  ✓  {APP_NAME} is ready!"))
    else:
        print(_c(YELLOW, f"  !  {APP_NAME} installed — but ffmpeg is missing."))
        print(_c(YELLOW, "     Install ffmpeg first, then re-run this script."))
    print()
    print(f"  Run the app:  python main.py")
    print(_c(BOLD, "=" * 60))
    print()


if __name__ == "__main__":
    main()
