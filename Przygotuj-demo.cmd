@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 echo Najpierw uruchom Zainstaluj.cmd.
 pause
 exit /b 1
)
".venv\Scripts\python.exe" "scripts\setup_demo.py"
pause
