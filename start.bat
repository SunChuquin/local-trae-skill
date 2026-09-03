@echo off
powershell -Command "Start-Process -WindowStyle Hidden -FilePath 'cmd' -ArgumentList '/c cd /d backend && ..\.venv310\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload'"
timeout /t 5 /nobreak > nul
powershell -Command "Start-Process -WindowStyle Hidden -FilePath 'cmd' -ArgumentList '/c cd /d frontend && npm run dev'"