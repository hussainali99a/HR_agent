@echo off
REM HR Recruitment Agent - Run Dashboard
REM Simply double-click this file to view the dashboard

cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "env-hr-agent\Scripts\activate.bat" (
    call env-hr-agent\Scripts\activate.bat
)

REM Run the dashboard
echo.
echo ========================================
echo Starting HR Recruitment Dashboard...
echo ========================================
echo.
echo Opening browser... (Check browser in a moment)
echo.

streamlit run dashboard.py

pause
