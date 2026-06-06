# ytmp3.spec
# ─────────────────────────────────────────────────────────────────────────────
# PyInstaller spec for YT Downloader (pywebview UI)
#
# HOW TO BUILD:
#   1. Open a terminal in this folder
#   2. pip install pyinstaller pywebview yt-dlp
#   3. pyinstaller ytmp3.spec
#   4. Your exe will be at:  dist\YT-MP3\YT-MP3.exe
#   5. Then compile ytmp3_setup.iss with Inno Setup
# ─────────────────────────────────────────────────────────────────────────────

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# ── Collect pywebview's data files (JS/HTML assets it ships internally) ───────
webview_datas = collect_data_files('webview')

# ── Hidden imports pywebview needs on Windows ─────────────────────────────────
webview_hiddenimports = collect_submodules('webview')

a = Analysis(
    ['app_webview.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # pywebview internal assets
        *webview_datas,
        # our own packages (source, dest inside the bundle)
        ('core',   'core'),
        ('ui',     'ui'),
        ('assets', 'assets'),
        ('theme.py', '.'),
    ],
    hiddenimports=[
        # pywebview Windows backends
        *webview_hiddenimports,
        'webview',
        'webview.platforms.winforms',
        'webview.platforms.edgechromium',
        'clr',
        'clr_loader',
        # yt-dlp
        'yt_dlp',
        'yt_dlp.extractor',
        'yt_dlp.postprocessor',
        # stdlib extras
        'json',
        'threading',
        'pathlib',
        'tempfile',
        'shutil',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'PIL',
        'PyQt5',
        'PyQt6',
        'wx',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='YT-MP3',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # no black console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='assets/icon.ico',   # uncomment if you have a .ico file
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='YT-MP3',          # output folder: dist\YT-MP3\
)
