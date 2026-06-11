# Gemini API Integration Guide

## 🚀 Adding Google Gemini to your AI Companion

Your AI Companion now supports **Google Gemini API** as an alternative brain to KoboldCPP! Gemini offers:

- ✅ Cloud-based AI (no local model needed)
- ✅ Fast response times
- ✅ Advanced reasoning capabilities
- ✅ Large context window
- ✅ Automatic fallback to KoboldCPP

## 📋 Setup Instructions

### 1. Install Dependencies
```bash
pip install google-generativeai
```

### 2. Get Your Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your new API key

### 3. Configure Environment
Add your API key to your `.env` file:
```env
# Google Gemini API Configuration
GEMINI_API_KEY=your_api_key_here
GEMINI_TIMEOUT=30
GEMINI_MAX_TOKENS=1000
```

### 4. Optional: Choose Model
The default model is `gemini-1.5-flash`. You can change it in the code:
- `gemini-1.5-flash` - Fast and efficient (recommended)
- `gemini-1.5-pro` - More capable but slower
- `gemini-1.0-pro` - Older version

## 🔄 How It Works

### Brain Selection Priority:
1. **Gemini API** (if configured and available)
2. **KoboldCPP** (fallback if Gemini fails)
3. **Error message** (if neither works)

### Status Display:
- 🟢 **Gemini** - Using Google Gemini API
- 🔵 **KoboldCPP** - Using local KoboldCPP model
- ❌ **Disconnected** - No brain available

## 🧪 Testing Your Setup

Run the test script to verify everything works:

```python
# Test Gemini connection
from src.core.gemini_client import test_gemini_connection
test_gemini_connection()
```

Or simply start your AI Companion - it will automatically try Gemini first!

## 💡 Benefits of Using Gemini

### Advantages:
- **No local setup** - works immediately with API key
- **Fast responses** - cloud-based processing
- **Always available** - no need to run local models
- **Latest AI capabilities** - regularly updated by Google

### When to Use KoboldCPP Instead:
- **Privacy concerns** - keep everything local
- **Custom models** - use specific fine-tuned models
- **Offline usage** - no internet required
- **Cost control** - avoid API usage charges

## 🔧 Advanced Configuration

### Custom Model Selection:
```python
# In gemini_client.py, change the model:
client = GeminiClient(model_name="gemini-1.5-pro")
```

### Adjust Generation Settings:
```python
# Modify temperature, max tokens, etc.
GEMINI_MAX_TOKENS=2000  # Longer responses
```

### Force KoboldCPP Usage:
If you want to skip Gemini and use only KoboldCPP, comment out the Gemini import in `orchestrator.py`:

```python
# Comment this line to disable Gemini:
# from core.gemini_client import GeminiClient
```

## 🎯 What's New

Your AI Companion now automatically:
1. ✅ Tries Gemini API first (if configured)
2. ✅ Falls back to KoboldCPP if needed
3. ✅ Shows which brain is active in the status
4. ✅ Handles errors gracefully
5. ✅ Works with all existing features (search, files, etc.)

## 🐛 Troubleshooting

### Common Issues:

**"Import google.generativeai could not be resolved"**
```bash
pip install google-generativeai
```

**"GEMINI_API_KEY not found"**
- Add your API key to `.env` file
- Make sure the file is in the project root

**"Gemini API test failed"**
- Check your API key is valid
- Verify internet connection
- Try regenerating the API key

**Rate limiting errors:**
- Gemini has usage limits
- The app will automatically fall back to KoboldCPP

## 📊 Cost Considerations

- Gemini has a **generous free tier**
- Free tier includes thousands of requests per month
- See [Google AI pricing](https://ai.google.dev/pricing) for details
- KoboldCPP remains free for unlimited local usage

## 🎉 Ready to Go!

Your AI Companion is now enhanced with Google Gemini! Simply restart the application and you'll see:
- 🟢 **Gemini** status if successfully connected
- All the same great features with improved AI capabilities
- Automatic fallback to KoboldCPP if needed

Enjoy your upgraded AI companion! 🚀
