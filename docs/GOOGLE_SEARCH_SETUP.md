# 🔍 Google Search API Setup Guide

Your AI Companion now supports **both Brave Search and Google Custom Search APIs**! Here's how to set up Google Search for enhanced search capabilities.

## 🚀 Why Google Search API?

### **Advantages:**
- ✅ **High Quality Results** - Google's search algorithm
- ✅ **Rich Snippets** - Enhanced result information  
- ✅ **Global Coverage** - Comprehensive web index
- ✅ **Reliable Uptime** - Google's infrastructure

### **Considerations:**
- 📊 **Free Tier**: 100 queries per day
- 💰 **Paid Tier**: $5 per 1000 queries after free tier
- 🔧 **Setup Required**: Custom Search Engine configuration

---

## 📋 Step-by-Step Setup

### **Step 1: Enable Google Custom Search API**

1. **Go to Google Cloud Console**
   - Visit: https://console.developers.google.com/
   - Sign in with your Google account

2. **Create or Select Project**
   - Create new project or select existing one
   - Note the project name

3. **Enable Custom Search API**
   - Go to "APIs & Services" > "Library"
   - Search for "Custom Search API"
   - Click "Enable"

4. **Create API Key**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy the API key (keep it secure!)

### **Step 2: Create Custom Search Engine**

1. **Go to Custom Search Console**
   - Visit: https://cse.google.com/
   - Sign in with the same Google account

2. **Create New Search Engine**
   - Click "Add" or "New search engine"
   - Enter a name: "AI Companion Search"

3. **Configure Search Settings**
   - **Sites to search**: Enter `*` (asterisk) to search entire web
   - **Language**: Select your preferred language
   - **SafeSearch**: Choose appropriate level

4. **Get Search Engine ID**
   - After creation, go to "Setup" tab
   - Copy the "Search engine ID" (cx parameter)

### **Step 3: Configure AI Companion**

1. **Update .env file**
   ```bash
   # Google Custom Search API
   GOOGLE_SEARCH_API_KEY=your_api_key_from_step1
   GOOGLE_SEARCH_CX=your_search_engine_id_from_step2
   ```

2. **Optional: Set as Primary Provider**
   - Google will be automatically selected as primary if configured
   - Falls back to Brave Search if Google fails or hits quota

---

## 🧪 Testing Your Setup

Run the test script to verify everything works:

```bash
python test_search_providers.py
```

Expected output:
```
🔍 Testing Multi-Provider Search System
==================================================
📊 Provider Status:
   Available: ['google', 'brave']
   Primary: google
   Configured: {'brave': True, 'google': True}

🔍 Testing Primary Provider: Google
------------------------------
I found 3 result(s) for 'Python programming tutorials' using Google Search:

1. **Learn Python - Full Course for Beginners [Tutorial]**
   🔗 https://www.youtube.com/watch?v=rfscVS0vtbw
   📝 This course will give you a full introduction into all of the core concepts in python...
```

---

## 💡 Usage Examples

Your AI Companion will automatically use the best available search provider:

### **Natural Language Requests:**
- *"Search for the latest AI developments"*
- *"Find information about Python web frameworks and create a summary document"*
- *"Look up renewable energy trends"*

### **Provider-Specific Requests:**
- *"Use Google to search for machine learning tutorials"*
- *"Search with Brave for privacy-focused solutions"*

---

## 🔧 Advanced Configuration

### **Search Engine Customization**

You can customize your Google Custom Search Engine:

1. **Go to CSE Control Panel**: https://cse.google.com/
2. **Select your search engine**
3. **Customize settings**:
   - **Look and feel**: Customize appearance
   - **Search features**: Enable image search, etc.
   - **Business settings**: Commercial use settings

### **API Quota Management**

Monitor your usage in Google Cloud Console:
- **APIs & Services** > **Quotas**
- View daily usage and remaining quota
- Set up billing for higher limits if needed

### **Multiple Search Engines**

You can create multiple Custom Search Engines for different purposes:
- General web search
- Academic/research focused
- News and current events
- Technical documentation

---

## 🚨 Troubleshooting

### **Common Issues:**

1. **"API Key Invalid"**
   - Verify API key is copied correctly
   - Ensure Custom Search API is enabled
   - Check API key restrictions in Cloud Console

2. **"Search Engine ID Invalid"**
   - Verify Search Engine ID (cx) is correct
   - Ensure search engine is configured to search entire web

3. **"Quota Exceeded"**
   - You've hit the 100 queries/day free limit
   - Wait until next day or upgrade to paid tier
   - AI Companion will automatically fall back to Brave Search

4. **"No Results"**
   - Check your search engine configuration
   - Ensure "Sites to search" includes `*` for entire web
   - Verify search engine is enabled

### **Getting Help:**

If you encounter issues:
1. Check the test script output for specific error messages
2. Verify all environment variables are set correctly
3. Test the APIs directly in Google Cloud Console
4. Check Google Custom Search documentation

---

## 📊 Comparison: Google vs Brave Search

| Feature | Google Custom Search | Brave Search |
|---------|---------------------|--------------|
| **Free Tier** | 100 queries/day | 2000 queries/month |
| **Result Quality** | Excellent | Very Good |
| **Privacy** | Standard | Privacy-focused |
| **Setup Complexity** | Moderate | Simple |
| **Commercial Use** | Requires configuration | Included |

---

## ✅ Next Steps

Once configured, your AI Companion will:

1. **Automatically prioritize** Google Search for better results
2. **Fall back to Brave** if Google quota is exceeded
3. **Show which provider** was used in responses
4. **Handle errors gracefully** with provider switching

Your search capabilities are now significantly enhanced! 🚀

---

*Last Updated: December 2024*  
*Multi-Provider Search System Active*
