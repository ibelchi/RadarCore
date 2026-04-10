@echo off
title AI Investment Research Terminal
echo ===================================================
echo Starting the AI Investment Research Terminal...
echo ===================================================
echo.
echo Loading virtual environment and Streamlit...

cd /d "%~dp0"
call venv\Scripts\activate.bat
streamlit run app.py

echo.
echo The application has been closed.
pause
