@echo off

:: Activate the virtual environment
call .venv\Scripts\activate.bat

:: Use the virtual environment's pip to install uvicorn if not already installed
.venv\Scripts\pip.exe show uvicorn >nul 2>nul || .venv\Scripts\pip.exe install uvicorn

:: Start the FastAPI server using the virtual environment's python -m uvicorn
.venv\Scripts\python.exe -m uvicorn server:app --host 0.0.0.0 --port 8000

:: @GPT-4o: Updated batch script to explicitly use the virtual environment's python and pip. 