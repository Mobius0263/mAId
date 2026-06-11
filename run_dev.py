"""
Simple development runner for AI Companion
"""

import subprocess
import sys
import os
from pathlib import Path

def run_development():
    """Run the AI Companion in development mode"""
    print("🚀 AI Companion Development Runner")
    print("=" * 40)
    
    # Check if we're in the project's virtual environment
    project_root = Path(__file__).parent
    venv_path = project_root / ".venv"
    
    # Check if .venv exists and VIRTUAL_ENV points to it (or skip check if .venv doesn't exist)
    if venv_path.exists():
        virtual_env = os.environ.get("VIRTUAL_ENV", "")
        if not virtual_env or not Path(virtual_env).name == ".venv":
            print("❌ Project virtual environment not activated!")
            print("Please run:")
            print("   .venv\\Scripts\\activate")
            print("   python run_dev.py")
            input("\nPress Enter to exit...")
            return
        print("✅ Project virtual environment active")
    else:
        print("ℹ️  No .venv found, using system Python")
        # Check if we have a virtual environment at all
        if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("⚠️  Consider creating a virtual environment for better isolation")
    
    # Check KoboldCPP connection
    try:
        import requests
        response = requests.get("http://localhost:5001/api/v1/model", timeout=5)
        if response.status_code == 200:
            model_info = response.json()
            print(f"✅ KoboldCPP connected: {model_info.get('result', 'Unknown model')}")
        else:
            print("⚠️  KoboldCPP server responded with error")
    except Exception as e:
        print(f"❌ KoboldCPP not accessible: {e}")
        print("Make sure KoboldCPP is running on localhost:5001")
    
    print("\n🎯 Starting AI Companion...")
    
    # Run the main application
    try:
        from src.gui.tray_manager import create_gui_with_tray
        app, tray_manager = create_gui_with_tray()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    run_development()
