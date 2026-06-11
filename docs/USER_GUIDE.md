# 🤖 AI Companion - User Guide

## 🚀 Quick Start

### Easy Setup (3 steps):
1. **Run setup**: Double-click `setup.bat`
2. **Add API key**: Edit `.env` file with your Brave Search API key
3. **Launch**: Double-click `ai_companion_launcher.py`

### Your AI companion will appear with:
- 📱 **Modern GUI**: SillyTavern-inspired interface
- 🔍 **System Tray**: Minimizes to tray icon (robot icon)
- 🧠 **Smart AI**: Uses your KoboldCPP model for decisions
- 🛠️ **Multiple Tools**: Web search, vision analysis, and more

---

## 🎯 Features

### 💬 **Chat Interface**
- Type natural language commands
- AI decides which tools to use automatically
- Real-time responses with reasoning explanations

### 🔍 **Web Search**
- "Search for latest AI news"
- "Find information about Python programming"
- Uses Brave Search API (2,000 free searches/month)

### 👁️ **Vision Analysis** 
- "Take a screenshot and tell me what's on my screen"
- "Analyze this image"
- Uses Moondream2 for fast local processing

### ⚡ **Quick Actions**
- 📸 Screenshot button for instant screen analysis
- 🔍 Search button for quick web searches
- 🗑️ Clear button to reset conversation

### 🎛️ **System Tray Features**
- Right-click tray icon for quick menu
- Quick screenshot from tray
- Quick search from tray
- Always accessible when minimized

---

## 🎨 Interface Guide

### Left Sidebar:
- **System Status**: Shows brain and tools connection
- **Quick Actions**: One-click common tasks
- **Settings**: Always on top, minimize to tray options

### Main Chat Area:
- **Messages**: Timestamped conversation history
- **Input Box**: Type your requests here
- **Send Button**: Or press Enter to send

### System Tray:
- **Robot Icon**: Your AI companion in the tray
- **Right-click**: Access quick features
- **Double-click**: Open main window

---

## 💡 Example Commands

### 🔍 **Search Commands**:
```
"Search for best AI models 2025"
"Look up Python tutorials"
"Find news about space exploration"
```

### 👁️ **Vision Commands**:
```
"Take a screenshot and describe it"
"What applications are open on my screen?"
"Analyze what I'm working on"
```

### 🔧 **Multi-tool Commands**:
```
"Screenshot my screen and search for help with this software"
"Analyze this image and find similar topics online"
```

---

## ⚙️ Settings & Configuration

### 📝 **Environment Variables** (`.env` file):
```env
# Required for web search
BRAVE_SEARCH_API_KEY=your_api_key_here

# KoboldCPP settings (adjust if needed)
KOBOLDCPP_URL=http://localhost:5001
KOBOLDCPP_TIMEOUT=30
```

### 🧠 **KoboldCPP Requirements**:
- Run KoboldCPP with your 7B model
- Default port: 5001 (or edit `.env`)
- Enable API in KoboldCPP settings

### 📱 **GUI Settings**:
- **Always on top**: Keep window above others
- **Minimize to tray**: Hide to system tray instead of closing
- **Dark theme**: Modern dark interface (default)

---

## 🏗️ Creating an Executable

### For Yourself:
```bash
# Run the build script
build_executable.bat

# Creates: build/exe.win-amd64-*/AI_Companion.exe
```

### For Distribution:
1. Copy the entire `build/exe.win-amd64-*` folder
2. Include `.env.example` file
3. User needs to:
   - Rename `.env.example` to `.env`
   - Add their Brave Search API key
   - Run KoboldCPP with their model
   - Double-click `AI_Companion.exe`

---

## 🔧 Troubleshooting

### ❌ **"Brain: Disconnected"**
- Make sure KoboldCPP is running
- Check port in `.env` file (default: 5001)
- Verify KoboldCPP API is enabled

### ❌ **"Web Search: Need API key"**
- Get free API key: https://api.search.brave.com/app/keys
- Add to `.env` file: `BRAVE_SEARCH_API_KEY=your_key`

### ❌ **"Import Error"**
- Run `setup.bat` to install missing packages
- Or manually: `pip install customtkinter pystray`

### ⚠️ **Tray Icon Missing**
- Some Linux distributions need: `sudo apt install python3-tk`
- Windows: Usually works out of the box

---

## 🎯 Advanced Usage

### 🔗 **Custom Model Integration**:
- Edit `src/core/config.py` for different model APIs
- Supports Ollama, LM Studio, or custom endpoints

### 🛠️ **Adding New Tools**:
- Create new tools in `src/tools/`
- Register in `smart_orchestrator.py`
- AI will automatically learn to use them through intelligent tool selection

### 🎨 **UI Customization**:
- Edit `src/gui/main_app.py` for interface changes
- Themes: light, dark, or system
- Colors: blue, green, dark-blue

---

## 📞 Support

### 🔍 **Getting Help**:
- Check the terminal output for error messages
- Run `demo_startup.py` to check system status
- Verify all requirements in the status panel

### 🐛 **Common Issues**:
- **Slow responses**: Model might be too large for your hardware
- **No responses**: Check KoboldCPP connection
- **Missing features**: Install optional packages with `pip install -r requirements.txt`

---

## 🎉 What's Next?

Your AI companion is now ready! It combines:
- 🧠 **Local AI**: Your KoboldCPP model making decisions
- 🔍 **Web Search**: Brave API for internet information
- 👁️ **Vision**: Moondream2 for image analysis
- 📱 **Modern UI**: Professional desktop application
- 🔧 **System Integration**: Tray icon and notifications

Enjoy your new AI companion! 🚀
