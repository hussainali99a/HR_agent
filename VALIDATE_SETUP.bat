@echo off
REM HR Recruitment Agent - System Validation
REM Double-click to verify everything is set up correctly

cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "env-hr-agent\Scripts\activate.bat" (
    call env-hr-agent\Scripts\activate.bat
)

REM Run validation
echo.
echo ========================================
echo Validating HR Agent System Setup
echo ========================================
echo.

python validate_setup.py

echo.
echo.
pause
