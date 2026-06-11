"""
UI Configuration for AI Companion
Centralized configuration for customizable UI elements
"""

from pathlib import Path
from typing import Dict, Any
import json

class UIConfig:
    """Manages UI configuration settings"""
    
    def __init__(self):
        self.config_file = Path(__file__).parent.parent.parent / "config" / "ui_config.json"
        self.config_file.parent.mkdir(exist_ok=True)
        
        # Default configuration values
        self.defaults = {
            "font": {
                "base_size": 14,          # Base font size in points
                "scale_percentage": 100,  # Current scale as percentage (50% to 300%)
                "min_scale": 50,          # Minimum scale percentage
                "max_scale": 300,         # Maximum scale percentage
                "family": "Segoe UI",     # Primary font family
                "code_family": "Consolas", # Code font family
                "input_scale": 0.9        # Input field font scale relative to base (90%)
            },
            "spacing": {
                "chat_padding": 10,
                "sidebar_padding": 20,
                "line_spacing": 1.2
            },
            "colors": {
                "primary": "#0078d4",
                "success": "#107c10", 
                "warning": "#ff8c00",
                "error": "#d13438",
                "code_bg": "#1e1e1e",
                "code_fg": "#d4d4d4"
            }
        }
        
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create with defaults"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                
                # Merge with defaults to ensure all keys exist
                config = self.defaults.copy()
                self._deep_merge(config, loaded_config)
                return config
            else:
                # Create default config file
                self.save_config(self.defaults)
                return self.defaults.copy()
                
        except Exception as e:
            print(f"Error loading UI config: {e}")
            return self.defaults.copy()
    
    def save_config(self, config: Dict[str, Any] = None) -> bool:
        """Save configuration to file"""
        try:
            if config is None:
                config = self.config
                
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
            
        except Exception as e:
            print(f"Error saving UI config: {e}")
            return False
    
    def _deep_merge(self, target: Dict, source: Dict):
        """Deep merge source dict into target dict"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
    
    def get_font_size(self, element_type: str = "base") -> int:
        """Get font size for specific element type"""
        base_size = self.config["font"]["base_size"]
        scale = self.config["font"]["scale_percentage"] / 100.0
        
        if element_type == "input":
            input_scale = self.config["font"]["input_scale"]
            return int(base_size * scale * input_scale)
        elif element_type == "h1":
            return int(base_size * scale) + 4
        elif element_type == "h2":
            return int(base_size * scale) + 2
        elif element_type == "h3":
            return int(base_size * scale) + 1
        else:  # base, normal, code, etc.
            return int(base_size * scale)
    
    def get_font_family(self, font_type: str = "normal") -> str:
        """Get font family for specific type"""
        if font_type == "code":
            return self.config["font"]["code_family"]
        else:
            return self.config["font"]["family"]
    
    def set_font_scale(self, percentage: int) -> bool:
        """Set font scale percentage and save config"""
        min_scale = self.config["font"]["min_scale"]
        max_scale = self.config["font"]["max_scale"]
        
        # Clamp to valid range
        percentage = max(min_scale, min(max_scale, percentage))
        
        self.config["font"]["scale_percentage"] = percentage
        return self.save_config()
    
    def get_font_scale(self) -> int:
        """Get current font scale percentage"""
        return self.config["font"]["scale_percentage"]
    
    def get_font_scale_range(self) -> tuple:
        """Get min and max font scale percentages"""
        return (self.config["font"]["min_scale"], self.config["font"]["max_scale"])
    
    def get_color(self, color_name: str) -> str:
        """Get color value by name"""
        return self.config["colors"].get(color_name, "#000000")
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to defaults"""
        self.config = self.defaults.copy()
        return self.save_config()

# Global config instance
ui_config = UIConfig()
