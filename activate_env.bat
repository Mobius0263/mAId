@echo off
REM AI Companion Project - Environment Activation Script
REM Run this script to activate the virtual environment

echo 🤖 AI Companion Project
echo Activating virtual environment...

call ".venv\Scripts\activate.bat"

echo ✅ Virtual environment activated!
echo 📍 Current environment: %VIRTUAL_ENV%

REM Test the environment
python --version
echo.
echo 💡 You can now run:
echo    python run_gui.py
echo    python get_started.py
echo    python test_smart_orchestrator.py
echo.
echo 🛑 To deactivate, type: deactivate
