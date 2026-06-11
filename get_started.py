"""
AI Companion Project - Getting Started Guide
Run this script to understand your project structure and next steps.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def show_project_structure():
    """Display the project structure"""
    print("📁 Project Structure:")
    print("""
AI Companion Project/
├── 📋 requirements.txt        # All Python dependencies
├── 📋 .env.example           # Environment variables template
├── 🚀 demo_startup.py        # Quick status check
├── 🎯 get_started.py         # This file!
├── 📁 src/
│   ├── 🧠 core/
│   │   ├── config.py              # Configuration & settings
│   │   ├── smart_orchestrator.py  # AI coordination with character system
│   │   ├── character_system.py    # SillyTavern-style personality system
│   │   └── intelligent_tool_selector.py # AI-powered tool selection
│   └── 🛠️  tools/
│       ├── 🔍 search/
│       │   └── searcher.py   # Web search (Brave API)
│       └── 👁️  vision/
│           └── analyzer.py   # Image analysis (Moondream2)
├── 📁 data/                  # Your AI's data storage
├── 📁 logs/                  # Application logs
└── 📁 tests/                 # Test files
""")

def show_installation_guide():
    """Show step-by-step installation guide"""
    print("🔧 Installation & Setup Guide:")
    print("=" * 50)
    
    print("\n1️⃣  BASIC SETUP (Already Done!)")
    print("  ✅ Python environment created")
    print("  ✅ Basic packages installed")
    print("  ✅ Project structure created")
    
    print("\n2️⃣  GET API KEYS (Required for full functionality)")
    print("  🔑 Brave Search API (Free):")
    print("     → Visit: https://api.search.brave.com/app/keys")
    print("     → Sign up and get your free API key")
    print("     → Copy .env.example to .env")
    print("     → Add your API key to .env file")
    
    print("\n3️⃣  INSTALL ADDITIONAL PACKAGES")
    print("  📦 For Vision Analysis (Moondream2):")
    print("     → Already installed! (transformers, torch)")
    
    print("  📦 For Audio Processing (Optional):")
    print("     → pip install openai-whisper SpeechRecognition pyaudio")
    
    print("  📦 For Full Feature Set:")
    print("     → pip install -r requirements.txt")
    
    print("\n4️⃣  CHOOSE YOUR 7B LANGUAGE MODEL")
    print("  🧠 Recommended Options:")
    print("     → Ollama (Easy): Download from ollama.ai")
    print("     → LM Studio (GUI): Download from lmstudio.ai")
    print("     → Direct Python: Use transformers library")

def show_quick_tests():
    """Show how to test each component"""
    print("\n🧪 Quick Tests:")
    print("=" * 30)
    
    print("\n📊 Check Overall Status:")
    print("   python demo_startup.py")
    
    print("\n🔍 Test Web Search:")
    print("   python src/tools/search/searcher.py")
    
    print("\n👁️  Test Vision Analysis:")
    print("   python src/tools/vision/analyzer.py")
    
    print("\n🤖 Try the Smart AI System:")
    print("   python test_smart_orchestrator.py")

def show_development_roadmap():
    """Show the development roadmap"""
    print("\n🗺️  Development Roadmap:")
    print("=" * 40)
    
    print("\n🎯 Phase 1: Core Tools (1-2 weeks)")
    print("  [ ] Get Brave Search API working")
    print("  [ ] Test Moondream2 vision analysis")
    print("  [ ] Set up your preferred 7B model")
    print("  [ ] Create basic conversation flow")
    
    print("\n🎯 Phase 2: Enhanced Features (2-3 weeks)")
    print("  [ ] Add Whisper audio processing")
    print("  [ ] Implement safe file operations")
    print("  [ ] Add task scheduling capabilities")
    print("  [ ] Create better prompts for tool selection")
    
    print("\n🎯 Phase 3: Integration & Polish (2-4 weeks)")
    print("  [ ] Build complex multi-tool workflows")
    print("  [ ] Add conversation memory/context")
    print("  [ ] Create a proper user interface")
    print("  [ ] Add safety features and logging")
    
    print("\n🎯 Phase 4: Advanced Features (ongoing)")
    print("  [ ] Upgrade to LLaVA for better vision")
    print("  [ ] Add custom tool creation")
    print("  [ ] Build learning/adaptation features")
    print("  [ ] Create plugin system")

def show_example_workflows():
    """Show example workflows you can build"""
    print("\n✨ Example Workflows You Can Build:")
    print("=" * 45)
    
    examples = [
        {
            "name": "Research Assistant",
            "description": "Search → Analyze → Summarize → Save to document",
            "command": '"Research the latest AI developments and create a summary"'
        },
        {
            "name": "Screen Helper", 
            "description": "Screenshot → Analyze → Search for help → Provide guidance",
            "command": '"What software is this and how do I use this feature?"'
        },
        {
            "name": "Content Analyzer",
            "description": "Audio transcription → Topic extraction → Related search → Report generation",
            "command": '"Transcribe this meeting and find related resources"'
        },
        {
            "name": "Smart Organizer",
            "description": "File analysis → Content categorization → Auto-organization",
            "command": '"Organize my downloads folder by content type"'
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['name']}")
        print(f"   Flow: {example['description']}")
        print(f"   Command: {example['command']}")

def main():
    """Main function"""
    print("🤖 AI Companion Project - Getting Started")
    print("=" * 60)
    
    show_project_structure()
    show_installation_guide()
    show_quick_tests()
    show_development_roadmap()
    show_example_workflows()
    
    print("\n🎉 Congratulations!")
    print("You now have a solid foundation for your AI companion!")
    print("\n💡 Start by:")
    print("  1. Getting a Brave Search API key")
    print("  2. Running the demo: python demo_startup.py")
    print("  3. Testing individual tools")
    print("  4. Setting up your preferred 7B language model")
    
    print("\n📚 Need help? Check the README.md for detailed documentation!")

if __name__ == "__main__":
    main()
