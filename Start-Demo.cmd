@echo off
cd /d "%~dp0"
python tools\serve_demo.py
if errorlevel 1 pause
