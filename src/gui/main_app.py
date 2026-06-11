"""
AI Companion GUI - Modern UI Application
A SillyTavern-inspired interface optimized for AI companion tasks
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import sys
import os
from pathlib import Path
import json
from typing import Dict, Any, Optional
import time
from datetime import datetime

# Add src to path for imports
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import UI configuration
try:
    from core.ui_config import ui_config
    from core.chat_history import get_chat_history_manager
except ImportError:
    # Fallback if config module isn't available
    print("Warning: UI config module not found, using defaults")
    class FallbackConfig:
        def get_font_size(self, element_type="base"):
            base_size = 14
            if element_type == "input": return int(base_size * 0.9)
            elif element_type == "h1": return base_size + 4
            elif element_type == "h2": return base_size + 2
            elif element_type == "h3": return base_size + 1
            return base_size
        def get_font_family(self, font_type="normal"):
            return "Consolas" if font_type == "code" else "Segoe UI"
        def get_font_scale_range(self): return (50, 300)
        def get_font_scale(self): return 100
        def set_font_scale(self, percentage): return True
        def get_color(self, color_name): 
            colors = {"primary": "#0078d4", "error": "#d13438", "warning": "#ff8c00", "code_bg": "#1e1e1e", "code_fg": "#d4d4d4"}
            return colors.get(color_name, "#000000")
    ui_config = FallbackConfig()
    
    # Fallback chat history manager
    class FallbackChatHistory:
        def get_current_session(self): return None
        def list_sessions(self): return []
        def create_new_session(self, name): return "default"
        def switch_session(self, session_id): return True
        def delete_session(self, session_id): return True
        def rename_session(self, session_id, name): return True
        def update_current_session_history(self, history): pass
        def load_session_history(self, session_id): return []
    get_chat_history_manager = lambda: FallbackChatHistory()

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # "dark", "light", or "system"
ctk.set_default_color_theme("blue")  # "blue", "green", or "dark-blue"

class AICompanionGUI:
    """Modern GUI for AI Companion with system tray support"""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("AI Companion")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Initialize variables
        self.orchestrator = None
        self.conversation_history = []
        self.is_processing = False
        self.character_name = "AI Companion"  # Default name until character loads
        self.message_id_counter = 0  # For unique message IDs
        self.selected_message_id = None  # Track selected message for context menu
        
        # Initialize chat history manager
        self.chat_history_manager = get_chat_history_manager()
        
        # Load current session history if available
        current_session = self.chat_history_manager.get_current_session()
        if current_session and current_session.conversation_history:
            self.conversation_history = current_session.conversation_history.copy()
            # Update message counter based on existing messages
            if self.conversation_history:
                max_id = max((msg.get("id", 0) for msg in self.conversation_history), default=0)
                self.message_id_counter = max_id
        
        # UI Configuration
        self.ui_config = ui_config
        
        # Configure grid weights
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        self.setup_ui()
        
        # Show initial loading message if no conversation history exists
        if not self.conversation_history:
            self.add_message("System", "🔄 Loading AI Companion... Please wait.", is_user=False)
        else:
            # Display existing conversation history
            self.refresh_chat_display()
        
        self.load_orchestrator()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        """Setup the main UI components"""
        
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Chat Session", command=self.create_new_chat_tab)
        file_menu.add_command(label="Manage Sessions", command=self.show_session_manager)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Font Settings", command=self.show_font_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Help", command=self.show_help)
        
        # Left sidebar for tools and status
        self.sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_rowconfigure(10, weight=1)
        
        # Title
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="AI Companion", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Status section
        self.status_frame = ctk.CTkFrame(self.sidebar)
        self.status_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="System Status", font=ctk.CTkFont(weight="bold"))
        self.status_label.pack(pady=5)
        
        self.brain_status = ctk.CTkLabel(self.status_frame, text="🧠 Brain: Loading...", font=ctk.CTkFont(size=12))
        self.brain_status.pack(anchor="w", padx=10)
        
        self.tools_status = ctk.CTkLabel(self.status_frame, text="⚙️ Tools: Loading...", font=ctk.CTkFont(size=12))
        self.tools_status.pack(anchor="w", padx=10)
        
        self.character_status = ctk.CTkLabel(self.status_frame, text="🎭 Character: Loading...", font=ctk.CTkFont(size=12))
        self.character_status.pack(anchor="w", padx=10)
        
        # Quick actions
        self.actions_frame = ctk.CTkFrame(self.sidebar)
        self.actions_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(self.actions_frame, text="Quick Actions", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        self.screenshot_btn = ctk.CTkButton(
            self.actions_frame, 
            text="📸 Screenshot", 
            command=self.quick_screenshot,
            width=140
        )
        self.screenshot_btn.pack(pady=2)
        
        self.search_btn = ctk.CTkButton(
            self.actions_frame, 
            text="🔍 Web Search", 
            command=self.quick_search,
            width=140
        )
        self.search_btn.pack(pady=2)
        
        self.clear_btn = ctk.CTkButton(
            self.actions_frame, 
            text="🗑️ Clear Chat", 
            command=self.clear_conversation,
            width=140
        )
        self.clear_btn.pack(pady=2)
        
        self.format_help_btn = ctk.CTkButton(
            self.actions_frame, 
            text="📝 Format Help", 
            command=self.show_format_help,
            width=140
        )
        self.format_help_btn.pack(pady=2)
        
        self.session_manager_btn = ctk.CTkButton(
            self.actions_frame, 
            text="💬 Chat Sessions", 
            command=self.show_session_manager,
            width=140
        )
        self.session_manager_btn.pack(pady=2)
        
        # Settings
        self.settings_frame = ctk.CTkFrame(self.sidebar)
        self.settings_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(self.settings_frame, text="Settings", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        # Font size control
        self.font_size_frame = ctk.CTkFrame(self.settings_frame)
        self.font_size_frame.pack(fill="x", padx=5, pady=2)
        
        ctk.CTkLabel(self.font_size_frame, text="Font Size:", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=5)
        
        # Font size slider (percentage-based)
        min_scale, max_scale = self.ui_config.get_font_scale_range()
        self.font_size_slider = ctk.CTkSlider(
            self.font_size_frame,
            from_=min_scale,
            to=max_scale,
            number_of_steps=(max_scale - min_scale) // 10,  # 10% increments
            command=self.change_font_scale,
            width=120
        )
        self.font_size_slider.set(self.ui_config.get_font_scale())
        self.font_size_slider.pack(padx=5, pady=2)
        
        # Font size label (shows percentage)
        current_scale = self.ui_config.get_font_scale()
        self.font_size_label = ctk.CTkLabel(
            self.font_size_frame, 
            text=f"{current_scale}%", 
            font=ctk.CTkFont(size=10)
        )
        self.font_size_label.pack(padx=5, pady=(0, 5))
        
        self.always_on_top = ctk.CTkCheckBox(self.settings_frame, text="Always on top")
        self.always_on_top.pack(anchor="w", padx=10, pady=2)
        
        self.minimize_to_tray = ctk.CTkCheckBox(self.settings_frame, text="Minimize to tray", state="normal")
        self.minimize_to_tray.pack(anchor="w", padx=10, pady=2)
        self.minimize_to_tray.select()  # Default to enabled
        
        # Main chat area
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)  # Changed to 1 to accommodate tabs
        
        # Chat tabs frame
        self.tabs_frame = ctk.CTkFrame(self.main_frame)
        self.tabs_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        self.tabs_frame.grid_columnconfigure(0, weight=1)
        
        self.setup_chat_tabs()
        
        # Chat display
        self.chat_frame = ctk.CTkFrame(self.main_frame)
        self.chat_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 5))
        self.chat_frame.grid_columnconfigure(0, weight=1)
        self.chat_frame.grid_rowconfigure(0, weight=1)
        
        self.chat_display = ctk.CTkTextbox(
            self.chat_frame,
            wrap="word",
            font=ctk.CTkFont(size=self.ui_config.get_font_size(), family=self.ui_config.get_font_family()),
            state="disabled"
        )
        self.chat_display.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure text tags for formatting
        self.setup_text_formatting()
        
        # Input area
        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))  # Changed to row 2
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_rowconfigure(0, weight=1)
        
        # Use CTkTextbox instead of CTkEntry for multi-line input with wrapping
        self.input_entry = ctk.CTkTextbox(
            self.input_frame,
            font=ctk.CTkFont(size=self.ui_config.get_font_size("input")),
            height=60,  # Start with a reasonable height
            wrap="word"  # Enable word wrapping
        )
        self.input_entry.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        # Add placeholder text manually since CTkTextbox doesn't have placeholder_text
        self.input_placeholder = "Type your message... (Use **bold**, *italic*, `code`, # headers)\nPress Ctrl+Enter to send"
        self.input_entry.insert("1.0", self.input_placeholder)
        self.input_entry.configure(text_color="gray60")  # Make placeholder text gray
        
        # Bind events for placeholder behavior and sending
        self.input_entry.bind("<FocusIn>", self.on_input_focus_in)
        self.input_entry.bind("<FocusOut>", self.on_input_focus_out)
        
        # Enter key sends message, Shift+Enter creates new line
        self.input_entry.bind("<Return>", self.send_message)
        self.input_entry.bind("<Shift-Return>", self.insert_newline)
        
        # Also keep Ctrl+Enter as alternative for sending
        self.input_entry.bind("<Control-Return>", self.send_message)
        self.input_entry.bind("<Control-KeyPress-Return>", self.send_message)
        
        self.send_button = ctk.CTkButton(
            self.input_frame,
            text="Send",
            command=self.send_message,
            width=80,
            height=40
        )
        self.send_button.grid(row=0, column=1, padx=(5, 10), pady=10)
        
        # Initial system message - will be updated when orchestrator loads
        
    def setup_chat_tabs(self):
        """Setup the chat tabs interface"""
        # Tab controls frame
        self.tab_controls = ctk.CTkFrame(self.tabs_frame)
        self.tab_controls.pack(fill="x", padx=5, pady=5)
        
        # New tab button
        self.new_tab_btn = ctk.CTkButton(
            self.tab_controls,
            text="+",
            width=30,
            height=30,
            command=self.create_new_chat_tab,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.new_tab_btn.pack(side="left", padx=(0, 10))
        
        # Tabs container with scrollable frame
        self.tabs_container = ctk.CTkScrollableFrame(
            self.tab_controls,
            orientation="horizontal",
            height=40
        )
        self.tabs_container.pack(side="left", fill="x", expand=True)
        
        # Chat management buttons
        self.chat_management_frame = ctk.CTkFrame(self.tab_controls)
        self.chat_management_frame.pack(side="right", padx=(10, 0))
        
        self.rename_tab_btn = ctk.CTkButton(
            self.chat_management_frame,
            text="Rename",
            width=60,
            height=30,
            command=self.rename_current_tab,
            font=ctk.CTkFont(size=10)
        )
        self.rename_tab_btn.pack(side="left", padx=2)
        
        self.delete_tab_btn = ctk.CTkButton(
            self.chat_management_frame,
            text="Delete",
            width=60,
            height=30,
            command=self.delete_current_tab,
            font=ctk.CTkFont(size=10),
            fg_color="#d13438",
            hover_color="#b02a30"
        )
        self.delete_tab_btn.pack(side="left", padx=2)
        
        # Load and display existing tabs
        self.refresh_chat_tabs()
    
    def refresh_chat_tabs(self):
        """Refresh the chat tabs display"""
        # Clear existing tab buttons
        for widget in self.tabs_container.winfo_children():
            widget.destroy()
        
        # Get all sessions
        sessions = self.chat_history_manager.list_sessions()
        current_session = self.chat_history_manager.get_current_session()
        current_session_id = current_session.id if current_session else None
        
        # Create tab buttons
        for session_info in sessions:
            is_current = session_info["id"] == current_session_id
            
            # Create tab button
            tab_btn = ctk.CTkButton(
                self.tabs_container,
                text=session_info["name"][:15] + ("..." if len(session_info["name"]) > 15 else ""),
                width=120,
                height=30,
                command=lambda sid=session_info["id"]: self.switch_to_tab(sid),
                font=ctk.CTkFont(size=10, weight="bold" if is_current else "normal"),
                fg_color="#0078d4" if is_current else "#2b2b2b",
                hover_color="#106ebe" if is_current else "#404040"
            )
            tab_btn.pack(side="left", padx=2, pady=2)
            
            # Add message count indicator
            if session_info["message_count"] > 0:
                count_label = ctk.CTkLabel(
                    tab_btn,
                    text=f"({session_info['message_count']})",
                    font=ctk.CTkFont(size=8),
                    text_color="#cccccc"
                )
                count_label.place(relx=0.9, rely=0.1, anchor="ne")
    
    def create_new_chat_tab(self):
        """Create a new chat tab/session"""
        # Save current session before switching
        self.save_current_session()
        
        # Create new session
        session_id = self.chat_history_manager.create_new_session()
        
        # Clear current conversation
        self.conversation_history = []
        self.message_id_counter = 0
        
        # Refresh UI
        self.refresh_chat_tabs()
        self.refresh_chat_display()
        
        # Add welcome message to new session
        current_session = self.chat_history_manager.get_current_session()
        if current_session:
            self.add_message("System", f"✨ New chat session '{current_session.name}' created!", is_user=False)
    
    def switch_to_tab(self, session_id):
        """Switch to a specific chat tab/session"""
        # Save current session before switching
        self.save_current_session()
        
        # Switch to new session
        if self.chat_history_manager.switch_session(session_id):
            # Load conversation history for this session
            self.conversation_history = self.chat_history_manager.load_session_history(session_id)
            
            # Update message counter
            if self.conversation_history:
                max_id = max((msg.get("id", 0) for msg in self.conversation_history), default=0)
                self.message_id_counter = max_id
            else:
                self.message_id_counter = 0
            
            # Refresh UI
            self.refresh_chat_tabs()
            self.refresh_chat_display()
            
            print(f"[DEBUG] Switched to session: {session_id}")
    
    def rename_current_tab(self):
        """Rename the current chat tab"""
        current_session = self.chat_history_manager.get_current_session()
        if not current_session:
            return
        
        # Create rename dialog
        rename_window = ctk.CTkToplevel(self.root)
        rename_window.title("Rename Chat")
        rename_window.geometry("400x150")
        rename_window.transient(self.root)
        rename_window.grab_set()
        
        # Center the window
        rename_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))
        
        # Rename input
        ctk.CTkLabel(rename_window, text="Enter new name:", font=ctk.CTkFont(size=14)).pack(pady=10)
        
        name_entry = ctk.CTkEntry(rename_window, width=300, placeholder_text="Chat name")
        name_entry.pack(pady=10)
        name_entry.insert(0, current_session.name)
        name_entry.select_range(0, "end")
        
        # Buttons
        button_frame = ctk.CTkFrame(rename_window)
        button_frame.pack(pady=10)
        
        def save_rename():
            new_name = name_entry.get().strip()
            if new_name and new_name != current_session.name:
                self.chat_history_manager.rename_session(current_session.id, new_name)
                self.refresh_chat_tabs()
            rename_window.destroy()
        
        def cancel_rename():
            rename_window.destroy()
        
        ctk.CTkButton(button_frame, text="Save", command=save_rename).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Cancel", command=cancel_rename).pack(side="left", padx=5)
        
        name_entry.focus()
        name_entry.bind("<Return>", lambda e: save_rename())
    
    def delete_current_tab(self):
        """Delete the current chat tab"""
        current_session = self.chat_history_manager.get_current_session()
        if not current_session:
            return
        
        # Confirm deletion
        result = tk.messagebox.askyesno(
            "Delete Chat", 
            f"Are you sure you want to delete the chat '{current_session.name}'?\n\nThis action cannot be undone."
        )
        
        if result:
            session_id = current_session.id
            
            # Delete the session
            self.chat_history_manager.delete_session(session_id)
            
            # Load the new current session
            new_current = self.chat_history_manager.get_current_session()
            if new_current:
                self.conversation_history = self.chat_history_manager.load_session_history(new_current.id)
                # Update message counter
                if self.conversation_history:
                    max_id = max((msg.get("id", 0) for msg in self.conversation_history), default=0)
                    self.message_id_counter = max_id
                else:
                    self.message_id_counter = 0
            else:
                self.conversation_history = []
                self.message_id_counter = 0
            
            # Refresh UI
            self.refresh_chat_tabs()
            self.refresh_chat_display()
    
    def save_current_session(self):
        """Save the current conversation to the active session"""
        if self.conversation_history:
            self.chat_history_manager.update_current_session_history(self.conversation_history)
    
    def setup_text_formatting(self):
        """Setup comprehensive text formatting tags for word processor-like display"""
        # Get the underlying tkinter text widget
        text_widget = self.chat_display._textbox
        
        # Use the configuration system for font settings
        base_size = self.ui_config.get_font_size()
        font_family = self.ui_config.get_font_family()
        code_family = self.ui_config.get_font_family("code")
        
        # Configure fonts with CONSISTENT sizing from config
        normal_font = ctk.CTkFont(size=base_size, family=font_family)
        bold_font = ctk.CTkFont(size=base_size, weight="bold", family=font_family)
        italic_font = ctk.CTkFont(size=base_size, slant="italic", family=font_family)
        bold_italic_font = ctk.CTkFont(size=base_size, weight="bold", slant="italic", family=font_family)
        
        # Code fonts - same size as regular text
        code_font = ctk.CTkFont(family=code_family, size=base_size)
        code_block_font = ctk.CTkFont(family=code_family, size=base_size)
        code_header_font = ctk.CTkFont(family=code_family, size=base_size, weight="bold")
        
        # Headers - use config-based sizing
        h1_font = ctk.CTkFont(size=self.ui_config.get_font_size("h1"), weight="bold", family=font_family)
        h2_font = ctk.CTkFont(size=self.ui_config.get_font_size("h2"), weight="bold", family=font_family)
        h3_font = ctk.CTkFont(size=self.ui_config.get_font_size("h3"), weight="bold", family=font_family)
        
        # Label fonts - same size as base text but bold
        label_font = ctk.CTkFont(size=base_size, weight="bold", family=font_family)
        
        # Emphasis fonts - same base size
        strong_font = ctk.CTkFont(size=base_size, weight="bold", family=font_family)
        emphasis_font = ctk.CTkFont(size=base_size, slant="italic", family=font_family)
        
        # Configure text tags with CONSISTENT sizing
        text_widget.tag_configure("normal", font=normal_font)
        text_widget.tag_configure("bold", font=bold_font)
        text_widget.tag_configure("italic", font=italic_font)
        text_widget.tag_configure("bold_italic", font=bold_italic_font)
        
        # Set the default font for the entire text widget
        text_widget.configure(font=normal_font)
        
        # Get colors from config
        code_bg = self.ui_config.get_color("code_bg")
        code_fg = self.ui_config.get_color("code_fg")
        
        # Inline code with same base size
        text_widget.tag_configure("code", 
                                font=code_font, 
                                background="#2d2d30", 
                                foreground="#dcdcdc", 
                                relief="solid", 
                                borderwidth=1,
                                lmargin1=2, lmargin2=2,
                                spacing1=2, spacing3=2)
        
        # Code blocks with same base size
        text_widget.tag_configure("code_block", 
                                font=code_block_font, 
                                background=code_bg, 
                                foreground=code_fg, 
                                lmargin1=25, lmargin2=25, rmargin=25,
                                spacing1=8, spacing3=8,
                                relief="solid", borderwidth=1,
                                wrap="none")
        
        text_widget.tag_configure("code_block_header", 
                                font=code_header_font, 
                                background="#007acc", 
                                foreground="#ffffff", 
                                lmargin1=20, lmargin2=20, rmargin=20,
                                spacing1=5, spacing3=2)
        
        # Headers - only these should be larger
        text_widget.tag_configure("h1", font=h1_font, spacing1=10, spacing3=5)
        text_widget.tag_configure("h2", font=h2_font, spacing1=8, spacing3=4)
        text_widget.tag_configure("h3", font=h3_font, spacing1=6, spacing3=3)
        
        # Lists - same base size
        text_widget.tag_configure("bullet", font=normal_font, lmargin1=20, lmargin2=35)
        text_widget.tag_configure("number", font=normal_font, lmargin1=20, lmargin2=35)
        
        # Quotes - same base size with styling
        text_widget.tag_configure("quote", 
                                font=normal_font,
                                background="#f6f8fa", 
                                foreground="#24292f",
                                lmargin1=15, lmargin2=15, rmargin=15,
                                spacing1=5, spacing3=5,
                                borderwidth=1, relief="solid")
        
        # Sender labels - same base size as body text with config colors
        primary_color = self.ui_config.get_color("primary")
        error_color = self.ui_config.get_color("error")
        warning_color = self.ui_config.get_color("warning")
        
        text_widget.tag_configure("user_label", font=label_font, foreground=primary_color)
        text_widget.tag_configure("ai_label", font=label_font, foreground=error_color)
        text_widget.tag_configure("system_label", font=label_font, foreground=warning_color)
        
        # Links and emphasis - same base size
        text_widget.tag_configure("link", font=normal_font, foreground=primary_color, underline=True)
        text_widget.tag_configure("strong", font=strong_font, foreground="#2c3e50")
        text_widget.tag_configure("emphasis", font=emphasis_font, foreground="#34495e")
        
        # Table formatting - same base size with dark theme styling
        table_font = ctk.CTkFont(family=code_family, size=base_size)
        table_header_font = ctk.CTkFont(family=code_family, size=base_size, weight="bold")
        
        text_widget.tag_configure("table_border", 
                                font=table_font, 
                                foreground="#ffffff")
        text_widget.tag_configure("table_header", 
                                font=table_header_font, 
                                foreground="#ffffff",
                                background="#404040")
        text_widget.tag_configure("table_data", 
                                font=table_font, 
                                foreground="#ffffff")
        
        # Message action buttons styling
        action_font = ctk.CTkFont(size=base_size-2, family=font_family)
        text_widget.tag_configure("message_actions", 
                                font=action_font, 
                                foreground="#888888",
                                underline=True)
        
        # Configure message action hover effects
        text_widget.tag_bind("message_actions", "<Enter>", lambda e: text_widget.configure(cursor="hand2"))
        text_widget.tag_bind("message_actions", "<Leave>", lambda e: text_widget.configure(cursor=""))
    
    def change_font_scale(self, value):
        """Change the font scale percentage and update all text formatting"""
        # Update the configuration with new scale
        scale_percentage = int(value)
        self.ui_config.set_font_scale(scale_percentage)
        
        # Update the font size label
        self.font_size_label.configure(text=f"{scale_percentage}%")
        
        # Update input field font (now using textbox)
        self.input_entry.configure(font=ctk.CTkFont(size=self.ui_config.get_font_size("input")))
        
        # Update chat display base font
        self.chat_display.configure(font=ctk.CTkFont(
            size=self.ui_config.get_font_size(), 
            family=self.ui_config.get_font_family()
        ))
        
        # Recreate all text formatting with new scale
        self.setup_text_formatting()
        
        # Refresh the chat display to apply new formatting
        self.refresh_chat_display()
    
    def on_input_focus_in(self, event=None):
        """Handle input field focus in - remove placeholder"""
        current_text = self.input_entry.get("1.0", "end-1c")
        if current_text == self.input_placeholder:
            self.input_entry.delete("1.0", "end")
            self.input_entry.configure(text_color="white")  # Normal text color
    
    def parse_and_format_text(self, text: str, sender: str):
        """Parse text and add comprehensive formatting tags including tables"""
        import re
        
        # Get the underlying tkinter text widget
        text_widget = self.chat_display._textbox
        
        # Split text into lines to handle different types of content
        lines = text.split('\n')
        in_code_block = False
        code_language = ""
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Check for code block start/end
            if line.strip().startswith('```'):
                if not in_code_block:
                    # Starting code block
                    in_code_block = True
                    code_language = line.strip()[3:].strip() or "code"
                    
                    # Add code block header
                    if code_language:
                        text_widget.insert("end", f" {code_language.upper()} ", "code_block_header")
                        text_widget.insert("end", "\n")
                else:
                    # Ending code block
                    in_code_block = False
                    text_widget.insert("end", "\n")
                i += 1
                continue
            
            if in_code_block:
                # Inside code block - add with code formatting
                text_widget.insert("end", line + "\n", "code_block")
                i += 1
                continue
            
            # Check for table (outside code blocks)
            if '|' in line and line.strip().startswith('|') and line.strip().endswith('|'):
                # Potential table - collect all table rows
                table_rows = []
                table_start = i
                
                while i < len(lines) and '|' in lines[i] and lines[i].strip().startswith('|'):
                    table_rows.append(lines[i])
                    i += 1
                
                # Parse and display table if we have enough rows
                if len(table_rows) >= 2:
                    self.render_table(table_rows)
                    continue
                else:
                    # Not a valid table, reset and process as normal
                    i = table_start
            
            # Parse line for different content types
            stripped_line = line.strip()
            
            # Headers
            if stripped_line.startswith('# '):
                text_widget.insert("end", stripped_line[2:] + "\n", "h1")
            elif stripped_line.startswith('## '):
                text_widget.insert("end", stripped_line[3:] + "\n", "h2")
            elif stripped_line.startswith('### '):
                text_widget.insert("end", stripped_line[4:] + "\n", "h3")
            # Bullet points
            elif stripped_line.startswith('- ') or stripped_line.startswith('• '):
                bullet_text = stripped_line[2:]
                text_widget.insert("end", "• ", "bullet")
                self.parse_inline_formatting(bullet_text)
                text_widget.insert("end", "\n")
            # Numbered lists
            elif re.match(r'^\d+\.\s', stripped_line):
                self.parse_inline_formatting(stripped_line)
                text_widget.insert("end", "\n", "number")
            # Block quotes
            elif stripped_line.startswith('> '):
                quote_text = stripped_line[2:]
                self.parse_inline_formatting(quote_text, base_tag="quote")
                text_widget.insert("end", "\n")
            # Empty lines - preserve spacing
            elif not stripped_line:
                text_widget.insert("end", "\n", "normal")
            # Regular text with inline formatting
            else:
                self.parse_inline_formatting(line)
                # Only add newline if not the last line or if we're not already at end
                if i < len(lines) - 1:
                    text_widget.insert("end", "\n")
            
            i += 1
    
    def render_table(self, table_rows):
        """Render a markdown table with proper formatting"""
        import re
        text_widget = self.chat_display._textbox
        
        # Parse table data
        table_data = []
        for row in table_rows:
            # Skip separator rows (contain only |, -, :, spaces)
            if re.match(r'^[\|\-\:\s]+$', row.strip()):
                continue
            
            # Split by | and clean up
            cells = [cell.strip() for cell in row.split('|')[1:-1]]
            if cells:  # Only add non-empty rows
                table_data.append(cells)
        
        if not table_data:
            return
        
        # Calculate column widths
        col_widths = []
        for i in range(len(table_data[0])):
            max_width = max(len(str(row[i]) if i < len(row) else "") for row in table_data)
            col_widths.append(max(max_width, 8))  # Minimum width of 8
        
        # Add table header
        text_widget.insert("end", "┌", "table_border")
        for i, width in enumerate(col_widths):
            text_widget.insert("end", "─" * (width + 2), "table_border")
            if i < len(col_widths) - 1:
                text_widget.insert("end", "┬", "table_border")
        text_widget.insert("end", "┐\n", "table_border")
        
        # Add table content
        for row_idx, row in enumerate(table_data):
            text_widget.insert("end", "│", "table_border")
            
            for i, cell in enumerate(row):
                cell_content = str(cell) if i < len(row) else ""
                padding = col_widths[i] - len(cell_content)
                
                text_widget.insert("end", " ", "table_border")
                if row_idx == 0:
                    # Header row
                    text_widget.insert("end", cell_content + " " * padding, "table_header")
                else:
                    # Data row
                    text_widget.insert("end", cell_content + " " * padding, "table_data")
                text_widget.insert("end", " │", "table_border")
            
            text_widget.insert("end", "\n")
            
            # Add separator after header
            if row_idx == 0 and len(table_data) > 1:
                text_widget.insert("end", "├", "table_border")
                for i, width in enumerate(col_widths):
                    text_widget.insert("end", "─" * (width + 2), "table_border")
                    if i < len(col_widths) - 1:
                        text_widget.insert("end", "┼", "table_border")
                text_widget.insert("end", "┤\n", "table_border")
        
        # Add table footer
        text_widget.insert("end", "└", "table_border")
        for i, width in enumerate(col_widths):
            text_widget.insert("end", "─" * (width + 2), "table_border")
            if i < len(col_widths) - 1:
                text_widget.insert("end", "┴", "table_border")
        text_widget.insert("end", "┘\n", "table_border")
    
    def parse_inline_formatting(self, text: str, base_tag: str = "normal"):
        """Parse and insert text with comprehensive inline formatting"""
        import re
        
        text_widget = self.chat_display._textbox
        
        # Enhanced patterns for comprehensive formatting
        patterns = [
            (r'\*\*\*(.*?)\*\*\*', 'bold_italic'),    # ***bold italic***
            (r'\*\*(.*?)\*\*', 'bold'),               # **bold**
            (r'\*(.*?)\*', 'italic'),                 # *italic*
            (r'`(.*?)`', 'code'),                     # `code`
            (r'__(.*?)__', 'strong'),                 # __strong__
            (r'_(.*?)_', 'emphasis'),                 # _emphasis_
        ]
        
        pos = 0
        while pos < len(text):
            # Find the next formatting match
            earliest_match = None
            earliest_pos = len(text)
            earliest_pattern = None
            
            for pattern, tag in patterns:
                match = re.search(pattern, text[pos:])
                if match and match.start() + pos < earliest_pos:
                    earliest_match = match
                    earliest_pos = match.start() + pos
                    earliest_pattern = (pattern, tag)
            
            if earliest_match is None:
                # No more formatting, insert rest with proper font tag
                remaining_text = text[pos:]
                if remaining_text:
                    if base_tag != "normal":
                        text_widget.insert("end", remaining_text, base_tag)
                    else:
                        text_widget.insert("end", remaining_text, "normal")  # Always use normal tag
                break
            
            # Insert text before the match with proper font tag
            if earliest_pos > pos:
                before_text = text[pos:earliest_pos]
                if base_tag != "normal":
                    text_widget.insert("end", before_text, base_tag)
                else:
                    text_widget.insert("end", before_text, "normal")  # Always use normal tag
            
            # Insert the formatted text
            pattern, tag = earliest_pattern
            formatted_text = earliest_match.group(1)
            
            # Combine tags if we have a base tag
            if base_tag != "normal":
                # For complex tag combinations, we'll use the formatting tag primarily
                text_widget.insert("end", formatted_text, tag)
            else:
                text_widget.insert("end", formatted_text, tag)
            
            # Move position past the entire match
            pos = earliest_pos + earliest_match.end()
        
    def load_orchestrator(self):
        """Load the AI orchestrator in a separate thread"""
        def load():
            try:
                print("[DEBUG] Starting orchestrator loading in thread...")
                
                # Give main loop time to fully initialize
                import time
                time.sleep(0.1)
                
                # Import and initialize in thread
                import sys
                from pathlib import Path
                project_root = Path(__file__).parent.parent
                src_path = project_root
                if str(src_path) not in sys.path:
                    sys.path.insert(0, str(src_path))
                
                from core.smart_orchestrator import SmartAIOrchestrator
                print("[DEBUG] Creating smart orchestrator...")
                orchestrator = SmartAIOrchestrator()
                print("[DEBUG] Smart orchestrator created successfully")
                
                # Set the orchestrator in main thread with error handling
                def set_orchestrator():
                    try:
                        self.orchestrator = orchestrator
                        # Update character name from orchestrator
                        if hasattr(orchestrator, 'character_manager') and orchestrator.character_manager.current_character:
                            self.character_name = orchestrator.character_manager.current_character.name
                        self.update_status()
                        print("[DEBUG] Orchestrator set and status updated")
                        
                        # Remove the loading message
                        if self.conversation_history and self.conversation_history[-1]['sender'] == 'System' and 'Loading' in self.conversation_history[-1]['message']:
                            self.conversation_history.pop()
                            self.refresh_chat_display()
                        
                        # Add system status message first
                        self.add_message("System", f"✅ {self.character_name} is ready! All tools loaded successfully.", is_user=False)
                        
                        # Then add the character's greeting
                        if hasattr(orchestrator, 'character_manager') and orchestrator.character_manager.current_character:
                            greeting = orchestrator.character_manager.current_character.greeting
                            self.add_message(self.character_name, greeting, is_user=False)
                        
                    except Exception as e:
                        print(f"[DEBUG] Error setting orchestrator: {e}")
                        # Remove loading message even on error
                        if self.conversation_history and self.conversation_history[-1]['sender'] == 'System' and 'Loading' in self.conversation_history[-1]['message']:
                            self.conversation_history.pop()
                            self.refresh_chat_display()
                        self.add_message("System", f"⚠️ AI loaded but status update failed: {e}", is_user=False)
                
                # Schedule the GUI update with a small delay to ensure main loop is ready
                self.root.after(100, set_orchestrator)
                
            except Exception as e:
                print(f"[DEBUG] Error in orchestrator loading: {e}")
                import traceback
                traceback.print_exc()
                
                error_msg = str(e)  # Capture the error message
                
                # Schedule error message with delay
                def show_error():
                    try:
                        # Remove loading message
                        if self.conversation_history and self.conversation_history[-1]['sender'] == 'System' and 'Loading' in self.conversation_history[-1]['message']:
                            self.conversation_history.pop()
                            self.refresh_chat_display()
                        
                        self.add_message("System", f"❌ Error loading AI: {error_msg}", is_user=False)
                        # Add a fallback greeting from the default character name
                        self.add_message(self.character_name, "I apologize, but I'm having trouble starting up properly. Please check the system status and try again.", is_user=False)
                    except Exception as e2:
                        print(f"[DEBUG] Error showing error message: {e2}")
                
                self.root.after(100, show_error)
        
        print("[DEBUG] Starting orchestrator loading thread...")
        # Add small delay before starting the thread to ensure GUI is fully initialized
        self.root.after(50, lambda: threading.Thread(target=load, daemon=True).start())
    
    def update_status(self):
        """Update the status display"""
        try:
            print("[DEBUG] update_status called")
            if self.orchestrator:
                print("[DEBUG] Orchestrator exists, updating status")
                
                # Update character name if it has changed
                if hasattr(self.orchestrator, 'character_manager') and self.orchestrator.character_manager.current_character:
                    new_character_name = self.orchestrator.character_manager.current_character.name
                    if new_character_name != self.character_name:
                        self.character_name = new_character_name
                        print(f"[DEBUG] Character name updated to: {self.character_name}")
                
                # Update brain status with type information
                if self.orchestrator.brain:
                    brain_type = getattr(self.orchestrator, 'brain_type', 'unknown')
                    brain_emoji = "🟢" if brain_type == "gemini" else "🔵" if brain_type == "koboldcpp" else "🧠"
                    brain_status = f"{brain_emoji} Brain: ✅ {brain_type.title()}"
                else:
                    brain_status = "🔴 Brain: ❌ Disconnected"
                self.brain_status.configure(text=brain_status)
                
                # Update tools status
                tool_count = len(self.orchestrator.tools)
                self.tools_status.configure(text=f"⚙️ Tools: ✅ {tool_count} loaded")
                
                # Update character status
                if hasattr(self.orchestrator, 'character_manager') and self.orchestrator.character_manager.current_character:
                    char_name = self.orchestrator.character_manager.current_character.name
                    self.character_status.configure(text=f"🎭 Character: ✅ {char_name}")
                else:
                    self.character_status.configure(text="🎭 Character: ❌ None")
                
                print("[DEBUG] Status updated successfully")
            else:
                print("[DEBUG] No orchestrator to update status for")
        except Exception as e:
            print(f"[DEBUG] Error in update_status: {e}")
            import traceback
            traceback.print_exc()
    
    def add_message(self, sender: str, message: str, is_user: bool = True, message_id: int = None):
        """Add a message to the chat display with formatting and interactive features"""
        try:
            print(f"[DEBUG] add_message called: sender={sender}, is_user={is_user}")
            
            # Generate unique message ID if not provided
            if message_id is None:
                self.message_id_counter += 1
                message_id = self.message_id_counter
            
            self.chat_display.configure(state="normal")
            print(f"[DEBUG] Chat display state set to normal")
            
            # Add timestamp
            timestamp = datetime.now().strftime("%H:%M")
            print(f"[DEBUG] Timestamp created: {timestamp}")
            
            # Get the underlying tkinter text widget for formatted text
            text_widget = self.chat_display._textbox
            
            # Mark the start position for this message
            start_pos = text_widget.index("end")
            
            # Add sender prefix with appropriate formatting
            if is_user:
                prefix = f"[{timestamp}] You: "
                text_widget.insert("end", prefix, "user_label")
            elif sender == "System":
                prefix = f"[{timestamp}] {sender}: "
                text_widget.insert("end", prefix, "system_label")
            else:
                prefix = f"[{timestamp}] {sender}: "
                text_widget.insert("end", prefix, "ai_label")
            
            print(f"[DEBUG] Prefix inserted")
            
            # Parse and format the message content
            self.parse_and_format_text(message, sender)
            
            # Add action buttons for user messages and AI responses
            if is_user and sender != "System":
                self.add_message_actions(text_widget, message_id, "user")
            elif not is_user and sender != "System":
                self.add_message_actions(text_widget, message_id, "ai")
            
            text_widget.insert("end", "\n\n")
            
            # Mark the end position for this message
            end_pos = text_widget.index("end")
            
            # Create a tag for this message for easy identification
            message_tag = f"message_{message_id}"
            text_widget.tag_add(message_tag, start_pos, end_pos)
            
            # Bind right-click context menu to the message
            text_widget.tag_bind(message_tag, "<Button-3>", lambda e: self.show_message_context_menu(e, message_id, is_user, sender))
            
            print(f"[DEBUG] Message content inserted with formatting")
            
            self.chat_display.configure(state="disabled")
            print(f"[DEBUG] Chat display state set to disabled")
            
            self.chat_display.see("end")
            print(f"[DEBUG] Scrolled to end")
            
            # Store in history with message ID
            self.conversation_history.append({
                "id": message_id,
                "sender": sender,
                "message": message,
                "is_user": is_user,
                "timestamp": timestamp
            })
            print(f"[DEBUG] Message stored in history with ID: {message_id}")
            
            # Auto-save to current session
            self.save_current_session()
            
            # Refresh tabs to show updated message count
            self.refresh_chat_tabs()
            
        except Exception as e:
            print(f"[DEBUG] Error in add_message: {e}")
            import traceback
            traceback.print_exc()
    
    def add_message_actions(self, text_widget, message_id, message_type):
        """Add action buttons (edit, delete, regenerate) to a message"""
        text_widget.insert("end", "\n")
        
        if message_type == "user":
            # User message actions: Edit, Delete
            actions_text = "  [Edit] [Delete]"
            text_widget.insert("end", actions_text, "message_actions")
        elif message_type == "ai":
            # AI message actions: Regenerate, Delete
            actions_text = "  [Regenerate] [Delete]"
            text_widget.insert("end", actions_text, "message_actions")
        
        # Make actions clickable
        start_pos = text_widget.index("end-2c linestart")
        end_pos = text_widget.index("end-1c")
        action_tag = f"actions_{message_id}"
        text_widget.tag_add(action_tag, start_pos, end_pos)
        text_widget.tag_bind(action_tag, "<Button-1>", lambda e: self.handle_message_action(e, message_id, message_type))
    
    def show_message_context_menu(self, event, message_id, is_user, sender):
        """Show context menu for message actions"""
        self.selected_message_id = message_id
        
        # Create context menu
        context_menu = tk.Menu(self.root, tearoff=0)
        
        if is_user and sender != "System":
            context_menu.add_command(label="Edit Message", command=lambda: self.edit_message(message_id))
            context_menu.add_command(label="Delete Message", command=lambda: self.delete_message(message_id))
        elif not is_user and sender != "System":
            context_menu.add_command(label="Regenerate Response", command=lambda: self.regenerate_message(message_id))
            context_menu.add_command(label="Delete Message", command=lambda: self.delete_message(message_id))
        
        # Show context menu
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def handle_message_action(self, event, message_id, message_type):
        """Handle clicks on message action buttons"""
        # Get click position and determine which action was clicked
        text_widget = self.chat_display._textbox
        click_index = text_widget.index(f"@{event.x},{event.y}")
        line_text = text_widget.get(f"{click_index} linestart", f"{click_index} lineend")
        
        if "[Edit]" in line_text and message_type == "user":
            self.edit_message(message_id)
        elif "[Delete]" in line_text:
            self.delete_message(message_id)
        elif "[Regenerate]" in line_text and message_type == "ai":
            self.regenerate_message(message_id)
    
    def edit_message(self, message_id):
        """Edit a user message"""
        # Find the message in history
        message_data = None
        for msg in self.conversation_history:
            if msg.get("id") == message_id:
                message_data = msg
                break
        
        if not message_data or not message_data["is_user"]:
            return
        
        # Create edit dialog
        edit_window = ctk.CTkToplevel(self.root)
        edit_window.title("Edit Message")
        edit_window.geometry("500x300")
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Center the window
        edit_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Edit text area
        ctk.CTkLabel(edit_window, text="Edit your message:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        edit_text = ctk.CTkTextbox(edit_window, height=150, wrap="word")
        edit_text.pack(fill="both", expand=True, padx=20, pady=10)
        edit_text.insert("1.0", message_data["message"])
        
        # Buttons
        button_frame = ctk.CTkFrame(edit_window)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        def save_edit():
            new_message = edit_text.get("1.0", "end-1c").strip()
            if new_message:
                # Update message in history
                message_data["message"] = new_message
                message_data["timestamp"] = datetime.now().strftime("%H:%M")
                
                # Refresh display
                self.refresh_chat_display()
                
                # If this was the last user message, we might want to regenerate AI response
                if message_id == self.conversation_history[-1].get("id") or (
                    len(self.conversation_history) > 1 and 
                    message_id == self.conversation_history[-2].get("id") and 
                    not self.conversation_history[-1]["is_user"]
                ):
                    # Ask if user wants to regenerate AI response
                    self.ask_regenerate_after_edit(message_id)
            
            edit_window.destroy()
        
        def cancel_edit():
            edit_window.destroy()
        
        ctk.CTkButton(button_frame, text="Save", command=save_edit).pack(side="right", padx=5)
        ctk.CTkButton(button_frame, text="Cancel", command=cancel_edit).pack(side="right", padx=5)
        
        edit_text.focus()
    
    def delete_message(self, message_id):
        """Delete a message and optionally following AI response"""
        # Find message index
        message_index = None
        for i, msg in enumerate(self.conversation_history):
            if msg.get("id") == message_id:
                message_index = i
                break
        
        if message_index is None:
            return
        
        message_data = self.conversation_history[message_index]
        
        # Confirm deletion
        result = tk.messagebox.askyesno(
            "Delete Message", 
            f"Are you sure you want to delete this message from {message_data['sender']}?"
        )
        
        if result:
            # Remove from history
            self.conversation_history.pop(message_index)
            
            # If this was a user message and there's an AI response after it, ask if they want to delete that too
            if (message_data["is_user"] and 
                message_index < len(self.conversation_history) and 
                not self.conversation_history[message_index]["is_user"]):
                
                ai_delete_result = tk.messagebox.askyesno(
                    "Delete AI Response", 
                    "Do you also want to delete the AI response that followed this message?"
                )
                
                if ai_delete_result:
                    self.conversation_history.pop(message_index)
            
            # Refresh display
            self.refresh_chat_display()
    
    def regenerate_message(self, message_id):
        """Regenerate an AI response"""
        # Find the message and the user message that preceded it
        message_index = None
        for i, msg in enumerate(self.conversation_history):
            if msg.get("id") == message_id:
                message_index = i
                break
        
        if message_index is None or message_index == 0:
            return
        
        # Find the user message that this was responding to
        user_message = None
        for i in range(message_index - 1, -1, -1):
            if self.conversation_history[i]["is_user"]:
                user_message = self.conversation_history[i]["message"]
                break
        
        if user_message is None:
            tk.messagebox.showwarning("Cannot Regenerate", "Could not find the original user message to regenerate response for.")
            return
        
        # Remove the AI message from history
        self.conversation_history.pop(message_index)
        
        # Refresh display to remove the old response
        self.refresh_chat_display()
        
        # Regenerate response
        threading.Thread(target=self.process_message, args=(user_message,), daemon=True).start()
    
    def ask_regenerate_after_edit(self, edited_message_id):
        """Ask user if they want to regenerate AI response after editing a message"""
        result = tk.messagebox.askyesno(
            "Regenerate Response", 
            "You edited a message that has an AI response. Would you like to regenerate the AI response based on your edited message?"
        )
        
        if result:
            # Find and remove any AI responses after the edited message
            edited_index = None
            for i, msg in enumerate(self.conversation_history):
                if msg.get("id") == edited_message_id:
                    edited_index = i
                    break
            
            if edited_index is not None:
                # Remove AI responses after this message
                self.conversation_history = self.conversation_history[:edited_index + 1]
                self.refresh_chat_display()
                
                # Regenerate response
                user_message = self.conversation_history[edited_index]["message"]
                threading.Thread(target=self.process_message, args=(user_message,), daemon=True).start()
        """Handle input field focus in - remove placeholder"""
        current_text = self.input_entry.get("1.0", "end-1c")
        if current_text == self.input_placeholder:
            self.input_entry.delete("1.0", "end")
            self.input_entry.configure(text_color="white")  # Normal text color
    
    def on_input_focus_out(self, event=None):
        """Handle input field focus out - add placeholder if empty"""
        current_text = self.input_entry.get("1.0", "end-1c").strip()
        if not current_text:
            self.input_entry.insert("1.0", self.input_placeholder)
            self.input_entry.configure(text_color="gray60")  # Placeholder color
    
    def insert_newline(self, event=None):
        """Insert a new line when Shift+Enter is pressed"""
        self.input_entry.insert("insert", "\n")
        return "break"  # Prevent default behavior
    
    def send_message(self, event=None):
        """Send a message to the AI"""
        if self.is_processing:
            return "break" if event else None
            
        # Get text from textbox instead of entry
        message = self.input_entry.get("1.0", "end-1c").strip()
        
        # Don't send if it's just the placeholder text or empty
        if not message or message == self.input_placeholder:
            return "break" if event else None
        
        # Clear input
        self.input_entry.delete("1.0", "end")
        self.input_entry.configure(text_color="white")  # Reset to normal color
        
        # Add user message
        self.add_message("You", message, is_user=True)
        
        # Process in background
        threading.Thread(target=self.process_message, args=(message,), daemon=True).start()
        
        # Return "break" to prevent default Enter behavior when called from keyboard event
        return "break" if event else None
    
    def process_message(self, message: str):
        """Process the message using the AI orchestrator"""
        self.is_processing = True
        
        try:
            # Show processing indicator
            self.root.after(0, lambda: self.add_message(self.character_name, "Thinking...", is_user=False))
            
            if self.orchestrator:
                # Convert conversation history to the format expected by the AI
                # Include ALL previous messages for proper context
                chat_history = []
                for entry in self.conversation_history:
                    # Skip system messages and current thinking message
                    if (entry.get('sender') == 'System' or 
                        entry.get('message', '').startswith('Thinking...') or
                        entry.get('message', '').startswith('🔄 Loading')):
                        continue
                    
                    if entry.get('is_user', False):
                        chat_history.append({
                            "role": "user", 
                            "content": entry.get('message', ''),
                            "timestamp": entry.get('timestamp', '')
                        })
                    else:
                        # AI/Assistant message - preserve full context including tool results
                        chat_history.append({
                            "role": "assistant", 
                            "content": entry.get('message', ''),
                            "sender": entry.get('sender', self.character_name),
                            "timestamp": entry.get('timestamp', '')
                        })
                
                # Add timeout handling for AI processing
                print(f"[DEBUG] Processing message with {len(chat_history)} context messages: {message[:50]}...")
                
                import signal
                import time
                
                def timeout_handler(signum, frame):
                    raise TimeoutError("AI processing timeout")
                
                # Set timeout for Windows (using threading timer as signal doesn't work well on Windows)
                import threading
                timeout_occurred = threading.Event()
                
                def timeout_func():
                    timeout_occurred.set()
                
                timer = threading.Timer(30.0, timeout_func)  # 30 second timeout
                timer.start()
                
                try:
                    # Process the message with conversation history using smart orchestrator
                    result = self.orchestrator.process_user_request(message, chat_history)
                    timer.cancel()  # Cancel timeout if successful
                    
                    if timeout_occurred.is_set():
                        raise TimeoutError("AI processing took too long")
                        
                    print(f"[DEBUG] AI processing completed successfully")
                    
                except TimeoutError:
                    print(f"[DEBUG] AI processing timed out")
                    result = {
                        "error": "Request timed out",
                        "response": "Sorry, I'm taking too long to respond. This might be because:\n• KoboldCPP server is not responding\n• Network connection is slow\n• The AI model is overloaded\n\nPlease try again or check your KoboldCPP server."
                    }
                except Exception as e:
                    print(f"[DEBUG] AI processing error: {e}")
                    result = {
                        "error": f"Processing error: {e}",
                        "response": f"Sorry, I encountered an error: {str(e)}\n\nPlease check that KoboldCPP is running and try again."
                    }
                finally:
                    timer.cancel()
                
                # Remove thinking message
                print(f"[DEBUG] Removing thinking message...")
                self.root.after(0, self.remove_last_message)
                
                # Add response
                print(f"[DEBUG] Preparing response message...")
                if 'error' in result:
                    response = f"❌ Error: {result['error']}"
                elif 'response' in result:
                    response = result['response']
                    
                    # Add AI reasoning if available (for tool usage)
                    if 'ai_reasoning' in result and result['ai_reasoning']:
                        response += f"\n\n💭 AI Reasoning: {result['ai_reasoning']}"
                    
                    # Add tool info if this was a tool usage
                    if result.get('tool_used') and not result.get('is_conversation', False):
                        tool_used = result['tool_used'].replace('_', ' ').title()
                        response += f"\n\n🔧 Used: {tool_used}"
                else:
                    response = "I processed your request, but didn't get a clear response."
                
                print(f"[DEBUG] Adding AI response to chat...")
                # Use a safer approach for GUI updates
                def add_response():
                    try:
                        self.add_message(self.character_name, response, is_user=False)
                        print(f"[DEBUG] AI response added successfully")
                    except Exception as e:
                        print(f"[DEBUG] Error adding response: {e}")
                        
                self.root.after(0, add_response)
            else:
                self.root.after(0, lambda: self.add_message(self.character_name, "❌ AI system not ready yet. Please wait for initialization.", is_user=False))
                
        except Exception as e:
            self.root.after(0, lambda: self.add_message(self.character_name, f"❌ Error processing request: {e}", is_user=False))
        
        finally:
            self.is_processing = False
    
    def remove_last_message(self):
        """Remove the last message (used to remove 'thinking' indicator)"""
        try:
            print(f"[DEBUG] remove_last_message called")
            if self.conversation_history:
                self.conversation_history.pop()
                print(f"[DEBUG] Removed last message from history")
                self.refresh_chat_display()
                print(f"[DEBUG] Chat display refreshed")
            else:
                print(f"[DEBUG] No messages to remove")
        except Exception as e:
            print(f"[DEBUG] Error in remove_last_message: {e}")
            import traceback
            traceback.print_exc()
    
    def refresh_chat_display(self):
        """Refresh the entire chat display with formatting"""
        try:
            print(f"[DEBUG] refresh_chat_display called")
            self.chat_display.configure(state="normal")
            print(f"[DEBUG] Chat display state set to normal for refresh")
            
            self.chat_display.delete("1.0", "end")
            print(f"[DEBUG] Chat display cleared")
            
            # Get the underlying tkinter text widget
            text_widget = self.chat_display._textbox
            
            for i, msg in enumerate(self.conversation_history):
                print(f"[DEBUG] Adding message {i+1}/{len(self.conversation_history)}")
                
                # Get message data
                message_id = msg.get("id", i)  # Use index as fallback if no ID
                timestamp = msg.get("timestamp", datetime.now().strftime("%H:%M"))
                sender = msg["sender"]
                message = msg["message"]
                is_user = msg["is_user"]
                
                # Mark the start position for this message
                start_pos = text_widget.index("end")
                
                # Add sender prefix with appropriate formatting
                if is_user:
                    prefix = f"[{timestamp}] You: "
                    text_widget.insert("end", prefix, "user_label")
                elif sender == "System":
                    prefix = f"[{timestamp}] {sender}: "
                    text_widget.insert("end", prefix, "system_label")
                else:
                    prefix = f"[{timestamp}] {sender}: "
                    text_widget.insert("end", prefix, "ai_label")
                
                # Parse and format the message content
                self.parse_and_format_text(message, sender)
                
                # Add action buttons for user messages and AI responses
                if is_user and sender != "System":
                    self.add_message_actions(text_widget, message_id, "user")
                elif not is_user and sender != "System":
                    self.add_message_actions(text_widget, message_id, "ai")
                
                text_widget.insert("end", "\n\n")
                
                # Mark the end position for this message
                end_pos = text_widget.index("end")
                
                # Create a tag for this message for easy identification
                message_tag = f"message_{message_id}"
                text_widget.tag_add(message_tag, start_pos, end_pos)
                
                # Bind right-click context menu to the message
                text_widget.tag_bind(message_tag, "<Button-3>", lambda e, mid=message_id, iu=is_user, s=sender: self.show_message_context_menu(e, mid, iu, s))
            
            print(f"[DEBUG] All messages re-added with formatting")
            self.chat_display.configure(state="disabled")
            self.chat_display.see("end")
            print(f"[DEBUG] Chat display state set to disabled after refresh")
            
        except Exception as e:
            print(f"[DEBUG] Error in refresh_chat_display: {e}")
            import traceback
            traceback.print_exc()
    
    def quick_screenshot(self):
        """Quick screenshot action"""
        self.input_entry.delete("1.0", "end")
        self.input_entry.insert("1.0", "Take a screenshot and tell me what you see")
        self.input_entry.configure(text_color="white")
        self.send_message()
    
    def quick_search(self):
        """Quick search action"""
        self.input_entry.delete("1.0", "end")
        self.input_entry.insert("1.0", "Search for ")
        self.input_entry.configure(text_color="white")
        self.input_entry.focus()
        # Position cursor at the end
        self.input_entry.mark_set("insert", "end")
    
    def clear_conversation(self):
        """Clear the current conversation"""
        result = tk.messagebox.askyesno(
            "Clear Chat", 
            "Are you sure you want to clear this conversation?\n\nThis will delete all messages in the current chat."
        )
        
        if result:
            self.conversation_history = []
            self.message_id_counter = 0
            self.chat_display.configure(state="normal")
            self.chat_display.delete("1.0", "end")
            self.chat_display.configure(state="disabled")
            
            # Save the cleared session
            self.save_current_session()
            self.refresh_chat_tabs()
            
            # Add a system message
            self.add_message("System", "Conversation cleared. How can I help you?", is_user=False)
    
    def show_format_help(self):
        """Show comprehensive formatting help message"""
        help_text = """# **Enhanced Text Formatting Guide**

