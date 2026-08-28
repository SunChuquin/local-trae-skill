@echo off
chcp 65001 > nul
echo.

cd /d "%~dp0frontend"

echo.
echo http://localhost:3000

npm run dev
