# AI Companion Project

A local AI companion built with multiple AI backends and specialized tools for enhanced capabilities.

## ✨ Features

- 🧠 **Smart AI System**: Character-based personalities with intelligent tool selection
- 🎭 **Character System**: SillyTavern-style personality profiles for different AI behaviors
- 🤖 **Intelligent Orchestration**: AI-powered reasoning for tool selection and workflow
- 💾 **Persistent Memory**: Cross-session conversation memory and context building
- 🔍 **Web Search**: Internet search capabilities using Brave Search API
- 👁️ **Vision Analysis**: Image and document analysis using Moondream2/LLaVA
- 🎵 **Audio Processing**: Speech-to-text using OpenAI Whisper
- 📁 **File Operations**: Create, edit, delete, and find files (with safety restrictions)
- ⏰ **Task Scheduling**: Smart scheduling and reminders
- 🎨 **Modern GUI**: SillyTavern-inspired interface with dark theme

## 🧠 AI Backend Options

### Google Gemini API (Recommended)
- ✅ Cloud-based, fast responses
- ✅ Latest AI capabilities
- ✅ No local setup required
- ✅ Generous free tier

### KoboldCPP (Local Alternative)
- ✅ Complete privacy (local processing)
- ✅ Custom model support
- ✅ Offline usage
- ✅ No API costs

The system automatically tries Gemini first, then falls back to KoboldCPP if needed.

## 📁 Project Structure

```
ai-companion/
├── src/
│   ├── core/                        # Core AI companion logic
│   │   ├── smart_orchestrator.py    # Intelligent AI orchestration
│   │   ├── character_system.py      # SillyTavern-style personalities
│   │   ├── intelligent_tool_selector.py # AI-powered tool selection
│   │   ├── memory_manager.py        # Conversation memory system
│   │   ├── gemini_client.py         # Google Gemini integration
│   │   └── config.py               # Configuration
│   ├── tools/                  # Specialized tools
│   │   ├── search/            # Web search functionality
│   │   ├── vision/            # Image/document analysis
│   │   ├── audio/             # Speech processing
│   │   ├── files/             # File operations
│   │   └── scheduler/         # Task scheduling
│   ├── utils/                  # Utility functions
│   └── interfaces/             # User interfaces
├── data/                       # Data storage
├── logs/                       # Application logs
├── tests/                      # Test files
└── docs/                       # Documentation
```

## Setup

### First Time Setup
1. Virtual environment is already created in `.venv/`
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Activating the Environment

**VS Code (Recommended):**
- Open the project folder in VS Code
- VS Code should automatically detect and use the `.venv` environment
- Check the bottom-left status bar for Python version

**Manual Activation:**
```bash
# Windows Command Prompt
activate_env.bat

# Windows PowerShell  
.\activate_env.ps1

# Or manually:
.venv\Scripts\activate
```

3. Configure API keys (create `.env` file):
   ```
   BRAVE_SEARCH_API_KEY=your_api_key_here
   OPENAI_API_KEY=optional_for_fallback
   ```

## Quick Start

```python
from src.core.brain import AICompanion

companion = AICompanion()
response = companion.chat("Take a screenshot and tell me what's on my screen")
```

## Safety Features

- File operations restricted to safe directories
- User confirmation for potentially dangerous operations
- Sandboxed execution environment
- Audit logging for all actions

## Development Status

- [x] Project structure
- [ ] Web search implementation
- [ ] Vision analysis setup
- [ ] Audio processing
- [ ] File operations (with safety)
- [ ] Task scheduling
- [ ] Integration testing

## License

MIT License
