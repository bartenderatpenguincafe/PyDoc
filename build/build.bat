@echo off
setlocal enabledelayedexpansion

REM ==========================================================
REM PyDock build script (Windows)
REM Требования:
REM   - Python 3.13 (py launcher или python в PATH)
REM   - PySide6 (будет проверено/установлено)
REM   - PyInstaller (будет проверено/установлено)
REM Результат сборки:
REM   build\dist\PyDock\PyDock.exe   (one-folder, portable)
REM   В папке build\dist\PyDock\ лежат DLL/плагины Qt и ресурсы.
REM ==========================================================

cd /d "%~dp0\.."
set "ROOT=%CD%"

REM ---- 1) Найти Python 3.13 ----
set "PY=py -3.13"
%PY% -c "import sys; assert sys.version_info[:2]==(3,13)" >nul 2>nul
if errorlevel 1 (
  set "PY=python"
  %PY% -c "import sys; assert sys.version_info[:2]==(3,13)" >nul 2>nul
  if errorlevel 1 (
    echo [ERROR] Python 3.13 не найден.
    echo         Установите Python 3.13 и/или py launcher.
    echo         Проверка:  py -3.13 --version   или   python --version
    exit /b 1
  )
)

for /f "delims=" %%v in ('%PY% -c "import sys;print(sys.version)"') do set "PYVER=%%v"
echo [OK] Python: %PYVER%

REM ---- 2) Виртуальное окружение ----
if not exist "%ROOT%\.venv\Scripts\python.exe" (
  echo [INFO] Создаю venv: %ROOT%\.venv
  %PY% -m venv "%ROOT%\.venv"
  if errorlevel 1 (
    echo [ERROR] Не удалось создать venv.
    exit /b 1
  )
)

call "%ROOT%\.venv\Scripts\activate.bat"
if errorlevel 1 (
  echo [ERROR] Не удалось активировать venv.
  exit /b 1
)

set "VPY=%ROOT%\.venv\Scripts\python.exe"
echo [OK] Venv python: %VPY%

REM ---- 3) pip + зависимости ----
%VPY% -m pip -V >nul 2>nul
if errorlevel 1 (
  echo [ERROR] pip отсутствует в venv.
  exit /b 1
)

echo [INFO] Обновляю pip...
%VPY% -m pip install -U pip >nul
if errorlevel 1 (
  echo [ERROR] Не удалось обновить pip.
  exit /b 1
)

REM Проверка PySide6
%VPY% -c "import PySide6" >nul 2>nul
if errorlevel 1 (
  echo [WARN] PySide6 не найден. Устанавливаю зависимости...
  if exist "%ROOT%\requirements.txt" (
    %VPY% -m pip install -r "%ROOT%\requirements.txt"
  ) else (
    %VPY% -m pip install PySide6
  )
  if errorlevel 1 (
    echo [ERROR] Установка PySide6/requirements не удалась.
    exit /b 1
  )
)

REM Повторная проверка PySide6
%VPY% -c "import PySide6; print('PySide6 OK')" >nul 2>nul
if errorlevel 1 (
  echo [ERROR] PySide6 всё ещё не импортируется.
  exit /b 1
)
echo [OK] PySide6 импортируется.

REM Проверка PyInstaller
%VPY% -c "import PyInstaller" >nul 2>nul
if errorlevel 1 (
  echo [WARN] PyInstaller не найден. Устанавливаю...
  %VPY% -m pip install pyinstaller
  if errorlevel 1 (
    echo [ERROR] Установка PyInstaller не удалась.
    exit /b 1
  )
)
echo [OK] PyInstaller готов.

REM ---- 4) Сборка ----
set "DIST=%ROOT%\build\dist"
set "WORK=%ROOT%\build\work"
set "SPEC=%ROOT%\build\spec"

echo.
echo [INFO] Сборка в EXE...
echo       Итоговый EXE будет здесь:
echo       %DIST%\PyDock\PyDock.exe
echo.

set "ICON_ARG="
if exist "%ROOT%\resources\icons\app.ico" (
  set "ICON_ARG=--icon %ROOT%\resources\icons\app.ico"
)

%VPY% -m PyInstaller --noconfirm --clean ^
  --name "PyDock" ^
  --windowed ^
  --collect-all PySide6 ^
  --distpath "%DIST%" ^
  --workpath "%WORK%" ^
  --specpath "%SPEC%" ^
  --add-data "%ROOT%\resources;resources" ^
  %ICON_ARG% ^
  "%ROOT%\main.py"

if errorlevel 1 (
  echo [ERROR] PyInstaller завершился с ошибкой.
  exit /b 1
)

echo.
echo [OK] Готово.
echo      EXE: %DIST%\PyDock\PyDock.exe
echo      Папка: %DIST%\PyDock\
echo.
pause