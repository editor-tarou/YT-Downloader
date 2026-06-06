"""
app_webview.py – Replaces tkinter UI with a beautiful pywebview-based interface.

Run with:  python app_webview.py
"""
import os
import sys
import json
import threading
import tempfile
from pathlib import Path

# ── Dependency check ──────────────────────────────────────────────────────────

def _check_deps():
    missing = []
    try:
        import webview  # noqa
    except ModuleNotFoundError:
        missing.append("pywebview  →  pip install pywebview")
    try:
        import yt_dlp   # noqa
    except ModuleNotFoundError:
        missing.append("yt-dlp     →  pip install yt-dlp")
    if missing:
        print("=" * 60)
        print("  YT → MP3/MP4  ·  missing dependencies")
        print("=" * 60)
        for m in missing:
            print(f"\n  ✗  {m}")
        print("=" * 60)
        sys.exit(1)

_check_deps()

import webview
from core.downloader import DownloadSession
from core.fetcher    import fetch_info

# ── HTML UI ───────────────────────────────────────────────────────────────────

HTML = """<!DOCTYPE html>
<html lang="hu">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>YT Downloader</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Space+Mono:wght@400;700&display=swap');

*{box-sizing:border-box;margin:0;padding:0}

:root{
  --mp3:#e53935; --mp3g:rgba(229,57,53,.18); --mp3s:rgba(229,57,53,.08); --mp3m:rgba(229,57,53,.4);
  --mp4:#8b5cf6; --mp4g:rgba(139,92,246,.18); --mp4s:rgba(139,92,246,.08); --mp4m:rgba(139,92,246,.4);
  --ac:var(--mp3); --acg:var(--mp3g); --acs:var(--mp3s); --acm:var(--mp3m);
  --bg:#0f0f0f; --sf:#181818; --sf2:#222; --tx:#f5f5f5; --mu:#777; --br:rgba(255,255,255,.07);
  --tr:.5s cubic-bezier(.4,0,.2,1);
  --r:14px;
}

body{background:var(--bg);font-family:'DM Sans',sans-serif;color:var(--tx);
     display:flex;align-items:flex-start;justify-content:center;min-height:100vh;
     padding:2rem 1rem;-webkit-app-region:drag}

.app{width:100%;max-width:580px;-webkit-app-region:no-drag}

/* drag handle */
.titlebar{height:36px;-webkit-app-region:drag;display:flex;align-items:center;
  justify-content:flex-end;margin-bottom:.5rem;gap:6px;padding-right:2px}
.tb-btn{width:16px;height:16px;border-radius:50%;border:none;cursor:pointer;
  -webkit-app-region:no-drag;transition:filter .15s,transform .1s;
  display:flex;align-items:center;justify-content:center;
  font-size:0;position:relative;flex-shrink:0}
.tb-btn:hover{filter:brightness(1.2);transform:scale(1.12)}
.tb-btn:active{transform:scale(.95)}
.tb-close{background:#ff5f57}
.tb-min{background:#ffbd2e}
.tb-max{background:#28c840}
.tb-btn::after{content:'';position:absolute;inset:0;display:flex;
  align-items:center;justify-content:center;
  font-size:10px;font-weight:900;color:rgba(0,0,0,0.55);
  line-height:1;opacity:0;transition:opacity .15s;
  font-family:'Arial Black',sans-serif}
.tb-btn:hover::after{opacity:1}
.tb-close::after{content:'✕'}
.tb-min::after{content:'−';font-size:13px;margin-top:-1px}
.tb-max::after{content:'⛶';font-size:11px}

.logo{font-family:'Space Mono',monospace;font-size:12px;font-weight:700;
  letter-spacing:.2em;color:var(--ac);text-transform:uppercase;
  margin-bottom:2rem;display:flex;align-items:center;gap:10px;
  transition:color var(--tr)}

.dot{width:8px;height:8px;border-radius:50%;background:var(--ac);
  box-shadow:0 0 12px var(--ac);transition:background var(--tr),box-shadow var(--tr);
  animation:pulse 2s ease-in-out infinite}
@keyframes pulse{0%,100%{transform:scale(1);opacity:1}50%{transform:scale(1.4);opacity:.7}}

h1{font-size:1.9rem;font-weight:600;line-height:1.15;margin-bottom:.35rem;letter-spacing:-.03em}
.sub{color:var(--mu);font-size:14px;margin-bottom:1.75rem}

/* mode toggle */
.toggle{display:flex;gap:6px;margin-bottom:1.5rem;background:var(--sf);
  border-radius:13px;padding:5px;border:1px solid var(--br)}
.tbtn{flex:1;padding:9px;border:none;border-radius:10px;
  font-family:'Space Mono',monospace;font-size:12px;font-weight:700;
  letter-spacing:.08em;cursor:pointer;background:transparent;color:var(--mu);
  transition:background .3s,color .3s,box-shadow .3s}
.tbtn.act-mp3{background:var(--mp3s);color:var(--mp3);box-shadow:inset 0 0 0 1px var(--mp3m)}
.tbtn.act-mp4{background:var(--mp4s);color:var(--mp4);box-shadow:inset 0 0 0 1px var(--mp4m)}
.tbtn:hover:not(.act-mp3):not(.act-mp4){background:rgba(255,255,255,.04)}

/* url card */
.ucard{background:var(--sf);border:1px solid var(--br);border-radius:var(--r);
  padding:1.1rem 1.2rem;margin-bottom:.9rem;
  transition:border-color var(--tr),box-shadow var(--tr)}
.ucard:focus-within{border-color:var(--acm);box-shadow:0 0 0 3px var(--acs)}
.ulabel{font-size:11px;font-weight:500;letter-spacing:.12em;color:var(--mu);
  text-transform:uppercase;margin-bottom:9px}
.urow{display:flex;align-items:center;gap:10px}
.url-in{flex:1;background:transparent;border:none;outline:none;
  font-family:'DM Sans',sans-serif;font-size:15px;color:var(--tx);caret-color:var(--ac)}
.url-in::placeholder{color:var(--mu)}
.pbtn{background:var(--sf2);border:1px solid var(--br);color:var(--mu);
  border-radius:8px;padding:6px 12px;font-size:12px;font-family:'DM Sans',sans-serif;
  cursor:pointer;transition:color .2s,border-color .2s;white-space:nowrap}
.pbtn:hover{color:var(--tx);border-color:rgba(255,255,255,.15)}

/* folder row */
.frow{display:flex;align-items:center;gap:8px;margin-bottom:1rem;
  background:var(--sf);border:1px solid var(--br);border-radius:var(--r);
  padding:.75rem 1.1rem}
.frow .ulabel{margin:0;flex:none}
.fpath{flex:1;font-size:13px;color:var(--mu);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.fbtn{background:var(--sf2);border:1px solid var(--br);color:var(--mu);
  border-radius:8px;padding:5px 12px;font-size:12px;font-family:'DM Sans',sans-serif;
  cursor:pointer;transition:color .2s,border-color .2s;white-space:nowrap;flex:none}
.fbtn:hover{color:var(--tx);border-color:rgba(255,255,255,.15)}

/* chips */
.chips{display:flex;gap:7px;margin-bottom:1rem;flex-wrap:wrap}
.chip{padding:7px 14px;border-radius:999px;border:1px solid var(--br);
  background:var(--sf);font-size:13px;color:var(--mu);cursor:pointer;
  transition:all .25s;font-family:'DM Sans',sans-serif}
.chip.sel{color:var(--ac);border-color:var(--acm);background:var(--acs)}
.chip:hover:not(.sel){color:var(--tx);border-color:rgba(255,255,255,.15)}

/* mp4 extras */
.mp4x{display:none;gap:7px;margin-bottom:1rem;flex-wrap:wrap}
.mp4x.vis{display:flex}
.rchip{padding:6px 13px;border-radius:999px;border:1px solid var(--br);
  background:var(--sf);font-size:12px;color:var(--mu);cursor:pointer;
  transition:all .25s;font-family:'Space Mono',monospace}
.rchip.sel{color:var(--mp4);border-color:var(--mp4m);background:var(--mp4s)}
.rchip:hover:not(.sel){color:var(--tx);border-color:rgba(255,255,255,.15)}

/* download button */
.dlbtn{width:100%;padding:15px;border-radius:13px;border:none;
  background:var(--ac);color:#fff;font-family:'DM Sans',sans-serif;
  font-size:15px;font-weight:600;cursor:pointer;letter-spacing:.02em;
  position:relative;overflow:hidden;
  transition:background var(--tr),box-shadow var(--tr),transform .15s}
.dlbtn:hover:not(:disabled){box-shadow:0 8px 28px var(--acg);transform:translateY(-1px)}
.dlbtn:active:not(:disabled){transform:scale(.99)}
.dlbtn:disabled{opacity:.5;cursor:not-allowed}
.dlbtn::before{content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,rgba(255,255,255,.14) 0%,transparent 60%);pointer-events:none}

/* action row (pause/stop) */
.arow{display:flex;gap:8px;margin-top:.75rem}
.abtn{flex:1;padding:11px;border-radius:11px;border:1px solid var(--br);
  background:var(--sf);color:var(--mu);font-family:'DM Sans',sans-serif;
  font-size:13px;font-weight:500;cursor:pointer;transition:all .25s}
.abtn:hover:not(:disabled){border-color:rgba(255,255,255,.2);color:var(--tx)}
.abtn:disabled{opacity:.35;cursor:not-allowed}
.abtn.pause-act{background:rgba(61,125,255,.12);color:#3d7dff;border-color:rgba(61,125,255,.4)}

/* progress */
.prog{display:none;margin-top:1.25rem}
.prog.vis{display:block}
.phead{display:flex;justify-content:space-between;align-items:center;margin-bottom:9px}
.plabel{font-size:13px;color:var(--mu);font-weight:500}
.ppct{font-family:'Space Mono',monospace;font-size:13px;color:var(--ac);transition:color var(--tr)}
.ptrack{height:4px;background:var(--sf2);border-radius:999px;overflow:hidden}
.pfill{height:100%;border-radius:999px;background:var(--ac);width:0%;
  transition:width .35s ease,background var(--tr);box-shadow:0 0 10px var(--acm)}

/* stats */
.stats{display:flex;gap:8px;margin-top:1rem}
.stat{flex:1;background:var(--sf);border:1px solid var(--br);border-radius:11px;padding:11px 13px}
.slabel{font-size:11px;color:var(--mu);text-transform:uppercase;letter-spacing:.1em;margin-bottom:3px}
.sval{font-family:'Space Mono',monospace;font-size:14px;font-weight:700;
  color:var(--ac);transition:color var(--tr)}

/* done */
.done{display:none;align-items:center;gap:10px;background:var(--acs);
  border:1px solid var(--acm);border-radius:11px;padding:13px 15px;margin-top:1rem;
  font-size:14px;color:var(--ac);font-weight:500;
  transition:background var(--tr),border-color var(--tr),color var(--tr)}
.done.vis{display:flex}
.chk{width:22px;height:22px;border-radius:50%;background:var(--ac);
  display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:background var(--tr)}
.chk svg{width:12px;height:12px}

/* log */
.logwrap{background:var(--sf);border:1px solid var(--br);border-radius:var(--r);
  margin-top:1.25rem;padding:.85rem 1rem;max-height:160px;overflow-y:auto}
.logtitle{font-size:11px;font-weight:500;letter-spacing:.12em;color:var(--mu);
  text-transform:uppercase;margin-bottom:8px}
.logbox{font-family:'Space Mono',monospace;font-size:11px;line-height:1.7}
.log-ok{color:#00e676}.log-err{color:#ff5252}.log-warn{color:#ffab00}
.log-dim{color:var(--mu)}.log-info{color:var(--ac)}

/* ripple */
.ripple{position:absolute;border-radius:50%;background:rgba(255,255,255,.22);
  transform:scale(0);animation:rip .5s ease-out forwards;pointer-events:none}
@keyframes rip{to{transform:scale(5);opacity:0}}

/* flash overlay */
.flash-ov{position:fixed;inset:0;pointer-events:none;opacity:0;z-index:999;
  background:radial-gradient(ellipse at center,var(--ac) 0%,transparent 70%)}
.flash-ov.go{animation:flashAn .65s ease-out forwards}
@keyframes flashAn{0%{opacity:.16}100%{opacity:0}}

/* scrollbar */
::-webkit-scrollbar{width:4px}::-webkit-scrollbar-track{background:var(--sf)}
::-webkit-scrollbar-thumb{background:var(--br);border-radius:2px}
</style>
</head>
<body>

<div class="flash-ov" id="fov"></div>

<div class="app">

  <!-- custom titlebar -->
  <div class="titlebar">
    <button class="tb-btn tb-close" onclick="pywebview.api.close_window()" title="Close"></button>
    <button class="tb-btn tb-min"   onclick="pywebview.api.minimize_window()" title="Minimize"></button>
    <button class="tb-btn tb-max"   id="maxBtn" onclick="toggleMax()" title="Fullscreen"></button>
  </div>

  <div class="logo"><div class="dot" id="dot"></div>ytmp — downloader</div>

  <h1 id="title">Audio<br>Downloader</h1>
  <p class="sub" id="sub">Music and video from YouTube — lightning fast</p>

  <!-- MP3 / MP4 toggle -->
  <div class="toggle">
    <button class="tbtn act-mp3" id="bmp3" onclick="setMode('mp3')">♪ MP3</button>
    <button class="tbtn"         id="bmp4" onclick="setMode('mp4')">▶ MP4</button>
  </div>

  <!-- URL -->
  <div class="ucard">
    <div class="ulabel">YouTube Link</div>
    <div class="urow">
      <input class="url-in" id="urlIn" placeholder="https://youtube.com/watch?v=…" type="text">
      <button class="pbtn" onclick="pasteUrl()">Paste</button>
    </div>
  </div>

  <!-- Output folder -->
  <div class="frow">
    <div class="ulabel">Folder</div>
    <span class="fpath" id="fpath">~/Downloads</span>
    <button class="fbtn" onclick="pickFolder()">Browse…</button>
  </div>

  <!-- Quality chips (MP3) -->
  <div class="chips" id="qrow">
    <button class="chip sel" onclick="selQ(this,'128')">128 kbps</button>
    <button class="chip"     onclick="selQ(this,'192')">192 kbps</button>
    <button class="chip"     onclick="selQ(this,'320')">320 kbps</button>
  </div>

  <!-- Resolution chips (MP4) -->
  <div class="mp4x" id="rrow">
    <button class="rchip sel" onclick="selR(this,'720p   (HD)')">720p</button>
    <button class="rchip"     onclick="selR(this,'1080p  (FHD)')">1080p</button>
    <button class="rchip"     onclick="selR(this,'2160p  (4K)')">4K</button>
  </div>

  <!-- Download button -->
  <button class="dlbtn" id="dlBtn" onclick="startDl(event)">
    <span id="dlTxt">Start Download</span>
  </button>

  <!-- Pause / Stop -->
  <div class="arow">
    <button class="abtn" id="pauseBtn" disabled onclick="togglePause()">⏸ Pause</button>
    <button class="abtn" id="stopBtn"  disabled onclick="stopDl()">⏹ Stop</button>
  </div>

  <!-- Progress -->
  <div class="prog" id="progSec">
    <div class="phead">
      <span class="plabel" id="plabel">Processing…</span>
      <span class="ppct"   id="ppct">0%</span>
    </div>
    <div class="ptrack"><div class="pfill" id="pfill"></div></div>
    <div class="stats">
      <div class="stat"><div class="slabel">Speed</div><div class="sval" id="sSpeed">—</div></div>
      <div class="stat"><div class="slabel">ETA</div>    <div class="sval" id="sEta">—</div></div>
      <div class="stat"><div class="slabel">Format</div><div class="sval" id="sFmt">MP3</div></div>
    </div>
  </div>

  <!-- Done -->
  <div class="done" id="doneBox">
    <div class="chk" id="chkIco">
      <svg viewBox="0 0 12 12" fill="none">
        <path d="M2 6.5L4.5 9L10 3" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <span id="doneTxt">Download complete!</span>
  </div>

  <!-- Log -->
  <div class="logwrap">
    <div class="logtitle">Log</div>
    <div class="logbox" id="log"></div>
  </div>

</div><!-- .app -->

<script>
let mode = 'mp3', paused = false, downloading = false, maximized = false;
let quality = '128', resolution = '720p   (HD)';
let outDir = '';

// ── init ──────────────────────────────────────────────────────────────────────
window.addEventListener('load', () => {
  pywebview.api.get_default_dir().then(d => { outDir = d; document.getElementById('fpath').textContent = d; });
});

// ── mode switch ───────────────────────────────────────────────────────────────
function setMode(m) {
  if (m === mode) return;
  mode = m;
  const r = document.documentElement.style;
  if (m === 'mp4') {
    r.setProperty('--ac',  'var(--mp4)');  r.setProperty('--acg','var(--mp4g)');
    r.setProperty('--acs', 'var(--mp4s)'); r.setProperty('--acm','var(--mp4m)');
    document.getElementById('title').innerHTML = 'Video<br>Downloader';
    document.getElementById('sub').textContent  = 'YouTube videos in original quality';
    document.getElementById('dlTxt').textContent = 'Download Video';
    document.getElementById('sFmt').textContent  = 'MP4';
    document.getElementById('qrow').style.display = 'none';
    document.getElementById('rrow').classList.add('vis');
  } else {
    r.setProperty('--ac',  'var(--mp3)');  r.setProperty('--acg','var(--mp3g)');
    r.setProperty('--acs', 'var(--mp3s)'); r.setProperty('--acm','var(--mp3m)');
    document.getElementById('title').innerHTML = 'Audio<br>Downloader';
    document.getElementById('sub').textContent  = 'Music and video from YouTube — lightning fast';
    document.getElementById('dlTxt').textContent = 'Start Download';
    document.getElementById('sFmt').textContent  = 'MP3';
    document.getElementById('qrow').style.display = 'flex';
    document.getElementById('rrow').classList.remove('vis');
  }
  document.getElementById('bmp3').className = 'tbtn' + (m==='mp3'?' act-mp3':'');
  document.getElementById('bmp4').className = 'tbtn' + (m==='mp4'?' act-mp4':'');
  flash();
  resetProgress();
}

// ── chips ─────────────────────────────────────────────────────────────────────
function selQ(btn, val) {
  document.querySelectorAll('#qrow .chip').forEach(b => b.classList.remove('sel'));
  btn.classList.add('sel'); quality = val;
}
function selR(btn, val) {
  document.querySelectorAll('#rrow .rchip').forEach(b => b.classList.remove('sel'));
  btn.classList.add('sel'); resolution = val;
}

// ── paste / folder ────────────────────────────────────────────────────────────
function pasteUrl() {
  navigator.clipboard.readText().then(t => { document.getElementById('urlIn').value = t.trim(); }).catch(()=>{});
}
function pickFolder() {
  pywebview.api.pick_folder().then(d => {
    if (d) { outDir = d; document.getElementById('fpath').textContent = d; }
  });
}

// ── download ──────────────────────────────────────────────────────────────────
function startDl(e) {
  if (downloading) return;
  const url = document.getElementById('urlIn').value.trim();
  if (!url) { flashErr('No URL entered!'); return; }
  addRipple(e, document.getElementById('dlBtn'));
  downloading = true; paused = false;
  setButtons(true);
  resetProgress();
  document.getElementById('progSec').classList.add('vis');
  document.getElementById('doneBox').classList.remove('vis');
  document.getElementById('log').innerHTML = '';

  pywebview.api.start_download({
    url, outDir, mode,
    quality: mode === 'mp3' ? quality : '192',
    resolution: mode === 'mp4' ? resolution : 'best',
  });
}

function togglePause() {
  if (!downloading) return;
  paused = !paused;
  const btn = document.getElementById('pauseBtn');
  if (paused) {
    pywebview.api.pause_download();
    btn.textContent = '▶ Resume'; btn.classList.add('pause-act');
  } else {
    pywebview.api.resume_download();
    btn.textContent = '⏸ Pause'; btn.classList.remove('pause-act');
  }
}

function stopDl() { pywebview.api.stop_download(); }

// ── callbacks from Python (called via js_api) ─────────────────────────────────
function onProgress(data) {
  document.getElementById('plabel').textContent = data.title || 'Downloading…';
  document.getElementById('ppct').textContent   = data.pct || '0%';
  document.getElementById('pfill').style.width  = (parseFloat(data.pct) || 0) + '%';
  document.getElementById('sSpeed').textContent = data.speed || '—';
  document.getElementById('sEta').textContent   = data.eta   || '—';
}

function onLog(msg, tag) {
  const el = document.getElementById('log');
  const line = document.createElement('div');
  line.className = tag ? 'log-' + tag : '';
  line.textContent = msg;
  el.appendChild(line);
  el.parentElement.scrollTop = el.parentElement.scrollHeight;
}

function onFinished(summary, ok) {
  downloading = false; paused = false;
  setButtons(false);
  document.getElementById('pfill').style.width = ok ? '100%' : document.getElementById('pfill').style.width;
  document.getElementById('ppct').textContent  = ok ? '100%' : document.getElementById('ppct').textContent;
  document.getElementById('doneTxt').textContent = summary;
  document.getElementById('doneBox').classList.add('vis');
  flash();
}

// ── helpers ───────────────────────────────────────────────────────────────────
function setButtons(active) {
  document.getElementById('dlBtn').disabled    = active;
  document.getElementById('pauseBtn').disabled = !active;
  document.getElementById('stopBtn').disabled  = !active;
  if (!active) {
    document.getElementById('pauseBtn').textContent = '⏸ Pause';
    document.getElementById('pauseBtn').classList.remove('pause-act');
  }
}

function resetProgress() {
  document.getElementById('pfill').style.width = '0%';
  document.getElementById('ppct').textContent  = '0%';
  document.getElementById('plabel').textContent = 'Processing…';
  document.getElementById('sSpeed').textContent = '—';
  document.getElementById('sEta').textContent   = '—';
  document.getElementById('progSec').classList.remove('vis');
  document.getElementById('doneBox').classList.remove('vis');
}

function toggleMax() {
  maximized = !maximized;
  pywebview.api.toggle_maximize(maximized);
  const btn = document.getElementById('maxBtn');
  // swap icon: one big box vs two small boxes
  btn.style.setProperty('--max-icon', maximized ? '"❐"' : '"⛶"');
  if (maximized) {
    document.styleSheets[0].insertRule('.tb-max::after{content:"❐" !important}', 0);
  } else {
    document.styleSheets[0].insertRule('.tb-max::after{content:"⛶" !important}', 0);
  }
}

function flash() {
  const el = document.getElementById('fov');
  el.classList.remove('go'); void el.offsetWidth; el.classList.add('go');
}

function flashErr(msg) {
  onLog('⚠ ' + msg, 'err');
}

function addRipple(e, btn) {
  const r = document.createElement('div');
  r.className = 'ripple';
  const rect = btn.getBoundingClientRect();
  const sz = 60;
  r.style.cssText = `width:${sz}px;height:${sz}px;left:${e.clientX-rect.left-sz/2}px;top:${e.clientY-rect.top-sz/2}px`;
  btn.appendChild(r); setTimeout(()=>r.remove(), 600);
}
</script>
</body>
</html>
"""

