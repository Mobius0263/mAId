"""
AI Companion Configuration
"""
import os
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# API Configuration
BRAVE_SEARCH_API_KEY = os.getenv("BRAVE_SEARCH_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Debug: Print API key status (first few characters only for security)
if BRAVE_SEARCH_API_KEY:
    print(f"[DEBUG] Brave Search API Key loaded: {BRAVE_SEARCH_API_KEY[:10]}...")
else:
    print("[DEBUG] No Brave Search API Key found in environment")

# Model Configuration
class ModelConfig:
    # Vision models (start with Moondream2, upgrade to LLaVA later)
    VISION_MODEL = "moondream2"  # or "llava"
    VISION_MODEL_PATH = "vikhyatk/moondream2"
    
    # Audio models
    WHISPER_MODEL = "small"  # tiny, base, small, medium, large
    WHISPER_DEVICE = "cpu"  # or "cuda" if GPU available
    
    # Language model configuration
    LLM_MODEL = "koboldcpp"  # or "ollama", "lmstudio", etc.
    LLM_API_BASE = "http://localhost:5001"  # KoboldCPP default port
    
    # KoboldCPP specific settings
    KOBOLDCPP_PORTS = [5001, 5000, 8080, 7860]  # Ports to try
    KOBOLDCPP_TIMEOUT = 30  # Request timeout in seconds
    
    # Alternative LLM endpoints
    OLLAMA_API_BASE = "http://localhost:11434"
    LMSTUDIO_API_BASE = "http://localhost:1234"

# Safety Configuration
class SafetyConfig:
    # Safe directories for file operations
    SAFE_DIRECTORIES: List[Path] = [
        Path.home() / "Documents",
        Path.home() / "Downloads", 
        Path.home() / "Desktop",
        PROJECT_ROOT / "data"
    ]
    
    # Forbidden directories
    FORBIDDEN_DIRECTORIES: List[str] = [
        "C:\\Windows",
        "C:\\Program Files",
        "C:\\System32",
        "/System",
        "/usr/bin",
        "/etc"
    ]
    
    # File operation permissions
    ALLOW_FILE_DELETION = False  # Require explicit user confirmation
    ALLOW_SYSTEM_COMMANDS = False
    MAX_FILE_SIZE_MB = 100  # Maximum file size to process

# Tool Configuration
class ToolConfig:
    # Search settings
    MAX_SEARCH_RESULTS = 10
    SEARCH_TIMEOUT = 30
    
    # Vision settings
    MAX_IMAGE_SIZE = (1920, 1080)
    SUPPORTED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".bmp", ".gif"]
    
    # Audio settings
    AUDIO_SAMPLE_RATE = 16000
    MAX_AUDIO_LENGTH = 300  # seconds
    SUPPORTED_AUDIO_FORMATS = [".wav", ".mp3", ".m4a", ".flac"]
    
    # File processing
    SUPPORTED_DOC_FORMATS = [".txt", ".docx", ".pdf", ".xlsx", ".csv", ".pptx"]
    MAX_DOCUMENTS_BATCH = 10

# Logging Configuration
class LogConfig:
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = LOGS_DIR / "ai_companion.log"
    MAX_LOG_SIZE_MB = 50
    BACKUP_COUNT = 5

# Environment validation
def validate_environment() -> Dict[str, Any]:
    """Validate the environment and return status"""
    status = {
        "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
        "project_root": str(PROJECT_ROOT),
        "data_dir_exists": DATA_DIR.exists(),
        "logs_dir_exists": LOGS_DIR.exists(),
        "brave_api_configured": bool(BRAVE_SEARCH_API_KEY),
        "openai_api_configured": bool(OPENAI_API_KEY),
    }
    return status

if __name__ == "__main__":
    # Quick environment check
    env_status = validate_environment()
    print("AI Companion Environment Status:")
    for key, value in env_status.items():
        print(f"  {key}: {value}")
