@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
 echo Zainstaluj Python 3.12 lub 3.13 z python.org i Python Launcher.
 goto fail
)
if not exist ".venv\Scripts\python.exe" py -3 -m venv .venv
if errorlevel 1 goto fail
".venv\Scripts\python.exe" -m pip install -r backend\requirements.txt
if errorlevel 1 goto fail
if not exist backend\.env copy backend\.env.example backend\.env >nul
pushd frontend
call npm ci --no-audit --no-fund
if errorlevel 1 (
 popd
 goto fail
)
call npm run build
if errorlevel 1 (
 popd
 goto fail
)
popd
echo Gotowe. Skonfiguruj baze i backend\.env wedlug README.md.
pause
exit /b 0
:fail
echo Instalacja nie powiodla sie. Przeczytaj komunikat powyzej.
pause
exit /b 1