## **Basic Formatting**
**Bold text**: `**bold**` → **bold**
*Italic text*: `*italic*` → *italic*
***Bold italic***: `***bold italic***` → ***bold italic***
__Strong emphasis__: `__strong__` → __strong__
_Light emphasis_: `_emphasis_` → _emphasis_

## **Code Formatting**
`Inline code`: `` `code` `` → `code`

**Code blocks with syntax highlighting**:
```python
def example_function():
    return "Hello, World!"
```

```javascript
function greetUser(name) {
    console.log("Hello, " + name + "!");
}
```

## **Document Structure**
# Large Header
## Medium Header  
### Small Header

**Lists**:
- Bullet point item
- Another bullet point
  - Sub-item (use spaces)

1. Numbered list item
2. Another numbered item

**Block quotes**:
> This is a quoted text that stands out
> Perfect for important information

## **AI Usage Tips**
✅ **Good examples**:
- "Explain **machine learning** with some `code examples`"
- "Create a ***comprehensive guide*** about Python"
- "Show me a ```python``` example of _data processing_"

The AI will automatically use these formatting styles in responses to make information clearer and more readable. You can also use them in your messages for better communication!

**Pro tip**: The AI understands when you want formatted responses and will structure information using headers, lists, code blocks, and emphasis for maximum clarity."""
        
        self.add_message("System", help_text, is_user=False)
    
    def show_font_settings(self):
        """Show font settings dialog"""
        # Create font settings window
        font_window = ctk.CTkToplevel(self.root)
        font_window.title("Font Settings")
        font_window.geometry("450x300")
        font_window.transient(self.root)
        font_window.grab_set()
        
        # Center the window
        font_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))
        
        # Title
        ctk.CTkLabel(font_window, text="Font Settings", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        
        # Font size section
        size_frame = ctk.CTkFrame(font_window)
        size_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(size_frame, text="Font Scale:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        # Current scale display
        current_scale = self.ui_config.get_font_scale()
        scale_var = tk.IntVar(value=current_scale)
        
        scale_label = ctk.CTkLabel(size_frame, text=f"Current: {current_scale}%", font=ctk.CTkFont(size=12))
        scale_label.pack(anchor="w", padx=10)
        
        # Scale slider
        min_scale, max_scale = self.ui_config.get_font_scale_range()
        scale_slider = ctk.CTkSlider(
            size_frame,
            from_=min_scale,
            to=max_scale,
            number_of_steps=(max_scale - min_scale) // 10,
            variable=scale_var,
            command=lambda v: scale_label.configure(text=f"Current: {int(v)}%")
        )
        scale_slider.pack(fill="x", padx=10, pady=5)
        
        # Preset buttons
        preset_frame = ctk.CTkFrame(size_frame)
        preset_frame.pack(fill="x", padx=10, pady=5)
        
        presets = [50, 75, 100, 125, 150, 200]
        for preset in presets:
            btn = ctk.CTkButton(
                preset_frame,
                text=f"{preset}%",
                width=60,
                height=30,
                command=lambda p=preset: (scale_slider.set(p), scale_label.configure(text=f"Current: {p}%")),
                font=ctk.CTkFont(size=10)
            )
            btn.pack(side="left", padx=2, pady=2)
        
        # Preview section
        preview_frame = ctk.CTkFrame(font_window)
        preview_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(preview_frame, text="Preview:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        preview_text = ctk.CTkTextbox(preview_frame, height=80, wrap="word")
        preview_text.pack(fill="both", expand=True, padx=10, pady=5)
        preview_text.insert("1.0", "This is a preview of how text will look with the selected font scale.\n\n**Bold text**, *italic text*, and `code text` will all scale proportionally.")
        
        def update_preview():
            new_scale = int(scale_slider.get())
            preview_size = int(14 * (new_scale / 100))
            preview_text.configure(font=ctk.CTkFont(size=preview_size))
        
        scale_slider.configure(command=lambda v: (scale_label.configure(text=f"Current: {int(v)}%"), update_preview()))
        update_preview()
        
        # Buttons
        button_frame = ctk.CTkFrame(font_window)
        button_frame.pack(fill="x", padx=20, pady=15)
        
        def apply_settings():
            new_scale = int(scale_slider.get())
            self.change_font_scale(new_scale)
            font_window.destroy()
        
        def reset_to_default():
            scale_slider.set(100)
            scale_label.configure(text="Current: 100%")
            update_preview()
        
        ctk.CTkButton(button_frame, text="Apply", command=apply_settings).pack(side="right", padx=5)
        ctk.CTkButton(button_frame, text="Cancel", command=font_window.destroy).pack(side="right", padx=5)
        ctk.CTkButton(button_frame, text="Reset to Default", command=reset_to_default).pack(side="left", padx=5)
    
    def show_help(self):
        """Show help dialog with application information"""
        help_window = ctk.CTkToplevel(self.root)
        help_window.title("AI Companion - Help")
        help_window.geometry("500x400")
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Center the window
        help_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))
        
        # Title
        ctk.CTkLabel(help_window, text="AI Companion - Help", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        
        # Help content in scrollable frame
        help_scroll = ctk.CTkScrollableFrame(help_window)
        help_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        help_content = """
