@echo off
echo ========================================
echo   AI Data Analyst - Glass UI Edition
echo ========================================
echo.
echo Starting the beautiful glassmorphism app...
echo.

cd /d "%~dp0"
call venv\Scripts\activate
streamlit run app_enterprise.py

pause
