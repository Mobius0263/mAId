"""
AI Companion System Tray Integration
Provides system tray icon with quick access and notifications
"""

import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import threading
import sys
import time
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

class SystemTrayManager:
    """Manages system tray integration for AI Companion"""
    
    def __init__(self, gui_app=None):
        self.gui_app = gui_app
        self.icon = None
        self.is_running = False
        self.tray_thread = None
        
    def create_icon_image(self):
        """Create the system tray icon"""
        # Create a simple robot icon
        width = 64
        height = 64
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw robot head (circle)
        head_size = 40
        head_x = (width - head_size) // 2
        head_y = (height - head_size) // 2
        draw.ellipse([head_x, head_y, head_x + head_size, head_y + head_size], 
                    fill=(100, 149, 237, 255), outline=(70, 130, 180, 255), width=2)
        
        # Draw eyes
        eye_size = 6
        eye_y = head_y + 12
        left_eye_x = head_x + 10
        right_eye_x = head_x + head_size - 16
        
        draw.ellipse([left_eye_x, eye_y, left_eye_x + eye_size, eye_y + eye_size], fill=(255, 255, 255, 255))
        draw.ellipse([right_eye_x, eye_y, right_eye_x + eye_size, eye_y + eye_size], fill=(255, 255, 255, 255))
        
        # Draw mouth
        mouth_y = head_y + 25
        mouth_width = 12
        mouth_x = head_x + (head_size - mouth_width) // 2
        draw.rectangle([mouth_x, mouth_y, mouth_x + mouth_width, mouth_y + 3], fill=(255, 255, 255, 255))
        
        return image
    
    def show_window(self, icon=None, item=None):
        """Show the main window"""
        if self.gui_app and hasattr(self.gui_app, 'root'):
            self.gui_app.root.deiconify()
            self.gui_app.root.lift()
            self.gui_app.root.focus_force()
    
    def quick_screenshot(self, icon=None, item=None):
        """Take a quick screenshot"""
        if self.gui_app:
            self.gui_app.root.after(0, self.gui_app.quick_screenshot)
            self.show_window()
    
    def quick_search(self, icon=None, item=None):
        """Open quick search"""
        if self.gui_app:
            self.gui_app.root.after(0, self.gui_app.quick_search)
            self.show_window()
    
    def quit_application(self, icon=None, item=None):
        """Quit the entire application"""
        self.is_running = False
        if self.icon:
            self.icon.stop()
        if self.gui_app and hasattr(self.gui_app, 'root'):
            self.gui_app.root.quit()
        sys.exit()
    
    def create_menu(self):
        """Create the context menu for the tray icon"""
        return pystray.Menu(
            item('AI Companion', self.show_window, default=True),
            item('Quick Screenshot', self.quick_screenshot),
            item('Quick Search', self.quick_search),
            pystray.Menu.SEPARATOR,
            item('Quit', self.quit_application)
        )
    
    def start_tray(self):
        """Start the system tray in a separate thread"""
        if self.tray_thread and self.tray_thread.is_alive():
            print("[DEBUG] Tray already running")
            return
            
        print("[DEBUG] Creating tray icon...")
        try:
            # Create the icon
            self.icon = pystray.Icon(
                "AI_Companion",
                self.create_icon_image(),
                "AI Companion",
                self.create_menu()
            )
            
            print("[DEBUG] Starting tray thread...")
            # Use a non-daemon thread to prevent premature exit
            self.tray_thread = threading.Thread(target=self._run_tray, daemon=False)
            self.tray_thread.start()
            
            # Give the tray more time to initialize
            time.sleep(1.0)
            print(f"[DEBUG] Tray thread started: {self.tray_thread.is_alive()}")
            
            # Ensure icon is visible
            if self.icon:
                self.icon.visible = True
                print("[DEBUG] Icon visibility set to True")
                
        except Exception as e:
            print(f"[DEBUG] Error starting tray: {e}")
            import traceback
            traceback.print_exc()
    
    def _run_tray(self):
        """Run the tray icon (called in separate thread)"""
        try:
            print("[DEBUG] Tray thread running...")
            self.is_running = True
            self.icon.run()  # This will block until icon.stop() is called
        except Exception as e:
            print(f"[DEBUG] Tray thread error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("[DEBUG] Tray thread finished")
    
    def start_tray_thread(self):
        """Start the system tray in a separate thread"""
        tray_thread = threading.Thread(target=self.start_tray, daemon=True)
        tray_thread.start()
        return tray_thread
    
    def show_notification(self, title: str, message: str, timeout: int = 3):
        """Show a system notification"""
        if self.icon:
            try:
                self.icon.notify(message, title)
            except:
                pass  # Fail silently if notifications aren't supported

# Enhanced GUI with tray integration
def create_gui_with_tray():
    """Create the GUI application with system tray support"""
    import customtkinter as ctk
    from gui.main_app import AICompanionGUI
    
    # Create the GUI
    app = AICompanionGUI()
    
    # Create tray manager
    tray_manager = SystemTrayManager(app)
    
    # Override the closing behavior
    original_on_closing = app.on_closing
    
    def enhanced_on_closing():
        # Ensure tray is running first
        if not tray_manager.tray_thread or not tray_manager.tray_thread.is_alive():
            print("[INFO] Starting tray icon before minimizing...")
            tray_manager.start_tray()
            # Give it a moment to initialize
            time.sleep(1.0)
        
        if app.minimize_to_tray.get():
            print("[INFO] Minimizing to tray...")
            app.root.withdraw()
            tray_manager.show_notification("AI Companion", "Minimized to system tray. Right-click the tray icon to access features.")
        else:
            print("[INFO] Quitting application...")
            tray_manager.quit_application()
    
    app.on_closing = enhanced_on_closing
    
    # Start tray immediately in background
    print("[INFO] Initializing system tray...")
    tray_manager.start_tray()
    
    # Give the tray a moment to initialize
    time.sleep(1.0)
    
    # Ensure the main window is visible and focused
    print("[INFO] Showing main window...")
    app.root.deiconify()
    app.root.lift()
    app.root.focus_force()
    
    return app, tray_manager

if __name__ == "__main__":
    app, tray = create_gui_with_tray()
    app.run()
