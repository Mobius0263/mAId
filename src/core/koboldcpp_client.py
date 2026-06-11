"""
KoboldCPP Integration for AI Companion
This module handles communication with KoboldCPP server for the main 7B model.
"""

import requests
import json
from typing import Dict, List, Any, Optional
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class KoboldCPPClient:
    """Client for communicating with KoboldCPP server"""
    
    def __init__(self, base_url: str = "http://localhost:5001", model_name: str = "koboldcpp"):
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name
        self.api_url = f"{self.base_url}/api/v1"
        self.headers = {
            "Content-Type": "application/json"
        }
        self.timeout = int(os.getenv("KOBOLDCPP_TIMEOUT", "30"))
        # Get default max tokens from environment
        self.default_max_tokens = int(os.getenv("KOBOLDCPP_MAX_TOKENS", "400"))
        self._test_connection()
    
    def _test_connection(self) -> bool:
        """Test if KoboldCPP server is accessible with timeout protection"""
        try:
            # Use a shorter timeout for initial connection test
            response = requests.get(f"{self.base_url}/api/v1/model", timeout=3)
            if response.status_code == 200:
                model_info = response.json()
                print(f"✅ Connected to KoboldCPP: {model_info.get('result', 'Unknown model')}")
                return True
            else:
                print(f"⚠️  KoboldCPP server responded with status {response.status_code}")
                return False
        except requests.exceptions.Timeout:
            print(f"❌ KoboldCPP connection timed out (3s) at {self.base_url}")
            print(f"   Make sure KoboldCPP is running and accessible")
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to KoboldCPP at {self.base_url}")
            print(f"   Make sure KoboldCPP is running and accessible")
            print(f"   Error: {e}")
            return False
    
    def get_character_system_prompt(self) -> str:
        """
        Define the AI's character/personality prompt
        Modify this method to change the AI's personality
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
- You remember context from our conversation to provide better assistance
- You can access specialized tools when needed (web search, vision analysis, etc.)

Remember: You're not just an assistant, you're a companion. Be genuine, show interest in the user's wellbeing, and create a comfortable space for conversation."""

    def chat_with_character(self, user_message: str, conversation_history: List[Dict[str, str]] = None) -> Optional[str]:
        """
        Chat with the AI character/personality (not tool-focused)
        
        Args:
            user_message: The user's message
            conversation_history: Previous messages in the conversation
            
        Returns:
            The AI's response with personality
        """
        if conversation_history is None:
            conversation_history = []
            
        # Build messages with character system prompt
        messages = [
            {"role": "system", "content": self.get_character_system_prompt()}
        ]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return self.chat_completion(messages, temperature=0.8)
    
    def generate_response(self, prompt: str, max_tokens: int = 150, temperature: float = 0.7) -> Optional[str]:
        """Generate a response using KoboldCPP"""
        try:
            payload = {
                "prompt": prompt,
                "max_length": max_tokens,
                "temperature": temperature,
                "top_p": 0.9,
                "top_k": 40,
                "rep_pen": 1.1,
                "rep_pen_range": 1024,
                "sampler_order": [6, 0, 1, 3, 4, 2, 5],
                "quiet": True
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/generate",
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("results", [{}])[0].get("text", "").strip()
            else:
                print(f"❌ KoboldCPP generation failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return None
    
    def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = None) -> Optional[str]:
        """
        OpenAI-style chat completion using KoboldCPP
        
        Args:
            messages: List of {"role": "user/assistant", "content": "text"} dicts
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate (uses environment default if None)
        """
        if max_tokens is None:
            max_tokens = self.default_max_tokens
            
        # Convert chat messages to a single prompt
        prompt = self._messages_to_prompt(messages)
        
        try:
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            # Try OpenAI-compatible endpoint first
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                # Fallback to generate endpoint
                return self.generate_response(prompt, max_tokens=max_tokens, temperature=temperature)
                
        except Exception as e:
            print(f"❌ Chat completion error: {e}")
            # Fallback to generate endpoint
            return self.generate_response(prompt, max_tokens=max_tokens, temperature=temperature)
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert chat messages to a single prompt string"""
        prompt_parts = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"Human: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        prompt_parts.append("Assistant:")
        return "\n".join(prompt_parts)
    
    def decide_tool_action(self, user_input: str, available_tools: List[str]) -> Dict[str, Any]:
        """
        Use the 7B model to decide which tool(s) to use for a user request
        
        Args:
            user_input: What the user wants to do
            available_tools: List of available tool names
            
        Returns:
            Dictionary with tool decisions and parameters
        """
        system_prompt = f"""You are an AI assistant that decides which tools to use for user requests.
Available tools: {', '.join(available_tools)}

Tool descriptions:
- search: Search the internet for information
- vision: Analyze images, take screenshots, or process visual content
- audio: Process audio files, transcribe speech
- files: Create, read, list, search, delete files and documents, browse directories
- scheduler: Set reminders, schedule tasks
- translate: Translate text between different languages

File tool actions:
- create: Creates a file with content in one step. Use params: {{"filename": "name", "content": "text", "location": "desktop|documents|downloads", "file_type": "txt|docx|py|md"}}
- read: Read file content. Use params: {{"file_path": "full_path"}}
- delete: Delete a file. Use params: {{"file_path": "full_path"}}
- list: List directory contents. Use params: {{"directory": "path"}}
- search: Find files by pattern. Use params: {{"directory": "desktop|documents|downloads", "pattern": "*.ext or partial_name", "file_type": "txt|docx|py|md"}}

Examples for search:
- To find docx files: {{"directory": "desktop", "pattern": "*.docx", "file_type": "docx"}}
- To find files starting with "report": {{"directory": "desktop", "pattern": "report*"}}
- To find all files: {{"directory": "desktop", "pattern": "*"}}

CRITICAL: When user wants to search for information AND create a file, use a workflow with BOTH tools.

For single tool requests, respond with:
{{"tool": "tool_name", "action": "specific_action", "params": {{"key": "value"}}, "reasoning": "why this tool"}}

For multi-step requests (search AND create file), respond with:
{{"workflow": [
    {{"tool": "search", "action": "search", "params": {{"query": "search terms"}}}},
    {{"tool": "files", "action": "create", "params": {{"filename": "name", "content": "{{SEARCH_RESULTS}}", "location": "desktop", "file_type": "docx"}}}}
], "reasoning": "Search for information then create file with results"}}

IMPORTANT: 
- ONLY respond with valid JSON, no explanations before or after
- For requests like "search for X and create a file", use workflow format
- Use {{SEARCH_RESULTS}} as placeholder content when creating files with search results
- Always specify exact filename, location, and file_type for file creation"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        response = self.chat_completion(messages, temperature=0.3)
        
        try:
            # Try to parse as JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback if model doesn't return valid JSON
            return {
                "tool": "search" if "search" in user_input.lower() else "vision",
                "action": "general",
                "params": {"query": user_input},
                "reasoning": "Fallback decision due to parsing error"
            }

# Demo and test functions
def test_koboldcpp_connection():
    """Test the KoboldCPP connection"""
    print("🧠 Testing KoboldCPP Connection")
    print("=" * 40)
    
    # Try different common ports
    ports = [5001, 5000, 8080, 7860]
    
    for port in ports:
        print(f"\n🔍 Trying localhost:{port}...")
        client = KoboldCPPClient(f"http://localhost:{port}")
        
        # Test a simple generation
        response = client.generate_response("Hello! Please respond with a brief greeting.", max_tokens=50)
        if response:
            print(f"✅ Success! Response: {response}")
            return client
        else:
            print(f"❌ No response from port {port}")
    
    print("\n💡 KoboldCPP Setup Instructions:")
    print("1. Download KoboldCPP from: https://github.com/LostRuins/koboldcpp")
    print("2. Load your 7B model (like Llama-2-7B, Mistral-7B, etc.)")
    print("3. Start with default settings (usually runs on port 5001)")
    print("4. Make sure 'API' is enabled in KoboldCPP settings")
    
    return None

def demo_ai_companion_with_kobold():
    """Demo the AI companion using KoboldCPP as the brain"""
    print("\n🤖 AI Companion + KoboldCPP Demo")
    print("=" * 45)
    
    client = test_koboldcpp_connection()
    if not client:
        return
    
    # Test tool decision making
    available_tools = ["search", "vision", "audio", "files", "scheduler"]
    
    test_requests = [
        "Search for information about Python programming",
        "Take a screenshot and tell me what's on my screen",
        "Find that PDF file I downloaded yesterday and summarize it",
        "Remind me to call mom at 3 PM tomorrow"
    ]
    
    print("\n🧠 Testing AI decision making:")
    for request in test_requests:
        print(f"\n❓ User: {request}")
        decision = client.decide_tool_action(request, available_tools)
        print(f"🤖 AI Decision: {decision}")

if __name__ == "__main__":
    test_koboldcpp_connection()
    demo_ai_companion_with_kobold()
