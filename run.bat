@echo off
title Dashboard de Gastos 2026
cd /d "%~dp0"
echo Iniciando dashboard...
call .venv\Scripts\activate.bat
streamlit run app.py
pause
