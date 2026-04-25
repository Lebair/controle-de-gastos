# launcher.spec — PyInstaller spec para o Controle de Gastos Launcher
# Gera: dist/launcher/launcher.exe
# Uso: pyinstaller launcher.spec

import os
import sys
from pathlib import Path

# Pasta raiz do projeto
BASE = os.path.dirname(os.path.abspath(SPEC))

# Localiza site-packages dinamicamente
import importlib, sysconfig
SP = sysconfig.get_paths()["purelib"]

# Caminhos dos pacotes principais
STREAMLIT_DIR = os.path.join(SP, "streamlit")
ALTAIR_DIR    = os.path.join(SP, "altair")

# ─── Arquivos a incluir ───────────────────────────────────────────────────────
datas = [
    # Streamlit frontend (HTML/CSS/JS e assets do servidor)
    (os.path.join(STREAMLIT_DIR, "static"),           "streamlit/static"),
    (os.path.join(STREAMLIT_DIR, "web"),              "streamlit/web"),
    (os.path.join(STREAMLIT_DIR, "runtime"),          "streamlit/runtime"),
    (os.path.join(STREAMLIT_DIR, "components"),       "streamlit/components"),
    # Altair (schemas Vega-Lite embutidos)
    (ALTAIR_DIR, "altair"),
    # Arquivos do projeto
    (os.path.join(BASE, "app.py"),                                     "."),
    (os.path.join(BASE, "config.json"),                                "."),
    (os.path.join(BASE, "Planilha de controle de gastos 2026.xlsx"),   "."),
    (os.path.join(BASE, "icon.png"),                                   "."),
    (os.path.join(BASE, "icon.ico"),                                   "."),
]

# ─── Imports ocultos (não detectados automaticamente) ────────────────────────
hidden_imports = [
    # Streamlit core
    "streamlit",
    "streamlit.web",
    "streamlit.web.cli",
    "streamlit.web.server",
    "streamlit.runtime",
    "streamlit.runtime.scriptrunner",
    "streamlit.components.v1",
    # Tornado (servidor HTTP/WS do Streamlit)
    "tornado",
    "tornado.web",
    "tornado.httpclient",
    "tornado.httputil",
    "tornado.websocket",
    "tornado.gen",
    "tornado.ioloop",
    # Watchdog (hot-reload do Streamlit)
    "watchdog",
    "watchdog.observers",
    "watchdog.observers.polling",
    "watchdog.events",
    # Metadata de pacotes (crítico para Streamlit 1.x)
    "importlib_metadata",
    "importlib.metadata",
    # Dados
    "pandas",
    "pandas._libs.tslibs",
    "openpyxl",
    "openpyxl.styles",
    "openpyxl.utils",
    # Gráficos
    "plotly",
    "plotly.graph_objects",
    "plotly.express",
    "altair",
    # Arrow / serialização
    "pyarrow",
    "pyarrow.vendored",
    # Outros
    "numpy",
    "pystray",
    "PIL",
    "PIL.Image",
    "PIL.ImageDraw",
    "PIL.ImageFont",
    "winreg",
    "urllib.request",
    "click",
    "toml",
    "rich",
    "validators",
    "packaging",
    "typing_extensions",
]

# ─── Análise ──────────────────────────────────────────────────────────────────
a = Analysis(
    [os.path.join(BASE, "launcher.py")],
    pathex=[BASE],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "scipy", "tensorflow", "torch"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="launcher",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,           # Sem janela preta
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(BASE, "icon.ico"),
    version=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="launcher",
)
