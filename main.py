#!/usr/bin/env python3
"""
main.py – Entry point. Launches the pywebview UI (app_webview.py).
Falls back to tkinter UI if pywebview is not available.
"""
import sys
import os


def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

    try:
        import webview  # noqa
        from app_webview import main as run
        run()
    except ModuleNotFoundError:
        # Fallback to tkinter if pywebview not installed
        from app import App
        App().mainloop()


if __name__ == "__main__":
    main()
