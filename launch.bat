@echo off
echo ========================================
echo GameCore Monitor - Quick Launcher
echo ========================================
echo.
echo Starting GameCore Monitor...
echo Dashboard will open in your browser.
echo.
echo Press Ctrl+C to stop the monitor.
echo ========================================
echo.

cd /d "%~dp0"
".venv\Scripts\python.exe" -m streamlit run app.py --theme.base dark

pause
