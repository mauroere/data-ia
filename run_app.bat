@echo off
cd /d %~dp0
set PYTHONPATH=%CD%
python -m streamlit run main.py
pause
