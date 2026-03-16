@echo off
REM HR Recruitment Agent - Run Agent
REM Simply double-click this file to run the main agent

cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "env-hr-agent\Scripts\activate.bat" (
    call env-hr-agent\Scripts\activate.bat
)

REM Run the main program
echo.
echo ========================================
echo Running HR Recruitment Agent...
echo ========================================
echo.

python main_agent.py

echo.
echo.
echo ========================================
echo Agent completed!
echo Check the results in the dashboard
echo ========================================
echo.
pause
