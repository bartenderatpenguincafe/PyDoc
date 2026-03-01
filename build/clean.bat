\
@echo off
cd /d "%~dp0"
rmdir /s /q "dist" 2>nul
rmdir /s /q "work" 2>nul
rmdir /s /q "spec" 2>nul
echo cleaned
pause
