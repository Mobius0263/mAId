# AI Companion Project - Environment Activation Script (PowerShell)
# Run this script to activate the virtual environment

Write-Host "🤖 AI Companion Project" -ForegroundColor Cyan
Write-Host "Activating virtual environment..." -ForegroundColor Yellow

# Activate the virtual environment
& ".\.venv\Scripts\Activate.ps1"

Write-Host "✅ Virtual environment activated!" -ForegroundColor Green
Write-Host "📍 Current environment: $env:VIRTUAL_ENV" -ForegroundColor Blue

# Test the environment
Write-Host "`n🐍 Python version:" -ForegroundColor Magenta
python --version

Write-Host "`n💡 You can now run:" -ForegroundColor Yellow
Write-Host "   python run_gui.py" -ForegroundColor White
Write-Host "   python get_started.py" -ForegroundColor White
Write-Host "   python test_smart_orchestrator.py" -ForegroundColor White

Write-Host "`n🛑 To deactivate, type: deactivate" -ForegroundColor Red
