"""
Web Search Tool - Brave Search API Implementation
This tool handles internet searches using the Brave Search API.
"""

import os
import requests
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WebSearcher:
    """Handles web searches using Brave Search API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("BRAVE_SEARCH_API_KEY")
        print(f"[DEBUG] WebSearcher - API key loaded: {'Yes' if self.api_key else 'No'}")
        if self.api_key:
            print(f"[DEBUG] WebSearcher - API key length: {len(self.api_key)} characters")
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip"
        }
        if self.api_key:
            # Brave Search API uses X-Subscription-Token header
            self.headers["X-Subscription-Token"] = self.api_key
            print(f"[DEBUG] WebSearcher - Header set: X-Subscription-Token")
    
    def search(self, query: str, count: int = 10, country: str = "US") -> Dict[str, Any]:
        """
        Perform a web search
        
        Args:
            query: Search query string
            count: Number of results to return (max 20 for free tier)
            country: Country code for localized results
            
        Returns:
            Dictionary containing search results and metadata
        """
        if not self.api_key:
            return {
                "error": "No API key configured. Set BRAVE_SEARCH_API_KEY environment variable.",
                "results": []
            }
        
        try:
            params = {
                "q": query,
                "count": min(count, 20),  # Free tier limit
                "country": country,
                "search_lang": "en",
                "ui_lang": "en-US",  # Fixed: Use full locale format
                "freshness": "pw"  # Past week for fresh results
            }
            
            # Debug: Only show URL and key params for search requests  
            print(f"[DEBUG] Search: '{query}' -> {self.base_url}")
            
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            print(f"[DEBUG] Search API response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                return self._format_results(data, query)
            else:
                error_details = ""
                try:
                    error_data = response.json()
                    error_details = f" - {error_data}"
                except:
                    error_details = f" - {response.text[:200]}"
                
                print(f"[DEBUG] Search API error: {response.status_code}{error_details}")
                return {
                    "error": f"API request failed with status {response.status_code}{error_details}",
                    "results": []
                }
                
        except Exception as e:
            return {
                "error": f"Search failed: {str(e)}",
                "results": []
            }
    
    def _format_results(self, raw_data: Dict, query: str) -> Dict[str, Any]:
        """Format the raw API response into a clean structure"""
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
            "success": True
        }
    
    def quick_search(self, query: str, max_results: int = 5) -> str:
        """
        Perform a quick search and return formatted text summary
        
        Args:
            query: Search query
            max_results: Maximum number of results to include
            
        Returns:
            Formatted string with search results
        """
        search_result = self.search(query, count=max_results)
        
        if search_result.get("error"):
            return f"❌ Search Error: {search_result['error']}"
        
        if not search_result.get("results"):
            return f"🔍 No results found for: {query}"
        
        # Create a more conversational response
        results = search_result["results"][:max_results]
        
        formatted = f"I found {len(results)} result(s) for '{query}':\n\n"
        
        for i, result in enumerate(results, 1):
            title = result['title']
            url = result['url']
            description = result['description'][:200]
            
            formatted += f"{i}. **{title}**\n"
            formatted += f"   🔗 {url}\n"
            formatted += f"   📝 {description}{'...' if len(result['description']) > 200 else ''}\n\n"
        
        return formatted

# Demo function
def demo_web_search():
    """Demo the web search capabilities"""
    print("🔍 Web Search Demo")
    print("=" * 30)
    
    searcher = WebSearcher()
    
    if not searcher.api_key:
        print("❌ No Brave Search API key configured.")
        print("📝 To get started:")
        print("   1. Get a free API key: https://api.search.brave.com/app/keys")
        print("   2. Copy .env.example to .env")
        print("   3. Add your API key to the .env file")
        return
    
    # Test search
    print("🔍 Testing search for 'AI companion local models'...")
    result = searcher.quick_search("AI companion local models", max_results=3)
    print(result)

if __name__ == "__main__":
    demo_web_search()
