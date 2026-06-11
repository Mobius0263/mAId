"""
AI Companion Launcher
Simple launcher for the AI Companion application
"""

import sys
import os
from pathlib import Path

def main():
    """Launch the AI Companion GUI application"""
    
    # Add src to path
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        # Import and run the GUI
        from gui.main_app import AICompanionGUI
        
        print("🚀 Starting AI Companion...")
        app = AICompanionGUI()
        app.run()
        
    except ImportError as e:
        print(f"❌ Failed to import GUI components: {e}")
        print("Make sure all dependencies are installed.")
        
    except Exception as e:
        print(f"❌ Failed to start AI Companion: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
