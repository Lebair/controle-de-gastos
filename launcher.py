"""
Controle de Gastos — Launcher (System Tray)
Gerencia o servidor Streamlit a partir do ícone na bandeja do sistema.
"""
import multiprocessing
multiprocessing.freeze_support()  # OBRIGATÓRIO para PyInstaller

import os
import sys
import time
import threading
import subprocess
import webbrowser
import winreg
from pathlib import Path

import pystray
from pystray import MenuItem as Item, Menu
from PIL import Image

# ─── Caminhos ─────────────────────────────────────────────────────────────────
if getattr(sys, "frozen", False):
    # Rodando como executável empacotado
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

APP_PY    = BASE_DIR / "app.py"
ICON_PNG  = BASE_DIR / "icon.png"
ICON_ICO  = BASE_DIR / "icon.ico"
PORT      = 8501
URL       = f"http://localhost:{PORT}"
APP_NAME  = "Controle de Gastos"
REG_KEY   = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_VALUE = APP_NAME

# ─── Estado global ────────────────────────────────────────────────────────────
_process: subprocess.Popen | None = None
_lock = threading.Lock()
_tray_icon: pystray.Icon | None = None


# ─── Utilitários ──────────────────────────────────────────────────────────────
def _streamlit_cmd() -> list[str]:
    """Monta o comando para iniciar o Streamlit."""
    if getattr(sys, "frozen", False):
        # Usa o Python embutido no pacote
        python = BASE_DIR / "_internal" / "python.exe"
        if not python.exists():
            python = Path(sys.executable).parent / "python.exe"
    else:
        python = Path(sys.executable)

    return [
        str(python), "-m", "streamlit", "run", str(APP_PY),
        "--server.headless", "true",
        "--server.port", str(PORT),
        "--browser.gatherUsageStats", "false",
    ]


def _is_running() -> bool:
    return _process is not None and _process.poll() is None


def _server_responding() -> bool:
    """Verifica se o servidor já está aceitando conexões."""
    import urllib.request
    try:
        urllib.request.urlopen(URL, timeout=2)
        return True
    except Exception:
        return False


def _notify(title: str, msg: str) -> None:
    """Exibe notificação Windows via system tray."""
    if _tray_icon:
        try:
            _tray_icon.notify(msg, title)
        except Exception:
            pass


def _update_icon() -> None:
    """Atualiza ícone e tooltip conforme estado do servidor."""
    if _tray_icon is None:
        return
    status = "🟢 Rodando" if _is_running() else "🔴 Parado"
    _tray_icon.title = f"{APP_NAME} — {status}"


# ─── Controle do servidor ─────────────────────────────────────────────────────
def start_server() -> None:
    global _process
    with _lock:
        if _is_running():
            return
        cmd = _streamlit_cmd()
        _process = subprocess.Popen(
            cmd,
            cwd=str(BASE_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )

    _notify(APP_NAME, "Iniciando servidor...")
    _update_icon()

    # Aguarda servidor responder e abre o browser
    def _wait_and_open():
        for _ in range(30):  # timeout 30 segundos
            if _server_responding():
                webbrowser.open(URL)
                _notify(APP_NAME, f"Servidor pronto! Acesse: {URL}")
                _update_icon()
                return
            time.sleep(1)
        _notify(APP_NAME, "Servidor demorou para responder — verifique os logs.")

    threading.Thread(target=_wait_and_open, daemon=True).start()


def stop_server() -> None:
    global _process
    with _lock:
        if _process is not None:
            try:
                _process.terminate()
                _process.wait(timeout=5)
            except Exception:
                try:
                    _process.kill()
                except Exception:
                    pass
            _process = None
    _notify(APP_NAME, "Servidor encerrado.")
    _update_icon()


def _watchdog() -> None:
    """Reinicia o servidor automaticamente se ele morrer."""
    while True:
        time.sleep(5)
        with _lock:
            if _process is not None and _process.poll() is not None:
                # Processo morreu inesperadamente — reinicia
                pass
            else:
                continue
        _notify(APP_NAME, "Servidor caiu. Reiniciando...")
        start_server()


# ─── Startup com Windows ──────────────────────────────────────────────────────
def _is_startup_enabled() -> bool:
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY)
        winreg.QueryValueEx(key, REG_VALUE)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False


def _toggle_startup(icon, item) -> None:
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_SET_VALUE)
        if _is_startup_enabled():
            winreg.DeleteValue(key, REG_VALUE)
            _notify(APP_NAME, "Removido da inicialização do Windows.")
        else:
            exe = str(Path(sys.executable) if not getattr(sys, "frozen", False)
                      else Path(sys.executable))
            winreg.SetValueEx(key, REG_VALUE, 0, winreg.REG_SZ, f'"{exe}"')
            _notify(APP_NAME, "Adicionado à inicialização do Windows.")
        winreg.CloseKey(key)
    except Exception as e:
        _notify(APP_NAME, f"Erro ao configurar startup: {e}")


# ─── Menu do tray ─────────────────────────────────────────────────────────────
def _menu_start(icon, item):
    threading.Thread(target=start_server, daemon=True).start()


def _menu_stop(icon, item):
    threading.Thread(target=stop_server, daemon=True).start()


def _menu_open(icon, item):
    webbrowser.open(URL)


def _menu_quit(icon, item):
    stop_server()
    icon.stop()


def _build_menu() -> Menu:
    return Menu(
        Item("🌐 Abrir Dashboard", _menu_open, default=True),
        Menu.SEPARATOR,
        Item("▶ Iniciar Servidor",  _menu_start, enabled=lambda item: not _is_running()),
        Item("⏹ Parar Servidor",   _menu_stop,  enabled=lambda item: _is_running()),
        Menu.SEPARATOR,
        Item(
            "🚀 Iniciar com o Windows",
            _toggle_startup,
            checked=lambda item: _is_startup_enabled(),
        ),
        Menu.SEPARATOR,
        Item(f"ℹ {APP_NAME} v1.0", None, enabled=False),
        Item("✕ Sair", _menu_quit),
    )


# ─── Carrega imagem do ícone ──────────────────────────────────────────────────
def _load_icon_image() -> Image.Image:
    if ICON_PNG.exists():
        return Image.open(ICON_PNG).convert("RGBA")
    # Fallback: gera ícone simples
    from PIL import ImageDraw
    img = Image.new("RGBA", (64, 64), (13, 27, 42, 255))
    d = ImageDraw.Draw(img)
    d.ellipse([10, 10, 54, 54], fill=(230, 126, 34))
    return img


# ─── Entry point ──────────────────────────────────────────────────────────────
def main():
    global _tray_icon

    # Inicia watchdog em background
    threading.Thread(target=_watchdog, daemon=True).start()

    # Carrega imagem do ícone
    img = _load_icon_image()

    # Cria ícone no tray
    _tray_icon = pystray.Icon(
        name=APP_NAME,
        icon=img,
        title=f"{APP_NAME} — 🔴 Parado",
        menu=_build_menu(),
    )

    # Inicia o servidor ao abrir
    threading.Thread(target=start_server, daemon=True).start()

    # Bloqueia até o usuário clicar em Sair
    _tray_icon.run()


if __name__ == "__main__":
    main()
