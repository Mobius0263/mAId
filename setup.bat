@echo off
echo 🤖 AI Companion Setup Script
echo ================================

echo.
echo 🔍 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo ✅ Python found!

echo.
echo 📦 Setting up virtual environment...
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
) else (
    echo ✅ Virtual environment already exists
)

echo.
echo ⚡ Activating environment and installing packages...
call .venv\Scripts\activate.bat

echo Installing core packages...
pip install --upgrade pip
pip install python-dotenv requests pillow transformers torch

echo Installing GUI packages...
pip install customtkinter pystray plyer

echo Installing optional packages...
pip install cx_Freeze auto-py-to-exe

echo.
echo 📝 Setting up configuration...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env"
        echo ✅ .env file created from template
        echo ⚠️  Please edit .env file and add your API keys
    ) else (
        echo ❌ .env.example not found
    )
) else (
    echo ✅ .env file already exists
)

echo.
echo ✅ Setup complete!
echo.
echo 🚀 To run AI Companion:
echo    - Double-click: ai_companion_launcher.py
echo    - Or run: python ai_companion_launcher.py
echo.
echo 💡 Don't forget to:
echo    1. Edit .env file with your Brave Search API key
echo    2. Make sure KoboldCPP is running (if using)
echo.
pause