🤖 AI Companion Help

📋 QUICK START:
• Type your message in the input field
• Press Ctrl+Enter or click Send to send
• Right-click messages for edit/delete options
• Use the + button to create new chat sessions

💬 CHAT SESSIONS:
• Switch between conversations using tabs
• Rename sessions with the Rename button
• Delete sessions with the Delete button
• Access session manager from File menu

✨ FORMATTING:
• **Bold text** - Use **text**
• *Italic text* - Use *text*
• `Code text` - Use `code`
• Headers - Use # ## ###
• Lists - Use - or 1. 2. 3.
• Code blocks - Use ```language

🔧 QUICK ACTIONS:
• Screenshot - Capture and analyze screen
• Web Search - Search the internet
• Clear Chat - Start fresh conversation
• Format Help - See formatting examples

⚙️ SETTINGS:
• Font Settings - Adjust text size (50%-300%)
• Always on Top - Keep window visible
• Minimize to Tray - Hide to system tray

🎯 MESSAGE ACTIONS:
• Edit - Modify your messages (right-click)
• Delete - Remove any message
• Regenerate - Get new AI response

💾 KEYBOARD SHORTCUTS:
• Ctrl+Enter - Send message
• Right-click - Context menu
• Tab navigation in multi-line input

🔍 TIPS:
• Chat history is automatically saved
• Sessions persist between app restarts
• Use formatting for better readability
• AI understands context across messages
        """
        
        ctk.CTkLabel(
            help_scroll, 
            text=help_content,
            font=ctk.CTkFont(size=12),
            anchor="w",
            justify="left"
        ).pack(fill="both", padx=10, pady=5)
        
        # Close button
        ctk.CTkButton(help_window, text="Close", command=help_window.destroy).pack(pady=15)
    
    def show_session_manager(self):
        """Show the chat session manager dialog"""
        # Create session manager window
        session_window = ctk.CTkToplevel(self.root)
        session_window.title("Chat Session Manager")
        session_window.geometry("600x400")
        session_window.transient(self.root)
        session_window.grab_set()
        
        # Center the window
        session_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Title
        ctk.CTkLabel(session_window, text="Chat Sessions", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        # Sessions list frame
        list_frame = ctk.CTkFrame(session_window)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create scrollable frame for sessions
        sessions_scroll = ctk.CTkScrollableFrame(list_frame, label_text="Active Sessions")
        sessions_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Get and display sessions
        sessions = self.chat_history_manager.list_sessions()
        current_session = self.chat_history_manager.get_current_session()
        current_id = current_session.id if current_session else None
        
        for session_info in sessions:
            # Session item frame
            session_frame = ctk.CTkFrame(sessions_scroll)
            session_frame.pack(fill="x", padx=5, pady=5)
            
            # Session info
            info_frame = ctk.CTkFrame(session_frame)
            info_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            
            # Session name and status
            name_text = session_info["name"]
            if session_info["is_current"]:
                name_text += " (Current)"
            
            name_label = ctk.CTkLabel(
                info_frame,
                text=name_text,
                font=ctk.CTkFont(size=14, weight="bold" if session_info["is_current"] else "normal"),
                anchor="w"
            )
            name_label.pack(anchor="w", padx=5, pady=2)
            
            # Session details
            details = f"Messages: {session_info['message_count']} | Created: {session_info['created_at'][:10]} | Updated: {session_info['last_updated'][:10]}"
            details_label = ctk.CTkLabel(
                info_frame,
                text=details,
                font=ctk.CTkFont(size=10),
                text_color="gray70",
                anchor="w"
            )
            details_label.pack(anchor="w", padx=5)
            
            # Action buttons
            actions_frame = ctk.CTkFrame(session_frame)
            actions_frame.pack(side="right", padx=5, pady=5)
            
            if not session_info["is_current"]:
                switch_btn = ctk.CTkButton(
                    actions_frame,
                    text="Switch",
                    width=60,
                    height=30,
                    command=lambda sid=session_info["id"]: self.switch_from_manager(sid, session_window),
                    font=ctk.CTkFont(size=10)
                )
                switch_btn.pack(side="top", pady=2)
            
            delete_btn = ctk.CTkButton(
                actions_frame,
                text="Delete",
                width=60,
                height=30,
                command=lambda sid=session_info["id"], name=session_info["name"]: self.delete_from_manager(sid, name, session_window),
                font=ctk.CTkFont(size=10),
                fg_color="#d13438",
                hover_color="#b02a30"
            )
            delete_btn.pack(side="top", pady=2)
        
        # Bottom buttons
        bottom_frame = ctk.CTkFrame(session_window)
        bottom_frame.pack(fill="x", padx=20, pady=10)
        
        new_session_btn = ctk.CTkButton(
            bottom_frame,
            text="New Session",
            command=lambda: self.new_session_from_manager(session_window)
        )
        new_session_btn.pack(side="left", padx=5)
        
        close_btn = ctk.CTkButton(
            bottom_frame,
            text="Close",
            command=session_window.destroy
        )
        close_btn.pack(side="right", padx=5)
        
        # Session stats
        stats = self.chat_history_manager.get_session_stats()
        stats_text = f"Total Sessions: {stats['total_sessions']} | Total Messages: {stats['total_messages']}"
        ctk.CTkLabel(
            bottom_frame,
            text=stats_text,
            font=ctk.CTkFont(size=10),
            text_color="gray70"
        ).pack()
    
    def switch_from_manager(self, session_id, window):
        """Switch session from manager dialog"""
        self.switch_to_tab(session_id)
        window.destroy()
    
    def delete_from_manager(self, session_id, session_name, window):
        """Delete session from manager dialog"""
        result = tk.messagebox.askyesno(
            "Delete Session", 
            f"Are you sure you want to delete '{session_name}'?"
        )
        if result:
            self.chat_history_manager.delete_session(session_id)
            window.destroy()
            self.refresh_chat_tabs()
            self.refresh_chat_display()
    
    def new_session_from_manager(self, window):
        """Create new session from manager dialog"""
        self.create_new_chat_tab()
        window.destroy()
    
    def on_closing(self):
        """Handle window closing"""
        # Save current session before closing
        self.save_current_session()
        
        if self.minimize_to_tray.get():
            self.root.withdraw()  # Hide window instead of closing
            self.show_tray_notification("AI Companion minimized to system tray")
        else:
            self.root.destroy()
    
    def show_tray_notification(self, message: str):
        """Show a system tray notification"""
        try:
            from plyer import notification
            notification.notify(
                title="AI Companion",
                message=message,
                timeout=3
            )
        except:
            pass  # Fail silently if notifications aren't available
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    app = AICompanionGUI()
    app.run()

if __name__ == "__main__":
    main()
