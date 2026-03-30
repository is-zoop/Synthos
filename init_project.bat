@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "TARGET_SCRIPT=%SCRIPT_DIR%initialize_project.py"

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py "%TARGET_SCRIPT%"
    exit /b %ERRORLEVEL%
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python "%TARGET_SCRIPT%"
    exit /b %ERRORLEVEL%
)

echo [ERROR] Python was not found in PATH. Please install Python or run initialize_project.py manually.
exit /b 1
