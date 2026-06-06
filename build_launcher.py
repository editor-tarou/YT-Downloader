"""
build_launcher.py
─────────────────
Called by the Inno Setup [Run] section after installation.
Creates  <install_dir>\launcher\YT-MP3.exe  — a native Windows
executable that launches main.py with no console window.

Strategy:
  1. Try PyInstaller (installed automatically if missing)
  2. Fall back to a .vbs wrapper if PyInstaller fails

Usage:
    python build_launcher.py <install_dir>
"""

import sys
import os
import subprocess
import shutil
import tempfile

def log(msg):
    # Inno hides stdout; write to a log file next to the script
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "install_log.txt")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def main():
    if len(sys.argv) < 2:
        log("build_launcher: no install_dir argument")
        sys.exit(1)

    install_dir  = sys.argv[1]
    launcher_dir = os.path.join(install_dir, "launcher")
    main_py      = os.path.join(install_dir, "main.py")
    exe_out      = os.path.join(launcher_dir, "YT-MP3.exe")

    os.makedirs(launcher_dir, exist_ok=True)

    log(f"build_launcher starting — install_dir={install_dir}")

    # ── Try PyInstaller ────────────────────────────────────────────────────────
    try:
        import PyInstaller  # noqa: F401
        log("PyInstaller already present")
    except ImportError:
        log("Installing PyInstaller…")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", "pyinstaller"],
            check=True,
        )

    try:
        # Build a single-file, no-console exe
        result = subprocess.run(
            [
                sys.executable, "-m", "PyInstaller",
                "--onefile",
                "--noconsole",
                "--name", "YT-MP3",
                "--distpath", launcher_dir,
                "--workpath", os.path.join(install_dir, "_build"),
                "--specpath", os.path.join(install_dir, "_build"),
                # Add all app packages so the exe finds them at runtime
                "--add-data", f"{install_dir};.",
                "--paths", install_dir,
                main_py,
            ],
            capture_output=True, text=True,
        )
        if result.returncode == 0 and os.path.isfile(exe_out):
            log("PyInstaller build succeeded")
            _cleanup(install_dir)
            return
        else:
            log(f"PyInstaller failed (rc={result.returncode})")
            log(result.stderr[-1000:])
    except Exception as e:
        log(f"PyInstaller exception: {e}")

    # ── Fallback: VBS wrapper → no console window ──────────────────────────────
    log("Falling back to VBS + stub exe")
    _create_vbs_launcher(install_dir, launcher_dir, main_py, exe_out)


def _create_vbs_launcher(install_dir, launcher_dir, main_py, exe_out):
    """
    Write a .vbs that runs python main.py with no window,
    then wrap it in a tiny stub .exe using a bat→exe trick or just
    leave the .vbs and create a .bat shim named YT-MP3.exe won't work,
    so we write a proper pythonw wrapper instead.
    """
    pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if not os.path.isfile(pythonw):
        pythonw = sys.executable   # last resort — shows console

    # Write a .vbs launcher (Inno shortcut will point here)
    vbs_path = os.path.join(launcher_dir, "YT-MP3.vbs")
    with open(vbs_path, "w") as f:
        f.write(
            f'Set sh = CreateObject("WScript.Shell")\n'
            f'sh.Run """{ pythonw }""" & " """ & _\n'
            f'  ""{main_py}"" ", 0, False\n'
        )

    # Write a minimal stub .bat and rename to .exe is not valid.
    # Instead write a proper "launcher" .py compiled with pythonw
    # into a .pyw (double-clickable, no console):
    pyw_path = os.path.join(launcher_dir, "YT-MP3.pyw")
    with open(pyw_path, "w") as f:
        f.write(
            f"import subprocess, sys, os\n"
            f"os.chdir(r'{install_dir}')\n"
            f"subprocess.Popen([r'{pythonw}', r'{main_py}'])\n"
        )

    # Create a tiny wrapper that Inno's shortcut can point to.
    # We write a self-extracting vbs approach: copy wscript as the "exe"
    # is not possible, so we use a batch-to-exe approach via a .bat file
    # clearly named, and update the .iss shortcut target to the .vbs.
    # Since we can't rename arbitrary binaries, write a note for the installer:
    note = os.path.join(launcher_dir, "README_LAUNCHER.txt")
    with open(note, "w") as f:
        f.write(
            "PyInstaller was unavailable during install.\n"
            "Launcher files created:\n"
            f"  {vbs_path}  ← double-click or use Start Menu shortcut\n"
            f"  {pyw_path}  ← also runnable with pythonw\n\n"
            "To rebuild with a proper .exe:\n"
            "  pip install pyinstaller\n"
            f"  python build_launcher.py \"{install_dir}\"\n"
        )

    log(f"VBS fallback written to {vbs_path}")


def _cleanup(install_dir):
    for d in ["_build"]:
        p = os.path.join(install_dir, d)
        if os.path.isdir(p):
            shutil.rmtree(p, ignore_errors=True)


if __name__ == "__main__":
    main()
