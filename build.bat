@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
cd /d "%~dp0"

echo ================================================================
echo   Controle de Gastos 2026 — Build do Instalador Windows
echo ================================================================
echo.

:: ── Verificar Python ──────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado. Instale Python 3.11+ e tente novamente.
    pause & exit /b 1
)

:: ── Instalar / atualizar dependencias ────────────────────────────
echo [1/5] Instalando dependencias Python...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet pillow pystray pyinstaller
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias.
    pause & exit /b 1
)
echo       OK

:: ── Gerar icone ───────────────────────────────────────────────────
echo [2/5] Gerando icone...
python icon.py
if errorlevel 1 (
    echo [ERRO] Falha ao gerar o icone. Verifique icon.py.
    pause & exit /b 1
)
echo       OK

:: ── Empacotar com PyInstaller ─────────────────────────────────────
echo [3/5] Empacotando com PyInstaller...
echo       (pode demorar varios minutos na primeira vez)
pyinstaller launcher.spec --clean --noconfirm
if errorlevel 1 (
    echo [ERRO] PyInstaller falhou. Veja os logs acima.
    pause & exit /b 1
)
echo       OK

:: ── Verificar Inno Setup ──────────────────────────────────────────
set "ISCC="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"
)

if "%ISCC%"=="" (
    echo.
    echo [AVISO] Inno Setup 6 nao encontrado.
    echo         Baixe em: https://jrsoftware.org/isdl.php
    echo         Apos instalar, execute este script novamente.
    echo.
    echo         O executavel sem instalador esta em:
    echo         dist\launcher\launcher.exe
    echo.
    pause & exit /b 0
)

:: ── Criar instalador ──────────────────────────────────────────────
echo [4/5] Criando instalador com Inno Setup...
if not exist Output mkdir Output
"%ISCC%" installer.iss
if errorlevel 1 (
    echo [ERRO] Inno Setup falhou. Veja os logs acima.
    pause & exit /b 1
)
echo       OK

:: ── Concluido ─────────────────────────────────────────────────────
echo.
echo [5/5] Tudo pronto!
echo.
echo   Executavel: dist\launcher\launcher.exe
echo   Instalador: Output\ControleDeGastos_Setup_v1.0.0.exe
echo.

:: Abrir pasta do instalador
if exist Output (
    explorer Output
)

pause
endlocal