# ── Python API (exposed to JS) ────────────────────────────────────────────────

class Api:
    def __init__(self):
        self._window   = None
        self._session: DownloadSession | None = None

    def set_window(self, w):
        self._window = w

    # ── Window controls ───────────────────────────────────────────────────────

    def close_window(self):
        if self._window:
            self._window.destroy()

    def minimize_window(self):
        if self._window:
            self._window.minimize()

    def toggle_maximize(self, maximized=False):
        if not self._window:
            return
        try:
            if maximized:
                self._window.maximize()
            else:
                self._window.restore()
        except Exception:
            try:
                self._window.toggle_fullscreen()
            except Exception:
                pass

    # ── Folder picker ─────────────────────────────────────────────────────────

    def get_default_dir(self):
        return str(Path.home() / "Downloads")

    def pick_folder(self):
        if self._window:
            result = self._window.create_file_dialog(
                webview.FOLDER_DIALOG
            )
            if result and len(result):
                return result[0]
        return None

    # ── Download controls ─────────────────────────────────────────────────────

    def start_download(self, params):
        url        = params.get("url", "")
        out_dir    = params.get("outDir", "").strip()
        if not out_dir:
            out_dir = str(Path.home() / "Downloads")
        fmt        = params.get("mode", "mp3")
        quality    = params.get("quality", "192")
        resolution = params.get("resolution", "best")

        def log(msg, tag=""):
            self._call_js("onLog", msg, tag)

        def progress(title, pct, speed, eta):
            self._call_js("onProgress", {"title": title, "pct": pct, "speed": speed, "eta": eta})

        def track_done(done, total, title):
            log(f"[{done}/{total}]  {title}", "ok")

        def finished(completed, failed):
            ok      = not failed
            summary = f"Done!  {len(completed)} downloaded"
            if failed:
                summary += f",  {len(failed)} failed."
            else:
                summary += "."
            self._call_js("onFinished", summary, ok)

        def status(msg):
            pass  # could update a status label

        self._session = DownloadSession(
            url=url,
            output_dir=out_dir,
            format=fmt,
            quality=quality,
            auth_opts={},
            sleep_min=2,
            sleep_max=5,
            sleep_req=1,
            use_archive=False,
            archive_path=os.path.join(out_dir, ".yt-archive.txt"),
            codec="any",
            resolution=resolution,
            embed_subs=False,
            embed_thumb=False,
            write_subs=False,
            on_log=log,
            on_progress=progress,
            on_track_done=track_done,
            on_finished=finished,
            on_status=status,
        )
        self._session.start()

    def pause_download(self):
        if self._session:
            self._session.pause()

    def resume_download(self):
        if self._session:
            self._session.resume()

    def stop_download(self):
        if self._session:
            self._session.stop()

    # ── JS bridge ─────────────────────────────────────────────────────────────

    def _call_js(self, fn, *args):
        if not self._window:
            return
        # Serialize args safely to JS
        js_args = ", ".join(json.dumps(a) for a in args)
        self._window.evaluate_js(f"{fn}({js_args})")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

    api = Api()

    window = webview.create_window(
        title        = "YT Downloader",
        html         = HTML,
        js_api       = api,
        width        = 660,
        height       = 820,
        min_size     = (500, 600),
        resizable    = True,
        frameless    = True,          # custom titlebar
        easy_drag    = True,
        background_color = "#0f0f0f",
    )
    api.set_window(window)
    webview.start(debug=False)


if __name__ == "__main__":
    main()
