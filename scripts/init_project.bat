@echo off
setlocal

set "ROOT_SCRIPT=%~dp0..\init_project.bat"
call "%ROOT_SCRIPT%"
exit /b %ERRORLEVEL%
