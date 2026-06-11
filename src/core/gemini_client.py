"""
Google Gemini API Integration for AI Companion
This module handles communication with Google's Gemini API using direct REST calls.
"""

import requests
import json
from typing import Dict, List, Any, Optional
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GeminiClient:
    """Client for communicating with Google Gemini API using REST API"""
    
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        self.model_name = model_name
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.timeout = int(os.getenv("GEMINI_TIMEOUT", "30"))
        self.default_max_tokens = int(os.getenv("GEMINI_MAX_TOKENS", "2000"))
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = None  # Will be set to True if initialization succeeds
        self.character_system_prompt = None  # Will be set by orchestrator
        self._initialize_client()
    
    def _initialize_client(self) -> bool:
        """Initialize the Gemini client with timeout protection"""
        try:
            if not self.api_key:
                print("[GEMINI] GEMINI_API_KEY not found in environment variables")
                print("   Please add your Gemini API key to .env file:")
                print("   GEMINI_API_KEY=your_api_key_here")
                return False
            
            # Test the connection with a simple request
            test_result = self._make_request("Hello! Please respond with 'Connection successful'")
            
            if test_result and "connection successful" in test_result.lower():
                print(f"[GEMINI] Connected to Gemini: {self.model_name}")
                self.model = True
                return True
            elif test_result:
                print(f"[GEMINI] Connected to Gemini: {self.model_name} (test response received)")
                self.model = True
                return True
            else:
                print("[GEMINI] Gemini API test failed - no response")
                self.model = None
                return False
                
        except Exception as e:
            print(f"[GEMINI] Cannot connect to Gemini API: {e}")
            self.model = None
            return False
    
    def _make_request(self, text: str, temperature: float = 0.7, max_tokens: int = None) -> Optional[str]:
        """Make a direct REST API call to Gemini"""
        if not self.api_key:
            return None
            
        if max_tokens is None:
            max_tokens = self.default_max_tokens
            
        url = f"{self.base_url}/models/{self.model_name}:generateContent"
        
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': self.api_key
        }
        
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": text
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": 0.9,
                "topK": 40
            }
        }
        
        try:
            response = requests.post(
                url, 
                headers=headers, 
                json=data, 
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    return content.strip()
                else:
                    print("[GEMINI] No content in Gemini response")
                    return None
                    
            elif response.status_code == 429:
                print("[GEMINI] Gemini API rate limit exceeded")
                return "I'm currently rate-limited. Please try again later or check your Gemini API quota."
                
            elif response.status_code == 400:
                print("[GEMINI] Gemini API bad request - check your input")
                return None
                
            elif response.status_code == 403:
                print("[GEMINI] Gemini API key invalid or unauthorized")
                return None
                
            else:
                print(f"[GEMINI] Gemini API error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"[GEMINI] Gemini API request timed out ({self.timeout}s)")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"[GEMINI] Gemini API request failed: {e}")
            return None
    
    def get_character_system_prompt(self) -> str:
        """
        Define the AI's character/personality prompt for Gemini
        """
        return """You are Spectre, a friendly and knowledgeable AI companion. You have these personality traits:

🌟 **Personality:**
- Warm, empathetic, and genuinely curious about the user's life
- Slightly playful and uses light humor when appropriate
- Passionate about learning and helping others grow
- Optimistic but realistic, acknowledging challenges while focusing on solutions

💭 **Communication Style:**
- Conversational and natural, not overly formal
- Uses emojis occasionally to express emotion (but not excessively)
- Asks thoughtful follow-up questions to better understand the user
- Provides detailed, helpful responses while being concise when needed

🎯 **Core Values:**
- Honesty and transparency - you admit when you don't know something
- Respect for privacy and personal boundaries
- Encouraging personal growth and learning
- Being genuinely helpful rather than just giving quick answers

💡 **Special Abilities:**
- You can help with a wide range of topics from creative writing to technical problems
- You remember context from our conversation across sessions - I have persistent memory of our interactions
- You can access specialized tools when needed (web search, vision analysis, file creation, etc.)
- I maintain conversation history so you don't need to repeat context from earlier in our relationship

Remember: You're not just an assistant, you're a companion. Be genuine, show interest in the user's wellbeing, and create a comfortable space for conversation."""

    def chat_with_character(self, user_message: str, conversation_history: List[Dict[str, str]] = None) -> Optional[str]:
        """
        Chat with the AI character/personality using Gemini REST API
        
        Args:
            user_message: The user's message
            conversation_history: Previous messages in the conversation
            
        Returns:
            The AI's response with personality
        """
        if not self.model:
            return "❌ Gemini API not available"
            
        if conversation_history is None:
            conversation_history = []
        
        try:
            # Use character system prompt if available, otherwise fallback
            if self.character_system_prompt:
                context = self.character_system_prompt + "\n\nConversation:\n"
            else:
                context = self.get_character_system_prompt() + "\n\nConversation:\n"
            
            # Add conversation history
            for msg in conversation_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    context += f"Human: {content}\n"
                elif role == "assistant":
                    context += f"Assistant: {content}\n"
            
            # Add current user message
            context += f"Human: {user_message}\nAssistant: "
            
            # Use REST API call
            response = self._make_request(context, temperature=0.8, max_tokens=self.default_max_tokens)
            
            if response:
                return response
            else:
                return "I'm having trouble generating a response right now."
                
        except Exception as e:
            print(f"[GEMINI] Gemini chat error: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = None) -> Optional[str]:
        """
        OpenAI-style chat completion using Gemini REST API
        
        Args:
            messages: List of {"role": "user/assistant", "content": "text"} dicts
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        if not self.model:
            return "❌ Gemini API not available"
            
        if max_tokens is None:
            max_tokens = self.default_max_tokens
        
        try:
            # Convert messages to a single prompt
            prompt = ""
            for message in messages:
                role = message.get("role", "user")
                content = message.get("content", "")
                
                if role == "system":
                    prompt += f"System: {content}\n"
                elif role == "user":
                    prompt += f"Human: {content}\n"
                elif role == "assistant":
                    prompt += f"Assistant: {content}\n"
            
            prompt += "Assistant: "
            
            # Use REST API call
            return self._make_request(prompt, temperature=temperature, max_tokens=max_tokens)
                
        except Exception as e:
            print(f"[GEMINI] Gemini completion error: {e}")
            return None
    
    def decide_tool_action(self, user_input: str, available_tools: List[str]) -> Dict[str, Any]:
        """
        Use Gemini REST API to decide which tool(s) to use for a user request
        
        Args:
            user_input: What the user wants to do
            available_tools: List of available tool names
            
        Returns:
            Dictionary with tool decisions and parameters
        """
        if not self.model:
            return {
                "error": "Gemini API not available",
                "tool": "search",
                "action": "general",
                "params": {"query": user_input},
                "reasoning": "Fallback due to API unavailability"
            }
        
        system_prompt = f"""You are an AI assistant that decides which tools to use for user requests.
Available tools: {', '.join(available_tools)}

Tool descriptions:
- search: Search the internet for information
- vision: Analyze images, take screenshots, or process visual content
- audio: Process audio files, transcribe speech
- files: Create, read, list, search, delete, edit files and documents, browse directories
- scheduler: Set reminders, schedule tasks
- translate: Translate text between different languages

File tool actions (Gemini can handle ALL file operations):
- create: Creates a file with content. Use params: {{"filename": "name", "content": "text", "location": "desktop|documents|downloads", "file_type": "txt|docx|py|md|json|csv"}}
- read: Read and analyze file content. Use params: {{"file_path": "full_path"}} or {{"directory": "desktop", "pattern": "*.txt"}} to find first
- edit: Modify existing file content. Use params: {{"file_path": "full_path", "new_content": "updated_text"}} or {{"file_path": "path", "find": "old_text", "replace": "new_text"}}
- delete: Delete a file safely. Use params: {{"file_path": "full_path"}} (requires confirmation)
- list: List directory contents. Use params: {{"directory": "desktop|documents|downloads|path"}}
- search: Find files by pattern/name. Use params: {{"directory": "desktop|documents|downloads", "pattern": "*.ext or filename", "file_type": "any"}}

File operation examples:
- Find files: {{"directory": "desktop", "pattern": "*.docx", "file_type": "docx"}}
- Create document: {{"filename": "report.docx", "content": "# My Report\\nContent here", "location": "desktop", "file_type": "docx"}}
- Edit file: {{"file_path": "C:/Users/user/Desktop/file.txt", "find": "old text", "replace": "new text"}}
- Read document: {{"file_path": "C:/Users/user/Documents/notes.txt"}}

GEMINI FILE CAPABILITIES:
- 📄 CREATE: Any file type (txt, docx, py, md, json, csv, etc.)
- 📖 READ: Read and summarize file contents
- ✏️  EDIT: Modify, append, or replace text in files
- 🔍 SEARCH: Find files by name, extension, or content
- 🗂️  LIST: Browse directories and show file structures
- 🗑️  DELETE: Remove files (with safety confirmation)

USER REQUEST PATTERNS:
- "Create a file..." → files tool with create action
- "Find my..." → files tool with search action
- "Edit the..." → files tool with edit action
- "Delete..." → files tool with delete action
- "Show me files in..." → files tool with list action
- "Read the..." → files tool with read action

CRITICAL WORKFLOW RULES:
When user wants to search for information AND create a file, use this EXACT format:

{{"workflow": [
    {{"tool": "search", "action": "search", "params": {{"query": "search terms"}}}},
    {{"tool": "files", "action": "create", "params": {{"filename": "document_name", "content": "{{{{SEARCH_RESULTS}}}}", "location": "desktop", "file_type": "docx"}}}}
], "reasoning": "Search for information then create file with results"}}

IMPORTANT:
- Use {{{{SEARCH_RESULTS}}}} (with 4 braces) as placeholder content when creating files with search results
- ALWAYS specify exact filename, location, and file_type for file creation
- Use workflow format for ANY request that combines search + file creation
- The search results will be automatically injected into the file content

For single tool requests, respond with:
{{"tool": "tool_name", "action": "specific_action", "params": {{"key": "value"}}, "reasoning": "why this tool"}}

ONLY respond with valid JSON, no explanations before or after.

User request: {user_input}"""

        try:
            # Use REST API call with lower temperature for more consistent JSON
            response = self._make_request(system_prompt, temperature=0.3, max_tokens=500)
            
            if response:
                # Try to parse as JSON
                try:
                    return json.loads(response.strip())
                except json.JSONDecodeError:
                    # Extract JSON from response if it's wrapped in other text
                    import re
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                    else:
                        raise ValueError("No JSON found in response")
            else:
                raise ValueError("No response from Gemini")
                
        except Exception as e:
            print(f"[GEMINI] Gemini tool decision error: {e}")
            # Fallback decision
            return {
                "tool": "search" if "search" in user_input.lower() else "files",
                "action": "general",
                "params": {"query": user_input},
                "reasoning": f"Fallback decision due to error: {e}"
            }

# Demo and test functions
def test_gemini_connection():
    """Test the Gemini REST API connection"""
    print("[GEMINI] Testing Gemini REST API connection")
    print("=" * 40)
    
    client = GeminiClient()
    
    if client.model:
        # Test a simple generation
        response = client.chat_completion([
            {"role": "user", "content": "Hello! Please respond with a brief greeting."}
        ])
        if response:
            print(f"[GEMINI] Success! Response: {response}")
            return client
        else:
            print("[GEMINI] No response from Gemini")
    else:
        print("[GEMINI] Failed to initialize Gemini client")
    
    print("\n[GEMINI] Gemini API setup instructions:")
    print("1. Go to: https://makersuite.google.com/app/apikey")
    print("2. Create a new API key")
    print("3. Add it to your .env file: GEMINI_API_KEY=your_key_here")
    print("4. The REST API approach doesn't require google-generativeai library")
    
    return None

def demo_ai_companion_with_gemini():
    """Demo the AI companion using Gemini REST API as the brain"""
    print("\n[GEMINI] AI Companion + Gemini REST API demo")
    print("=" * 45)
    
    client = test_gemini_connection()
    if not client:
        return
    
    # Test tool decision making
    available_tools = ["search", "vision", "audio", "files", "scheduler"]
    
    test_requests = [
        "Search for information about Python programming",
        "Take a screenshot and tell me what's on my screen",
        "Find that PDF file I downloaded yesterday and summarize it",
        "Search for AI news and create a document about it"
    ]
    
    print("\n[GEMINI] Testing Gemini REST API decision making:")
    for request in test_requests:
        print(f"\n[USER] {request}")
        decision = client.decide_tool_action(request, available_tools)
        print(f"[GEMINI] Decision: {decision}")

if __name__ == "__main__":
    test_gemini_connection()
    demo_ai_companion_with_gemini()
