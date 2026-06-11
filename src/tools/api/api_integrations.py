"""
API Integrations Manager for AI Companion
Manages external API connections and integrations
"""

import os
import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class APIIntegrationManager:
    """Manages various API integrations and external services"""
    
    def __init__(self):
        """Initialize API manager with available integrations"""
        self.integrations = {}
        self.rate_limits = {}
        self._initialize_integrations()
        print(f"[API] Available integrations: {list(self.integrations.keys())}")
    
    def _initialize_integrations(self):
        """Initialize available API integrations"""
        
        # Weather API (OpenWeatherMap)
        weather_api_key = os.getenv("OPENWEATHER_API_KEY")
        if weather_api_key:
            self.integrations["weather"] = {
                "name": "OpenWeatherMap",
                "base_url": "https://api.openweathermap.org/data/2.5",
                "api_key": weather_api_key,
                "rate_limit": 60,  # calls per minute
                "available": True
            }
        
        # News API
        news_api_key = os.getenv("NEWS_API_KEY")
        if news_api_key:
            self.integrations["news"] = {
                "name": "NewsAPI",
                "base_url": "https://newsapi.org/v2",
                "api_key": news_api_key,
                "rate_limit": 100,  # calls per day for free tier
                "available": True
            }
        
        # GitHub API
        github_token = os.getenv("GITHUB_TOKEN")
        self.integrations["github"] = {
            "name": "GitHub API",
            "base_url": "https://api.github.com",
            "api_key": github_token,
            "rate_limit": 5000 if github_token else 60,  # per hour
            "available": True
        }
        
        # REST API Generic Client
        self.integrations["rest"] = {
            "name": "Generic REST Client",
            "base_url": None,
            "api_key": None,
            "rate_limit": None,
            "available": True
        }
        
        # Currency Exchange API
        currency_api_key = os.getenv("CURRENCY_API_KEY")
        if currency_api_key:
            self.integrations["currency"] = {
                "name": "Exchange Rates API",
                "base_url": "https://api.exchangerate-api.com/v4",
                "api_key": currency_api_key,
                "rate_limit": 1500,  # per month
                "available": True
            }
        
        # Translation API
        translate_api_key = os.getenv("GOOGLE_TRANSLATE_API_KEY")
        if translate_api_key:
            self.integrations["translate"] = {
                "name": "Google Translate",
                "base_url": "https://translation.googleapis.com/language/translate/v2",
                "api_key": translate_api_key,
                "rate_limit": 100000,  # characters per day
                "available": True
            }
    
    def get_weather(self, location: str, units: str = "metric") -> Dict[str, Any]:
        """Get current weather for a location"""
        
        if "weather" not in self.integrations:
            return {
                "success": False,
                "error": "Weather API not configured. Set OPENWEATHER_API_KEY in .env"
            }
        
        api_config = self.integrations["weather"]
        
        try:
            url = f"{api_config['base_url']}/weather"
            params = {
                "q": location,
                "appid": api_config["api_key"],
                "units": units
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    "success": True,
                    "location": data["name"],
                    "country": data["sys"]["country"],
                    "temperature": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "humidity": data["main"]["humidity"],
                    "pressure": data["main"]["pressure"],
                    "description": data["weather"][0]["description"].title(),
                    "wind_speed": data.get("wind", {}).get("speed", 0),
                    "units": units,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"Weather API error: {response.status_code}",
                    "details": response.text
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Weather request failed: {str(e)}"
            }
    
    def get_news(self, query: str = None, category: str = None, country: str = "us", 
                 max_articles: int = 10) -> Dict[str, Any]:
        """Get latest news articles"""
        
        if "news" not in self.integrations:
            return {
                "success": False,
                "error": "News API not configured. Set NEWS_API_KEY in .env"
            }
        
        api_config = self.integrations["news"]
        
        try:
            if query:
                url = f"{api_config['base_url']}/everything"
                params = {
                    "q": query,
                    "apiKey": api_config["api_key"],
                    "sortBy": "publishedAt",
                    "pageSize": max_articles
                }
            else:
                url = f"{api_config['base_url']}/top-headlines"
                params = {
                    "apiKey": api_config["api_key"],
                    "country": country,
                    "pageSize": max_articles
                }
                if category:
                    params["category"] = category
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                articles = []
                for article in data.get("articles", []):
                    articles.append({
                        "title": article["title"],
                        "description": article["description"],
                        "url": article["url"],
                        "source": article["source"]["name"],
                        "published_at": article["publishedAt"],
                        "author": article.get("author", "Unknown")
                    })
                
                return {
                    "success": True,
                    "total_results": data.get("totalResults", len(articles)),
                    "articles": articles,
                    "query": query,
                    "category": category
                }
            else:
                return {
                    "success": False,
                    "error": f"News API error: {response.status_code}",
                    "details": response.text
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"News request failed: {str(e)}"
            }
    
    def github_search_repos(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search GitHub repositories"""
        
        api_config = self.integrations["github"]
        
        try:
            url = f"{api_config['base_url']}/search/repositories"
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": max_results
            }
            
            headers = {}
            if api_config["api_key"]:
                headers["Authorization"] = f"token {api_config['api_key']}"
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                repos = []
                for repo in data.get("items", []):
                    repos.append({
                        "name": repo["name"],
                        "full_name": repo["full_name"],
                        "description": repo["description"],
                        "stars": repo["stargazers_count"],
                        "forks": repo["forks_count"],
                        "language": repo["language"],
                        "url": repo["html_url"],
                        "updated_at": repo["updated_at"]
                    })
                
                return {
                    "success": True,
                    "total_count": data.get("total_count", len(repos)),
                    "repositories": repos,
                    "query": query
                }
            else:
                return {
                    "success": False,
                    "error": f"GitHub API error: {response.status_code}",
                    "details": response.text
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"GitHub search failed: {str(e)}"
            }
    
    def get_exchange_rates(self, base_currency: str = "USD", 
                          target_currencies: List[str] = None) -> Dict[str, Any]:
        """Get current exchange rates"""
        
        try:
            # Use free exchange rate API
            url = f"https://api.exchangerate-api.com/v4/latest/{base_currency.upper()}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                rates = data.get("rates", {})
                
                if target_currencies:
                    filtered_rates = {
                        curr: rates.get(curr.upper()) 
                        for curr in target_currencies 
                        if curr.upper() in rates
                    }
                else:
                    filtered_rates = rates
                
                return {
                    "success": True,
                    "base_currency": base_currency.upper(),
                    "date": data.get("date"),
                    "rates": filtered_rates
                }
            else:
                return {
                    "success": False,
                    "error": f"Exchange rate API error: {response.status_code}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Exchange rate request failed: {str(e)}"
            }
    
    def translate_text(self, text: str, target_language: str, 
                      source_language: str = "auto") -> Dict[str, Any]:
        """Translate text using available translation service"""
        
        if "translate" not in self.integrations:
            # Try free translation service as fallback
            return self._free_translate(text, target_language, source_language)
        
        # Google Translate implementation would go here
        # For now, use free service
        return self._free_translate(text, target_language, source_language)
    
    def _free_translate(self, text: str, target_lang: str, source_lang: str = "auto") -> Dict[str, Any]:
        """Use free translation service"""
        try:
            # Using MyMemory free translation API
            url = "https://api.mymemory.translated.net/get"
            params = {
                "q": text,
                "langpair": f"{source_lang}|{target_lang}"
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("responseStatus") == 200:
                    return {
                        "success": True,
                        "original_text": text,
                        "translated_text": data["responseData"]["translatedText"],
                        "source_language": source_lang,
                        "target_language": target_lang,
                        "service": "MyMemory"
                    }
            
            return {
                "success": False,
                "error": "Translation failed",
                "service": "MyMemory"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Translation request failed: {str(e)}"
            }
    
    def make_rest_request(self, url: str, method: str = "GET", headers: Dict[str, str] = None,
                         data: Dict[str, Any] = None, params: Dict[str, str] = None) -> Dict[str, Any]:
        """Make a generic REST API request"""
        
        try:
            method = method.upper()
            
            request_kwargs = {
                "timeout": 30,
                "headers": headers or {}
            }
            
            if params:
                request_kwargs["params"] = params
            
            if data and method in ["POST", "PUT", "PATCH"]:
                request_kwargs["json"] = data
            
            response = requests.request(method, url, **request_kwargs)
            
            # Try to parse JSON response
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text}
            
            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "data": response_data,
                "url": url,
                "method": method
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"REST request failed: {str(e)}",
                "url": url,
                "method": method
            }
    
    def get_integration_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all integrations"""
        
        status = {}
        
        for integration_name, config in self.integrations.items():
            status[integration_name] = {
                "name": config["name"],
                "available": config["available"],
                "has_api_key": bool(config.get("api_key")),
                "rate_limit": config.get("rate_limit"),
                "base_url": config.get("base_url")
            }
        
        return status
    
    def test_integrations(self) -> Dict[str, Dict[str, Any]]:
        """Test all available integrations"""
        
        results = {}
        
        # Test weather
        if "weather" in self.integrations:
            try:
                result = self.get_weather("London")
                results["weather"] = {
                    "status": "✅ Working" if result["success"] else "❌ Failed",
                    "error": result.get("error")
                }
            except Exception as e:
                results["weather"] = {"status": "❌ Error", "error": str(e)}
        
        # Test news
        if "news" in self.integrations:
            try:
                result = self.get_news(max_articles=1)
                results["news"] = {
                    "status": "✅ Working" if result["success"] else "❌ Failed",
                    "error": result.get("error")
                }
            except Exception as e:
                results["news"] = {"status": "❌ Error", "error": str(e)}
        
        # Test GitHub
        try:
            result = self.github_search_repos("python", max_results=1)
            results["github"] = {
                "status": "✅ Working" if result["success"] else "❌ Failed",
                "error": result.get("error")
            }
        except Exception as e:
            results["github"] = {"status": "❌ Error", "error": str(e)}
        
        return results

# Demo function
def demo_api_integrations():
    """Demo API integration capabilities"""
    print("🔗 API Integrations Demo")
    print("=" * 30)
    
    api_manager = APIIntegrationManager()
    
    # Show integration status
    print("Integration Status:")
    status = api_manager.get_integration_status()
    for name, info in status.items():
        api_key_status = "🔑" if info["has_api_key"] else "🔓"
        print(f"  {api_key_status} {info['name']}: {'✅' if info['available'] else '❌'}")
    
    print("\n🧪 Testing integrations...")
    test_results = api_manager.test_integrations()
    for integration, result in test_results.items():
        print(f"  {integration}: {result['status']}")
        if result.get("error"):
            print(f"    Error: {result['error']}")
    
    # Test exchange rates (usually works without API key)
    print("\n💰 Testing exchange rates...")
    rates_result = api_manager.get_exchange_rates("USD", ["EUR", "GBP", "JPY"])
    if rates_result["success"]:
        print("✅ Exchange rates working!")
        for curr, rate in list(rates_result["rates"].items())[:3]:
            print(f"  1 USD = {rate} {curr}")
    else:
        print(f"❌ Exchange rates failed: {rates_result['error']}")

if __name__ == "__main__":
    demo_api_integrations()
