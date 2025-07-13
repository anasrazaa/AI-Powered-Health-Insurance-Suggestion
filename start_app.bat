@echo off
echo Starting HealthCompare Application...
echo.

echo Starting FastAPI Backend...
start "HealthCompare Backend" cmd /k "cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo Waiting for backend to start...
timeout /t 3 /nobreak > nul

echo Starting React Frontend...
start "HealthCompare Frontend" cmd /k "cd frontend && npm start"

echo.
echo Application starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit this launcher...
pause > nul 