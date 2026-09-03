@echo off
start "backend" cmd /k "cd /d backend && ..\.venv310\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 5 /nobreak > nul
start "frontend" cmd /k "cd /d frontend && npm run dev"
pause
