\
@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0\.."

if not exist ".venv\Scripts\python.exe" (
  py -3.13 -m venv .venv
)

call ".venv\Scripts\activate.bat"
python -m pip install -U pip
pip install -r requirements.txt

set ICON=
if exist "resources\icons\app.ico" (
  set ICON=--icon "resources\icons\app.ico"
)

pyinstaller --noconfirm --clean ^
  --name "PyDock" ^
  --windowed ^
  --distpath "build\dist" ^
  --workpath "build\work" ^
  --specpath "build\spec" ^
  --add-data "resources;resources" ^
  %ICON% ^
  main.py

echo.
echo Done. EXE: build\dist\PyDock\PyDock.exe
pause
