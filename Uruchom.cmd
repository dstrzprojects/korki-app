@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 echo Najpierw wykonaj instalacje zgodnie z README.md.
 pause
 exit /b 1
)
".venv\Scripts\python.exe" "scripts\launch.py"
if errorlevel 1 pause
