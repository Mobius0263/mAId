"""
Enhanced Web Search Tool - Multiple Search Provider Support
Supports Brave Search API and Google Custom Search API
"""

import os
import requests
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MultiSearcher:
    """Handles web searches using multiple search providers"""
    
    def __init__(self):
        # Brave Search API configuration
        self.brave_api_key = os.getenv("BRAVE_SEARCH_API_KEY")
        self.brave_base_url = "https://api.search.brave.com/res/v1/web/search"
        
        # Google Custom Search API configuration
        self.google_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.google_cx = os.getenv("GOOGLE_SEARCH_CX")  # Custom Search Engine ID
        self.google_base_url = "https://www.googleapis.com/customsearch/v1"
        
        # Determine available providers
        self.providers = self._detect_available_providers()
        self.primary_provider = self._select_primary_provider()
        
        print(f"[DEBUG] MultiSearcher - Available providers: {self.providers}")
        print(f"[DEBUG] MultiSearcher - Primary provider: {self.primary_provider}")
    
    def _detect_available_providers(self) -> List[str]:
        """Detect which search providers are configured"""
        providers = []
        
        if self.brave_api_key:
            providers.append("brave")
            print(f"[DEBUG] Brave Search API configured")
        
        if self.google_api_key and self.google_cx:
            providers.append("google")
            print(f"[DEBUG] Google Custom Search API configured")
        
        return providers
    
    def _select_primary_provider(self) -> Optional[str]:
        """Select the primary search provider based on preference and availability"""
        # Priority: Google first (often more accurate), then Brave
        preferred_order = ["google", "brave"]
        
        for provider in preferred_order:
            if provider in self.providers:
                return provider
        
        return None
    
    def search(self, query: str, count: int = 10, country: str = "US", provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform a web search using the specified or primary provider
        
        Args:
            query: Search query string
            count: Number of results to return
            country: Country code for localized results
            provider: Force specific provider ("brave" or "google")
            
        Returns:
            Dictionary containing search results and metadata
        """
        # Use specified provider or fall back to primary
        use_provider = provider if provider and provider in self.providers else self.primary_provider
        
        if not use_provider:
            return {
                "error": "No search providers configured. Please set up Brave Search or Google Custom Search API.",
                "results": [],
                "provider": None
            }
        
        print(f"[DEBUG] Using search provider: {use_provider}")
        
        try:
            if use_provider == "brave":
                return self._search_brave(query, count, country)
            elif use_provider == "google":
                return self._search_google(query, count, country)
            else:
                return {
                    "error": f"Unknown provider: {use_provider}",
                    "results": [],
                    "provider": use_provider
                }
        
        except Exception as e:
            # If primary provider fails, try fallback
            fallback_providers = [p for p in self.providers if p != use_provider]
            
            if fallback_providers:
                fallback_provider = fallback_providers[0]
                print(f"[DEBUG] {use_provider} failed, trying fallback: {fallback_provider}")
                
                try:
                    if fallback_provider == "brave":
                        result = self._search_brave(query, count, country)
                    elif fallback_provider == "google":
                        result = self._search_google(query, count, country)
                    
                    result["fallback_used"] = True
                    result["original_provider"] = use_provider
                    return result
                    
                except Exception as fallback_error:
                    return {
                        "error": f"Both {use_provider} and {fallback_provider} failed: {e}, {fallback_error}",
                        "results": [],
                        "provider": use_provider
                    }
            else:
                return {
                    "error": f"Search failed: {e}",
                    "results": [],
                    "provider": use_provider
                }
    
    def _search_brave(self, query: str, count: int, country: str) -> Dict[str, Any]:
        """Search using Brave Search API"""
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.brave_api_key
        }
        
        params = {
            "q": query,
            "count": min(count, 20),  # Brave free tier limit
            "country": country,
            "search_lang": "en",
            "ui_lang": "en-US",
            "freshness": "pw"  # Past week for fresh results
        }
        
        response = requests.get(
            self.brave_base_url,
            headers=headers,
            params=params,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return self._format_brave_results(data, query)
        else:
            raise Exception(f"Brave API error: {response.status_code}")
    
    def _search_google(self, query: str, count: int, country: str) -> Dict[str, Any]:
        """Search using Google Custom Search API"""
        params = {
            "key": self.google_api_key,
            "cx": self.google_cx,
            "q": query,
            "num": min(count, 10),  # Google free tier limit per request
            "gl": country.lower(),  # Country code
            "lr": "lang_en",  # Language restriction
            "safe": "medium",  # Safe search
            "fields": "items(title,link,snippet,displayLink)"
        }
        
        response = requests.get(
            self.google_base_url,
            params=params,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return self._format_google_results(data, query)
        elif response.status_code == 403:
            raise Exception("Google API quota exceeded or invalid API key")
        else:
            raise Exception(f"Google API error: {response.status_code}")
    
    def _format_brave_results(self, raw_data: Dict, query: str) -> Dict[str, Any]:
        """Format Brave Search API response"""
        results = []
        
        if "web" in raw_data and "results" in raw_data["web"]:
            for item in raw_data["web"]["results"]:
                result = {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "description": item.get("description", ""),
                    "published": item.get("age", ""),
                    "snippet": item.get("extra_snippets", [])
                }
                results.append(result)
        
        return {
            "query": query,
            "total_results": len(results),
            "results": results,
            "success": True,
            "provider": "brave"
        }
    
    def _format_google_results(self, raw_data: Dict, query: str) -> Dict[str, Any]:
        """Format Google Custom Search API response"""
        results = []
        
        if "items" in raw_data:
            for item in raw_data["items"]:
                result = {
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "description": item.get("snippet", ""),
                    "published": "",  # Google doesn't provide publish date in basic response
                    "snippet": [],
                    "domain": item.get("displayLink", "")
                }
                results.append(result)
        
        return {
            "query": query,
            "total_results": len(results),
            "results": results,
            "success": True,
            "provider": "google"
        }
    
    def quick_search(self, query: str, max_results: int = 5, provider: Optional[str] = None) -> str:
        """
        Perform a quick search and return formatted text summary
        
        Args:
            query: Search query
            max_results: Maximum number of results to include
            provider: Specific provider to use
            
        Returns:
            Formatted string with search results
        """
        search_result = self.search(query, count=max_results, provider=provider)
        
        if search_result.get("error"):
            return f"❌ Search Error: {search_result['error']}"
        
        if not search_result.get("results"):
            return f"🔍 No results found for: {query}"
        
        # Create a conversational response
        results = search_result["results"][:max_results]
        provider_name = search_result.get("provider", "unknown").title()
        
        formatted = f"I found {len(results)} result(s) for '{query}' using {provider_name} Search:\n\n"
        
        if search_result.get("fallback_used"):
            formatted += f"⚠️ Primary provider failed, using {provider_name} as fallback\n\n"
        
        for i, result in enumerate(results, 1):
            title = result['title']
            url = result['url']
            description = result['description'][:200]
            
            formatted += f"{i}. **{title}**\n"
            formatted += f"   🔗 {url}\n"
            formatted += f"   📝 {description}{'...' if len(result['description']) > 200 else ''}\n\n"
        
        return formatted
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all search providers"""
        status = {
            "available_providers": self.providers,
            "primary_provider": self.primary_provider,
            "providers_configured": {
                "brave": bool(self.brave_api_key),
                "google": bool(self.google_api_key and self.google_cx)
            }
        }
        return status

# Backward compatibility - alias for existing code
class WebSearcher(MultiSearcher):
    """Backward compatible alias for MultiSearcher"""
    pass

def demo_multi_search():
    """Demo the multi-provider search capabilities"""
    print("🔍 Multi-Provider Search Demo")
    print("=" * 40)
    
    searcher = MultiSearcher()
    
    if not searcher.providers:
        print("❌ No search providers configured.")
        print("\n📝 Setup Instructions:")
        print("\n🔍 Brave Search API:")
        print("   1. Get free API key: https://api.search.brave.com/app/keys")
        print("   2. Add to .env: BRAVE_SEARCH_API_KEY=your_key_here")
        print("\n🔍 Google Custom Search API:")
        print("   1. Enable Custom Search API: https://console.developers.google.com/")
        print("   2. Create Custom Search Engine: https://cse.google.com/")
        print("   3. Add to .env:")
        print("      GOOGLE_SEARCH_API_KEY=your_api_key")
        print("      GOOGLE_SEARCH_CX=your_search_engine_id")
        return
    
    # Test search with primary provider
    print(f"🔍 Testing search with primary provider: {searcher.primary_provider}")
    result = searcher.quick_search("AI programming tutorial", max_results=3)
    print(result)
    
    # Test provider-specific searches if multiple available
    if len(searcher.providers) > 1:
        print("\n" + "="*40)
        for provider in searcher.providers:
            print(f"\n🔍 Testing {provider.title()} Search specifically:")
            result = searcher.quick_search("Python best practices", max_results=2, provider=provider)
            print(result[:300] + "..." if len(result) > 300 else result)

if __name__ == "__main__":
    demo_multi_search()
