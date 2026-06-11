"""
AI Companion Orchestrator - Redesigned
Intelligent, character-driven AI coordination system
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from core.memory_manager import get_memory_manager
from core.character_system import get_character_manager
from core.intelligent_tool_selector import get_tool_selector


class SmartAIOrchestrator:
    """
    Redesigned orchestrator with character system and intelligent tool selection
    """
    
    def __init__(self):
        """Initialize the smart orchestrator"""
        self.tools = {}
        self.brain = None  # AI client for reasoning
        self.memory_manager = get_memory_manager()
        self.character_manager = get_character_manager()
        self.tool_selector = get_tool_selector()
        
        print("[SMART] Initializing AI Companion with character system...")
        self._load_tools()
        self._load_brain()
        
        # Display character info
        char_info = self.character_manager.get_character_info()
        print(f"[CHARACTER] Active: {char_info.get('name', 'Unknown')}")
    
    def _load_brain(self):
        """Load the AI brain with character-aware system prompt"""
        print("[SMART] Loading AI brain...")
        
        # Try Gemini first
        try:
            from core.gemini_client import GeminiClient
            self.brain = GeminiClient()
            
            # Set character-aware system prompt
            character_prompt = self.character_manager.get_system_prompt()
            self.brain.character_system_prompt = character_prompt
            
            print("[SMART] Gemini brain loaded with character system")
            return
        except Exception as e:
            print(f"[SMART] Gemini failed: {e}")
        
        # Try KoboldCPP as fallback
        try:
            from core.koboldcpp_client import KoboldCPPClient
            self.brain = KoboldCPPClient()
            print("[SMART] KoboldCPP brain loaded as fallback")
        except Exception as e:
            print(f"[SMART] KoboldCPP failed: {e}")
            print("[SMART] No AI brain available")
    
    def _load_tools(self):
        """Load available tools - Updated with PyGPT feature set"""
        print("[SMART] Loading PyGPT-enhanced tool suite...")
        
        # Web Search tool (existing)
        try:
            from tools.search.multi_searcher import MultiSearcher
            searcher = MultiSearcher()
            self.tools["search"] = searcher
            providers = searcher.get_available_providers() if hasattr(searcher, 'get_available_providers') else ["Available"]
            print(f"[SMART] Web Search: {', '.join(providers)}")
        except Exception as e:
            print(f"[SMART] Search tool failed: {e}")
        
        # Enhanced Files I/O Manager
        try:
            from tools.files.enhanced_file_io import AdvancedFileManager
            self.tools["files"] = AdvancedFileManager()
            print("[SMART] Enhanced File I/O loaded")
        except Exception as e:
            print(f"[SMART] Enhanced file I/O failed: {e}")
        
        # Chat With Files Manager
        try:
            from tools.files.chat_with_files import ChatWithFilesManager
            self.tools["chat_files"] = ChatWithFilesManager()
            print("[SMART] Chat With Files loaded")
        except Exception as e:
            print(f"[SMART] Chat With Files failed: {e}")
        
        # Enhanced Vision System
        try:
            from tools.vision.enhanced_vision import EnhancedVisionSystem
            self.tools["vision"] = EnhancedVisionSystem()
            print("[SMART] Enhanced Vision System loaded")
        except Exception as e:
            print(f"[SMART] Enhanced Vision not available: {e}")
        
        # Audio Processing System
        try:
            from tools.audio.audio_processor import AudioProcessor
            self.tools["audio"] = AudioProcessor()
            print("[SMART] Audio Processing loaded")
        except Exception as e:
            print(f"[SMART] Audio Processing failed: {e}")
        
        # Code Interpreter
        try:
            from tools.code.code_interpreter import CodeInterpreter
            self.tools["code"] = CodeInterpreter()
            print("[SMART] Code Interpreter loaded")
        except Exception as e:
            print(f"[SMART] Code Interpreter failed: {e}")
        
        # Document Processor
        try:
            from tools.documents.document_processor import DocumentProcessor
            self.tools["documents"] = DocumentProcessor()
            print("[SMART] Document Processor loaded")
        except Exception as e:
            print(f"[SMART] Document Processor failed: {e}")
        
        # API Integrations Manager
        try:
            from tools.api.api_integrations import APIIntegrationManager
            self.tools["api"] = APIIntegrationManager()
            print("[SMART] API Integrations loaded")
        except Exception as e:
            print(f"[SMART] API Integrations failed: {e}")
        
        # Multi-Model Manager
        try:
            from tools.models.multi_model_manager import MultiModelManager
            self.tools["models"] = MultiModelManager()
            print("[SMART] Multi-Model Manager loaded")
        except Exception as e:
            print(f"[SMART] Multi-Model Manager failed: {e}")
        
        print(f"[SMART] PyGPT Tool Suite: {len(self.tools)} tools loaded")
    
    def process_user_request(self, user_input: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Process user request with intelligent tool selection and character awareness
        
        Args:
            user_input: User's message
            conversation_history: Previous conversation context
            
        Returns:
            Response with tool results or character conversation
        """
        
        if not self.brain:
            return {
                "error": "AI brain not available",
                "response": "I'm sorry, but my AI brain isn't available right now. Please check the configuration."
            }
        
        try:
            # Step 1: Analyze user intent with AI reasoning
            tool_analysis = self._analyze_intent_with_ai(user_input, conversation_history)
            
            # Step 2: Execute based on analysis
            if tool_analysis.get("selected_tool") == "character_chat":
                # Pure conversation
                return self._handle_character_conversation(user_input, conversation_history)
            else:
                # Tool-based request
                return self._execute_intelligent_tool_action(tool_analysis, user_input, conversation_history)
                
        except Exception as e:
            print(f"[SMART] Error processing request: {e}")
            return {
                "error": f"Processing error: {e}",
                "response": "I encountered an error while processing your request. Could you try rephrasing it?"
            }
    
    def process_command(self, user_input: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Alias for process_user_request for backwards compatibility
        
        Args:
            user_input: User's message
            conversation_history: Previous conversation context
            
        Returns:
            Response with tool results or character conversation
        """
        return self.process_user_request(user_input, conversation_history)
    
    def _analyze_intent_with_ai(self, user_input: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Use AI to analyze user intent and select appropriate tool"""
        
        # Get tool analysis prompt
        analysis_info = self.tool_selector.analyze_user_intent(user_input, conversation_history)
        analysis_prompt = analysis_info["analysis_prompt"]
        
        # Ask AI to analyze the request
        try:
            if hasattr(self.brain, '_make_request'):
                # Gemini client
                analysis_response = self.brain._make_request(
                    analysis_prompt, 
                    temperature=0.1,  # Low temperature for consistent analysis
                    max_tokens=500
                )
            else:
                # Fallback method
                analysis_response = self.brain.generate_response(analysis_prompt)
            
            # Parse AI response as JSON
            if analysis_response:
                try:
                    # Clean up response and extract JSON
                    response_text = analysis_response.strip()
                    if "```json" in response_text:
                        json_start = response_text.find("```json") + 7
                        json_end = response_text.find("```", json_start)
                        response_text = response_text[json_start:json_end].strip()
                    elif "{" in response_text:
                        json_start = response_text.find("{")
                        json_end = response_text.rfind("}") + 1
                        response_text = response_text[json_start:json_end]
                    
                    analysis_result = json.loads(response_text)
                    print(f"[SMART] Tool analysis: {analysis_result.get('selected_tool')} - {analysis_result.get('reasoning', '')[:100]}...")
                    return analysis_result
                    
                except json.JSONDecodeError as e:
                    print(f"[SMART] JSON parse error: {e}")
                    print(f"[SMART] Raw response: {analysis_response[:200]}...")
                    # Fallback to simple analysis
                    return self._fallback_intent_analysis(user_input)
            else:
                return self._fallback_intent_analysis(user_input)
                
        except Exception as e:
            print(f"[SMART] AI analysis error: {e}")
            return self._fallback_intent_analysis(user_input)
    
    def _fallback_intent_analysis(self, user_input: str) -> Dict[str, Any]:
        """Enhanced fallback intent analysis for PyGPT features"""
        user_lower = user_input.lower()
        
        # Audio processing keywords
        if any(phrase in user_lower for phrase in ["read aloud", "text to speech", "tts", "speak", "voice", "audio file", "transcribe", "speech to text", "stt"]):
            return {
                "selected_tool": "audio",
                "confidence": 0.9,
                "reasoning": "Request involves audio processing (TTS/STT)",
                "user_intent": "Process audio or convert text to speech",
                "parameters": {"text": user_input}
            }
        
        # Code execution keywords
        elif any(phrase in user_lower for phrase in ["run code", "execute", "python code", "javascript", "bash script", "code interpreter"]):
            return {
                "selected_tool": "code",
                "confidence": 0.9,
                "reasoning": "Request involves code execution",
                "user_intent": "Execute or interpret code",
                "parameters": {"code": user_input}
            }
        
        # Document processing keywords
        elif any(phrase in user_lower for phrase in ["pdf", "docx", "word document", "excel", "csv", "powerpoint", "analyze document", "summarize document"]):
            return {
                "selected_tool": "documents",
                "confidence": 0.9,
                "reasoning": "Request involves document processing",
                "user_intent": "Process or analyze documents",
                "parameters": {"query": user_input}
            }
        
        # API integration keywords
        elif any(phrase in user_lower for phrase in ["weather", "news", "github", "currency", "exchange rate", "translate"]):
            return {
                "selected_tool": "api",
                "confidence": 0.8,
                "reasoning": "Request involves external API services",
                "user_intent": "Get information from external APIs",
                "parameters": {"query": user_input}
            }
        
        # Chat with files keywords
        elif any(phrase in user_lower for phrase in ["chat with files", "ask about file", "search in documents", "question about document"]):
            return {
                "selected_tool": "chat_files",
                "confidence": 0.9,
                "reasoning": "Request involves conversing with file contents",
                "user_intent": "Chat with indexed file contents",
                "parameters": {"query": user_input}
            }
        
        # Model switching keywords
        elif any(phrase in user_lower for phrase in ["switch model", "use different model", "change ai model", "gemini", "gpt-4", "claude"]):
            return {
                "selected_tool": "models",
                "confidence": 0.8,
                "reasoning": "Request involves AI model management",
                "user_intent": "Switch or manage AI models",
                "parameters": {"query": user_input}
            }
        
        # File management keywords (enhanced)
        elif (
            any(phrase in user_lower for phrase in [
                "create file", "write file", "save to file", "make a file", "generate file",
                "create document", "write document", "save document", "docx file", "save to desktop",
                "create on desktop", "place it in", "write to", "save as", "export to",
                "create a .docx", "create a .txt", "create a .pdf", "search for files", "find files",
                "downloads folder", "my documents", "compress files", "zip", "backup"
            ])
            or (
                any(word in user_lower for word in ["create", "make", "write", "save", "export", "generate"])
                and any(word in user_lower for word in ["file", "document", "doc", "desktop", "documents", "downloads", ".txt", ".docx", ".pdf", ".md", ".json"])
            )
        ):
            return {
                "selected_tool": "files",
                "confidence": 0.9,
                "reasoning": "Request involves file creation, writing, or management",
                "user_intent": "Create, write, or manage files",
                "parameters": {"query": user_input}
            }
        
        # Web search keywords
        elif any(phrase in user_lower for phrase in ["search for", "look up", "find information", "research"]) and not any(phrase in user_lower for phrase in ["file", "folder", "document"]):
            return {
                "selected_tool": "search", 
                "confidence": 0.8,
                "reasoning": "Request appears to be about web search",
                "user_intent": "Find information online",
                "parameters": {"query": user_input}
            }
        
        # Vision analysis keywords
        elif any(phrase in user_lower for phrase in ["screenshot", "what's on my screen", "image", "picture", "analyze image", "describe photo"]):
            return {
                "selected_tool": "vision",
                "confidence": 0.8,
                "reasoning": "Request involves visual analysis",
                "user_intent": "Analyze visual content",
                "parameters": {}
            }
        
        # Memory keywords
        elif any(phrase in user_lower for phrase in ["memory", "conversation history", "what did we talk", "remember"]):
            return {
                "selected_tool": "memory",
                "confidence": 0.8,
                "reasoning": "Request about conversation memory",
                "user_intent": "Access conversation history",
                "parameters": {}
            }
        
        # Default to character chat
        else:
            return {
                "selected_tool": "character_chat",
                "confidence": 0.7,
                "reasoning": "General conversation or unclear intent",
                "user_intent": "Have a conversation",
                "parameters": {}
            }
    
    def _execute_intelligent_tool_action(self, analysis: Dict[str, Any], user_input: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Execute tool action based on AI analysis - Enhanced for PyGPT features"""
        
        tool_name = analysis.get("selected_tool")
        parameters = analysis.get("parameters", {})
        user_intent = analysis.get("user_intent", "")
        
        try:
            # PyGPT Enhanced Tools
            if tool_name == "audio" and "audio" in self.tools:
                return self._execute_audio_processing(parameters, user_input, user_intent)
            elif tool_name == "code" and "code" in self.tools:
                return self._execute_code_interpreter(parameters, user_input, user_intent)
            elif tool_name == "documents" and "documents" in self.tools:
                return self._execute_document_processing(parameters, user_input, user_intent, conversation_history)
            elif tool_name == "api" and "api" in self.tools:
                return self._execute_api_integration(parameters, user_input, user_intent)
            elif tool_name == "chat_files" and "chat_files" in self.tools:
                return self._execute_chat_with_files(parameters, user_input, user_intent, conversation_history)
            elif tool_name == "models" and "models" in self.tools:
                return self._execute_model_management(parameters, user_input, user_intent)
            
            # Existing Tools (Enhanced)
            elif tool_name == "search" and "search" in self.tools:
                return self._execute_search(parameters, user_input, user_intent, conversation_history)
            elif tool_name == "files" and "files" in self.tools:
                return self._execute_file_operation(parameters, user_input, user_intent, conversation_history)
            elif tool_name == "vision" and "vision" in self.tools:
                return self._execute_vision_analysis(parameters, user_input, user_intent)
            elif tool_name == "memory":
                return self._execute_memory_operation(parameters, user_input, user_intent)
            else:
                # Tool not available or not recognized
                return self._handle_character_conversation(user_input, conversation_history)
                
        except Exception as e:
            print(f"[SMART] Tool execution error: {e}")
            return {
                "error": f"Tool execution failed: {e}",
                "response": f"I tried to {user_intent.lower()}, but encountered an error. Could you try again or rephrase your request?"
            }
    
    def _execute_search(self, parameters: Dict, user_input: str, user_intent: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Execute web search with intelligent handling and context preservation"""
        query = parameters.get("query", user_input)
        
        # Clean up query
        search_query = query.replace("search for", "").replace("look up", "").replace("find information about", "").strip()
        
        print(f"[SMART] Executing search for: {search_query}")
        search_results = self.tools["search"].search(search_query, count=5)
        
        if search_results.get("success") and search_results.get("results"):
            # Format search results for preservation
            formatted_results = self._format_search_results(search_results["results"])
            
            # Build conversation context for better AI response
            full_history = self._build_conversation_context(conversation_history)
            
            # Have AI summarize results with character personality and conversation awareness
            summary_prompt = f"""As {self.character_manager.current_character.name}, provide a comprehensive and helpful response to the user's request: "{user_input}"

**Context from our conversation:**
"""
            
            # Add recent conversation context
            if full_history:
                for msg in full_history[-4:]:  # Last 4 messages for context
                    role = msg.get("role", "user")
                    content = msg.get("content", "")[:200]  # Truncate for efficiency
                    if role == "user":
                        summary_prompt += f"Human: {content}\n"
                    elif role == "assistant":
                        sender = msg.get("sender", "Assistant")
                        summary_prompt += f"{sender}: {content}\n"
                summary_prompt += "\n"
            
            summary_prompt += f"""**Based on these search results, give a detailed answer:**

{formatted_results}

**Instructions:**
- Synthesize information from multiple sources to give a complete answer
- Include specific details, facts, and context that directly answer their question
- Reference the sources when mentioning specific information
- Use your technical expertise to explain complex concepts clearly
- Remember this information for future reference in our conversation
- Structure the response so it can be easily referenced later for document creation or follow-up questions

**Provide a thorough response that can be referred back to:**"""
            
            # Get AI summary with full conversation context
            ai_summary = self._get_ai_response(summary_prompt, full_history)
            
            # Create comprehensive response that preserves search context
            full_response = f"{ai_summary}\n\n---\n**📋 Search Results Summary:**\n{formatted_results}\n\n*This information was found by searching for: \"{search_query}\"*"
            
            return {
                "tool_used": "search",
                "query": search_query,
                "raw_results": search_results["results"],
                "formatted_results": formatted_results,
                "response": full_response,
                "success": True,
                "context_preserved": True  # Flag to indicate this contains searchable context
            }
        else:
            error_msg = search_results.get("error", "No results found")
            return {
                "tool_used": "search",
                "query": search_query,
                "error": error_msg,
                "response": f"I couldn't find information about '{search_query}'. {error_msg}",
                "success": False
            }
    
    def _execute_file_operation(self, parameters: Dict, user_input: str, user_intent: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Execute file operations with intelligent handling"""
        
        # Determine specific file operation
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ["create", "make", "write", "save"]):
            return self._handle_file_creation(user_input, user_intent, conversation_history)
        elif any(word in user_lower for word in ["find", "search", "look for", "locate"]):
            return self._handle_file_search(user_input, user_intent)
        elif any(word in user_lower for word in ["delete", "remove"]):
            return self._handle_file_deletion(user_input, user_intent)
        else:
            # General file management
            return self._handle_general_file_operation(user_input, user_intent)
    
    def _extract_relevant_information_simple(self, conversation_history: List[Dict], user_request: str) -> str:
        """Extract only relevant factual information from conversation"""
        if not conversation_history:
            return user_request
        
        relevant_info = []
        
        for msg in conversation_history[-8:]:  # Look at last 8 messages
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            # Only include user questions and factual search results
            if role == "user" and content and len(content.strip()) > 10:
                relevant_info.append(content)
            elif role == "assistant":
                # Extract factual information from any assistant response
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    # Skip conversational parts but keep factual content
                    if any(phrase in line.lower() for phrase in [
                        "i found", "here's what", "let me", "i can help", 
                        "successfully created", "location:", "based on our"
                    ]):
                        continue
                    
                    # Include lines with factual formatting or technical content
                    if any(indicator in line for indicator in ["**", "##", "###", "-", "•", ":"]) and not line.startswith(("I ", "Here", "Let")):
                        relevant_info.append(line)
        
        return ' '.join(relevant_info) if relevant_info else user_request

    def _extract_relevant_information(self, conversation_history: List[Dict], user_request: str) -> str:
        """Extract the EXACT specifications and data the user wants documented"""
        if not conversation_history:
            return f"User is requesting: {user_request}"
        
        # Extract ALL specification content aggressively
        spec_content = []
        
        for msg in conversation_history[-8:]:  # Focus on recent context
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            # Include user's specific requests for context
            if role == "user" and content and len(content.strip()) > 10:
                if any(word in content.lower() for word in ["specifications", "specs", "details", "information"]):
                    spec_content.append(f"USER WANTS: {content}")
            
            # Extract ALL technical content from assistant responses
            elif role == "assistant" and content:
                lines = content.split('\n')
                
                for line in lines:
                    line = line.strip()
                    
                    # Skip meta-conversation completely
                    if any(phrase in line.lower() for phrase in [
                        "i found", "here's", "let me", "i can", "i'll", "based on", "this information",
                        "search results", "according to", "i apologize", "recently, there"
                    ]):
                        continue
                    
                    # AGGRESSIVELY capture specification data
                    should_include = False
                    
                    # Lines with technical formatting
                    if any(char in line for char in ["•", "-", "**", ":"]) and len(line) > 5:
                        should_include = True
                    
                    # Lines with measurements or technical terms
                    if any(term in line.lower() for term in [
                        "length", "wingspan", "height", "weight", "speed", "range", "engine", "thrust",
                        "maximum", "empty", "fuel", "ceiling", "hardpoints", "guns", "missiles", "radar",
                        "crew", "manufacturer", "avionics", "armament", "weapons", "service", "ceiling"
                    ]):
                        should_include = True
                    
                    # Lines with units or measurements
                    if any(unit in line for unit in [
                        "ft", "m", "kg", "lb", "mph", "km/h", "nm", "mm", "inches", "tons", "kn"
                    ]):
                        should_include = True
                    
                    # Lines with numbers and colons (like "Length: 50 ft")
                    if ":" in line and any(char.isdigit() for char in line):
                        should_include = True
                    
                    # Section headers for specifications
                    if any(header in line.lower() for header in [
                        "specifications", "technical details", "general specifications", 
                        "dimensions", "performance", "armament", "avionics"
                    ]):
                        should_include = True
                    
                    if should_include:
                        spec_content.append(line)
        
        if not spec_content:
            return f"No specific technical data found for: {user_request}"
        
        # Return all the captured specification content
        return '\n'.join(spec_content)

    def _handle_file_creation(self, user_input: str, user_intent: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Handle file creation requests with full conversation context awareness"""
        try:
            import re
            # Parse the user input to extract filename, content, and location
            import re
            import re
            
            # Extract filename from input
            filename_match = re.search(r'(?:file|document)\s+(?:named|called)\s+["\']?([^"\'.\s]+)["\']?', user_input, re.IGNORECASE)
            filename = filename_match.group(1) if filename_match else "document"
            
            # Extract file type
            type_match = re.search(r'\.(docx|txt|md|py|html|json)', user_input, re.IGNORECASE)
            file_type = type_match.group(1) if type_match else "txt"
            
            # If they specified docx, make sure we use that
            if "docx" in user_input.lower():
                file_type = "docx"
            
            # Extract location
            location = "desktop"  # Default
            if "desktop" in user_input.lower():
                location = "desktop"
            elif "documents" in user_input.lower():
                location = "documents"
            elif "downloads" in user_input.lower():
                location = "downloads"
            
            # Build conversation context for content generation
            full_history = self._build_conversation_context(conversation_history)
            
            # Extract relevant information from conversation (exclude AI responses and chat metadata)
            relevant_info = self._extract_relevant_information(full_history, user_input)
            
            # Generate content using AI with clean, focused context
            content_prompt = f"""TASK: Create file content based on: "{user_input}"

CONVERSATION DATA TO USE:
{relevant_info}

CRITICAL INSTRUCTIONS:
1. DO NOT write about what you're going to do - JUST DO IT
2. DO NOT say "This document contains..." - PUT THE ACTUAL CONTENT
3. USE THE EXACT specifications, measurements, and data from the conversation
4. START IMMEDIATELY with the title and then the actual information
5. Include ALL the technical details that were mentioned

EXAMPLE OF WHAT TO DO:
If conversation had "Length: 50 ft, Weight: 1000 lbs" then write:
"# F-22 Specifications
Length: 50 ft  
Weight: 1000 lbs"

NOT: "This document contains the specifications we discussed"

FORMAT: Professional {file_type.upper()} document with the ACTUAL DATA:"""
            
            # Get AI-generated content based on conversation context
            try:
                ai_generated_content = self._get_ai_response(content_prompt, full_history)
                content = ai_generated_content.strip()
                print(f"[SMART] Generated contextual content for file creation")
            except Exception as e:
                print(f"[SMART] Error generating contextual content: {e}")
                # Minimal fallback content if AI generation fails
                content = f"Document created on: {self._get_timestamp()}\n\nContent to be added based on discussion."
            
            # Create the file using FileManager
            result = self.tools["files"].create_file(
                content=content,
                filename=filename,
                location=location,
                file_type=file_type
            )
            
            if result.get("success"):
                file_path = result.get("file_path", "")
                response = f"✅ Successfully created **{filename}.{file_type}** in {location} with content based on our conversation!\n\n📁 **Location:** `{file_path}`\n\n📝 **Content:** The file includes relevant information from our recent discussion and is ready for your review and use."
            else:
                error_msg = result.get("error", "Unknown error")
                response = f"❌ I had trouble creating the file: {error_msg}"
            
            self.memory_manager.save_conversation_turn(user_input, response, {"tool_used": "files", "operation": "create"})
            
            return {
                "tool_used": "files",
                "operation": "create",
                "response": response,
                "details": result
            }
        except Exception as e:
            return {
                "tool_used": "files",
                "error": str(e),
                "response": f"❌ I encountered an error while trying to create the file: {e}"
            }
    
    def _get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _handle_file_search(self, user_input: str, user_intent: str) -> Dict[str, Any]:
        """Handle file search requests"""
        try:
            # Extract search terms from user input
            import re
            import re
            
            # Default search directory (start with user's home directory common folders)
            search_dirs = [
                str(Path.home() / "Desktop"),
                str(Path.home() / "Documents"),
                str(Path.home() / "Downloads")
            ]
            
            # Extract file type if specified
            file_type = None
            if "docx" in user_input.lower():
                file_type = "docx"
            elif ".txt" in user_input.lower():
                file_type = "txt"
            elif ".pdf" in user_input.lower():
                file_type = "pdf"
            
            # Extract filename pattern
            pattern = "*"
            filename_match = re.search(r'(?:named|called)\s+["\']?([^"\'.\s]+)["\']?', user_input, re.IGNORECASE)
            if filename_match:
                pattern = f"*{filename_match.group(1)}*"
            else:
                # Try to extract key terms from the search query
                search_terms = re.findall(r'\b[a-zA-Z]{3,}\b', user_input.lower())
                # Filter out common words
                common_words = {'find', 'search', 'look', 'for', 'files', 'named', 'called', 'document', 'file'}
                key_terms = [term for term in search_terms if term not in common_words]
                if key_terms:
                    pattern = f"*{key_terms[0]}*"
            
            # Search in each directory
            all_files = []
            for directory in search_dirs:
                try:
                    result = self.tools["files"].search_files(directory, pattern, file_type)
                    if result.get("success") and result.get("files"):
                        all_files.extend(result["files"])
                except Exception as e:
                    print(f"[DEBUG] Error searching in {directory}: {e}")
            
            if all_files:
                response = f"🔍 **Found {len(all_files)} file(s) matching your search:**\n\n"
                for i, file_info in enumerate(all_files[:10], 1):  # Limit to 10 results
                    name = file_info.get('name', 'Unknown')
                    path = file_info.get('path', 'Unknown location')
                    size = file_info.get('size', 'Unknown size')
                    response += f"**{i}. {name}**\n"
                    response += f"   📁 Location: `{path}`\n"
                    response += f"   📊 Size: {size}\n\n"
                
                if len(all_files) > 10:
                    response += f"... and {len(all_files) - 10} more files.\n\n"
                
                response += "Would you like me to do anything specific with these files?"
            else:
                response = f"🔍 **No files found** matching your search criteria.\n\nI searched for files with pattern `{pattern}`"
                if file_type:
                    response += f" of type `{file_type}`"
                response += " in common directories (Desktop, Documents, Downloads).\n\nTry:\n• Using different keywords\n• Checking if the file exists in the expected location\n• Searching with a broader pattern"
            
            self.memory_manager.save_conversation_turn(user_input, response, {"tool_used": "files", "operation": "search"})
            
            return {
                "tool_used": "files",
                "operation": "search",
                "response": response,
                "files_found": all_files
            }
        except Exception as e:
            return {
                "tool_used": "files",
                "error": str(e),
                "response": f"❌ I encountered an error while searching for files: {e}"
            }
    
    def _handle_file_deletion(self, user_input: str, user_intent: str) -> Dict[str, Any]:
        """Handle file deletion requests"""
        # Implement safe file deletion with confirmation
        return {
            "tool_used": "files",
            "operation": "delete",
            "response": "File deletion requires confirmation for safety. Please specify exactly which files you want to delete, and I'll ask for confirmation before proceeding."
        }
    
    def _handle_general_file_operation(self, user_input: str, user_intent: str) -> Dict[str, Any]:
        """Handle general file operations"""
        try:
            # Determine the operation based on user input
            user_lower = user_input.lower()
            
            if any(word in user_lower for word in ["list", "show", "directory", "folder"]):
                # List directory contents
                directory = None
                if "desktop" in user_lower:
                    directory = str(Path.home() / "Desktop")
                elif "documents" in user_lower:
                    directory = str(Path.home() / "Documents")
                elif "downloads" in user_lower:
                    directory = str(Path.home() / "Downloads")
                
                result = self.tools["files"].list_directory(directory)
                
                if result.get("success"):
                    files = result.get("files", [])
                    dirs = result.get("directories", [])
                    location = result.get("directory", "current directory")
                    
                    response = f"📁 **Contents of {location}:**\n\n"
                    
                    if dirs:
                        response += "**📂 Folders:**\n"
                        for folder in dirs[:10]:
                            response += f"  📂 {folder}\n"
                        if len(dirs) > 10:
                            response += f"  ... and {len(dirs) - 10} more folders\n"
                        response += "\n"
                    
                    if files:
                        response += "**📄 Files:**\n"
                        for file_info in files[:15]:
                            name = file_info.get('name', 'Unknown')
                            size = file_info.get('size', '')
                            response += f"  📄 {name}"
                            if size:
                                response += f" ({size})"
                            response += "\n"
                        if len(files) > 15:
                            response += f"  ... and {len(files) - 15} more files\n"
                    
                    if not files and not dirs:
                        response += "The directory is empty."
                else:
                    response = f"❌ Could not list directory contents: {result.get('error', 'Unknown error')}"
            
            elif any(word in user_lower for word in ["read", "open", "show content"]):
                response = "To read a file, please specify the exact file path or name. For example: 'read the file example.txt from desktop'"
            
            else:
                # Default response for unclear requests
                response = """I can help you with various file operations:

**File Management:**
- Create files: "Create a docx file named 'Report' on desktop"
- Search files: "Find files named 'hornet' in documents"  
- List directories: "Show me what's in my downloads folder"
- Read files: "Read the content of example.txt"

**What would you like me to do?**"""
            
            self.memory_manager.save_conversation_turn(user_input, response, {"tool_used": "files", "operation": "general"})
            
            return {
                "tool_used": "files",
                "operation": "general",
                "response": response
            }
        except Exception as e:
            return {
                "tool_used": "files",
                "error": str(e),
                "response": f"❌ I encountered an error with the file operation: {e}"
            }
    
    def _execute_vision_analysis(self, parameters: Dict, user_input: str, user_intent: str) -> Dict[str, Any]:
        """Execute vision analysis"""
        try:
            if "screenshot" in user_input.lower():
                result = self.tools["vision"].analyze_screenshot(user_input)
            else:
                result = self.tools["vision"].analyze_image(user_input)
            
            response = result.get("analysis", "I couldn't analyze the visual content.")
            
            self.memory_manager.save_conversation_turn(user_input, response, {"tool_used": "vision"})
            
            return {
                "tool_used": "vision",
                "response": response,
                "details": result
            }
        except Exception as e:
            return {
                "tool_used": "vision",
                "error": str(e),
                "response": f"I couldn't perform visual analysis: {e}"
            }
    
    def _execute_memory_operation(self, parameters: Dict, user_input: str, user_intent: str) -> Dict[str, Any]:
        """Execute memory-related operations"""
        user_lower = user_input.lower()
        
        if "status" in user_lower or "stats" in user_lower:
            stats = self.memory_manager.get_memory_stats()
            response = f"📊 **Memory Status**\n"
            response += f"💭 Total conversations: {stats['total_conversations']}\n"
            response += f"🕒 Recent conversations: {stats['recent_conversations']}\n"
            response += f"🧠 Memory enabled: {'Yes' if stats['memory_enabled'] else 'No'}"
        else:
            # Show conversation history
            history = self.memory_manager.get_conversation_history(limit=6)
            if history:
                response = "Here's what we've been discussing recently:\n\n"
                # Format recent conversations
                for i in range(0, len(history), 2):
                    if i + 1 < len(history):
                        user_msg = history[i]['content'][:100] + ("..." if len(history[i]['content']) > 100 else "")
                        ai_msg = history[i + 1]['content'][:100] + ("..." if len(history[i + 1]['content']) > 100 else "")
                        response += f"**You:** {user_msg}\n**Me:** {ai_msg}\n\n"
            else:
                response = "This appears to be the beginning of our conversation! I don't have any previous history to show you yet."
        
        return {
            "tool_used": "memory",
            "response": response
        }
    
    # === NEW PYGPT TOOL EXECUTION METHODS ===
    
    def _execute_audio_processing(self, parameters: Dict, user_input: str, user_intent: str) -> Dict[str, Any]:
        """Execute audio processing operations (TTS/STT)"""
        try:
            audio_tool = self.tools["audio"]
            user_lower = user_input.lower()
            
            # Text-to-Speech
            if any(phrase in user_lower for phrase in ["read aloud", "text to speech", "tts", "speak"]):
                # Extract text to speak
                text_to_speak = user_input
                for phrase in ["read aloud", "text to speech", "tts", "speak"]:
                    text_to_speak = text_to_speak.replace(phrase, "").strip()
                
                if not text_to_speak:
                    text_to_speak = "Hello! This is a test of the text to speech system."
                
                result = audio_tool.text_to_speech(text_to_speak, voice="en-US-AriaNeural")
                if result["success"]:
                    return {
                        "tool_used": "audio",
                        "response": f"🔊 Generated audio: {result.get('audio_file', 'audio.wav')}\n\nText spoken: \"{text_to_speak}\"",
                        "audio_file": result.get("audio_file")
                    }
                else:
                    return {
                        "tool_used": "audio",
                        "response": f"❌ TTS failed: {result.get('error', 'Unknown error')}",
                        "error": result.get("error")
                    }
            
            # Speech-to-Text
            elif any(phrase in user_lower for phrase in ["transcribe", "speech to text", "stt", "audio file"]):
                return {
                    "tool_used": "audio",
                    "response": "🎤 Please provide an audio file path for transcription, or use the file upload feature.",
                    "instructions": "To transcribe audio, use: audio_tool.speech_to_text('path/to/audio.wav')"
                }
            
            else:
                # General audio processing info
                return {
                    "tool_used": "audio",
                    "response": "🎵 **Audio Processing Available:**\n• Text-to-Speech (TTS)\n• Speech-to-Text (STT)\n• Multiple voice options\n\nTry: 'Read aloud Hello World' or 'Transcribe audio file'"
                }
                
        except Exception as e:
            return {
                "tool_used": "audio",
                "error": str(e),
                "response": f"❌ Audio processing error: {e}"
            }
    
    def _execute_code_interpreter(self, parameters: Dict, user_input: str, user_intent: str) -> Dict[str, Any]:
        """Execute code interpretation and execution"""
        try:
            code_tool = self.tools["code"]
            
            # Extract code from user input
            code_to_run = None
            language = "python"  # default
            
            # Look for code blocks
            if "```" in user_input:
                lines = user_input.split("\n")
                in_code_block = False
                code_lines = []
                
                for line in lines:
                    if line.strip().startswith("```"):
                        if not in_code_block:
                            in_code_block = True
                            # Check for language specification
                            lang_spec = line.strip()[3:].strip()
                            if lang_spec:
                                language = lang_spec
                        else:
                            break
                    elif in_code_block:
                        code_lines.append(line)
                
                code_to_run = "\n".join(code_lines)
            
            # If no code block, try to extract from natural language
            if not code_to_run:
                user_lower = user_input.lower()
                if "python" in user_lower:
                    language = "python"
                elif "javascript" in user_lower or "js" in user_lower:
                    language = "javascript"
                elif "bash" in user_lower or "shell" in user_lower:
                    language = "bash"
                
                # Simple code extraction (this could be improved)
                code_to_run = user_input.replace("run code", "").replace("execute", "").strip()
            
            if code_to_run:
                result = code_tool.execute_code(code_to_run, language)
                
                response = f"💻 **Code Execution Result** ({language})\n\n"
                if result["success"]:
                    response += f"**Output:**\n```\n{result.get('output', 'No output')}\n```"
                    if result.get("execution_time"):
                        response += f"\n⏱️ Execution time: {result['execution_time']:.3f}s"
                else:
                    response += f"❌ **Error:**\n```\n{result.get('error', 'Unknown error')}\n```"
                
                return {
                    "tool_used": "code",
                    "response": response,
                    "result": result
                }
            else:
                return {
                    "tool_used": "code",
                    "response": "💻 **Code Interpreter Ready**\n\nSupported languages: Python, JavaScript, Bash, PowerShell\n\nProvide code in markdown blocks:\n```python\nprint('Hello World')\n```"
                }
                
        except Exception as e:
            return {
                "tool_used": "code",
                "error": str(e),
                "response": f"❌ Code execution error: {e}"
            }
    
    def _execute_document_processing(self, parameters: Dict, user_input: str, user_intent: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Execute document processing operations"""
        try:
            doc_tool = self.tools["documents"]
            user_lower = user_input.lower()
            
            # Check for specific file path in the request
            file_path = None
            for word in user_input.split():
                if any(ext in word.lower() for ext in ['.pdf', '.docx', '.xlsx', '.csv', '.pptx']):
                    file_path = word.strip('"\'')
                    break
            
            if file_path:
                # Process specific document
                result = doc_tool.process_document(file_path)
                
                if result["success"]:
                    response = f"📄 **Document Analysis: {result.get('filename', 'Unknown')}**\n\n"
                    response += f"**Type:** {result.get('file_type', 'Unknown')}\n"
                    response += f"**Pages/Sheets:** {result.get('page_count', 'N/A')}\n\n"
                    
                    if result.get("summary"):
                        response += f"**Summary:**\n{result['summary']}\n\n"
                    
                    if result.get("key_points"):
                        response += f"**Key Points:**\n"
                        for point in result['key_points'][:5]:
                            response += f"• {point}\n"
                    
                    return {
                        "tool_used": "documents",
                        "response": response,
                        "result": result
                    }
                else:
                    return {
                        "tool_used": "documents",
                        "response": f"❌ Document processing failed: {result.get('error', 'Unknown error')}",
                        "error": result.get("error")
                    }
            else:
                # General document processing info
                return {
                    "tool_used": "documents",
                    "response": "📄 **Document Processor Ready**\n\nSupported formats: PDF, DOCX, XLSX, CSV, PPTX\n\nTry: 'Analyze document.pdf' or 'Summarize report.docx'"
                }
                
        except Exception as e:
            return {
                "tool_used": "documents",
                "error": str(e),
                "response": f"❌ Document processing error: {e}"
            }
    
    def _execute_api_integration(self, parameters: Dict, user_input: str, user_intent: str) -> Dict[str, Any]:
        """Execute API integration operations"""
        try:
            api_tool = self.tools["api"]
            user_lower = user_input.lower()
            
            # Weather
            if "weather" in user_lower:
                # Extract location
                location = "London"  # default
                words = user_input.split()
                for i, word in enumerate(words):
                    if word.lower() == "in" and i + 1 < len(words):
                        location = words[i + 1]
                        break
                    elif word.lower() == "weather" and i + 1 < len(words):
                        location = words[i + 1]
                        break
                
                result = api_tool.get_weather(location)
                if result["success"]:
                    response = f"🌤️ **Weather in {result['location']}, {result['country']}**\n\n"
                    response += f"🌡️ **Temperature:** {result['temperature']}°C (feels like {result['feels_like']}°C)\n"
                    response += f"📝 **Description:** {result['description']}\n"
                    response += f"💧 **Humidity:** {result['humidity']}%\n"
                    response += f"💨 **Wind:** {result['wind_speed']} m/s"
                    return {
                        "tool_used": "api",
                        "response": response
                    }
                else:
                    return {
                        "tool_used": "api",
                        "response": f"❌ Weather lookup failed: {result.get('error', 'Unknown error')}"
                    }
            
            # News
            elif "news" in user_lower:
                query = user_input.replace("news about", "").replace("latest news", "").strip()
                result = api_tool.get_news(query=query if query != user_input else None, max_articles=5)
                
                if result["success"]:
                    response = f"📰 **Latest News** {'about ' + query if query != user_input else ''}\n\n"
                    for i, article in enumerate(result["articles"][:3], 1):
                        response += f"**{i}. {article['title']}**\n"
                        response += f"   {article['description'] or 'No description'}\n"
                        response += f"   Source: {article['source']}\n\n"
                    
                    return {
                        "tool_used": "api",
                        "response": response
                    }
                else:
                    return {
                        "tool_used": "api",
                        "response": f"❌ News lookup failed: {result.get('error', 'Unknown error')}"
                    }
            
            # Currency/Exchange rates
            elif any(phrase in user_lower for phrase in ["currency", "exchange rate", "usd to", "eur to"]):
                result = api_tool.get_exchange_rates("USD", ["EUR", "GBP", "JPY", "CAD"])
                
                if result["success"]:
                    response = f"💱 **Exchange Rates** (Base: {result['base_currency']})\n\n"
                    for currency, rate in list(result["rates"].items())[:5]:
                        response += f"**{result['base_currency']} → {currency}:** {rate:.4f}\n"
                    
                    return {
                        "tool_used": "api",
                        "response": response
                    }
                else:
                    return {
                        "tool_used": "api",
                        "response": f"❌ Exchange rate lookup failed: {result.get('error', 'Unknown error')}"
                    }
            
            # GitHub search
            elif "github" in user_lower:
                query = user_input.replace("github", "").replace("search", "").strip()
                result = api_tool.github_search_repos(query, max_results=5)
                
                if result["success"]:
                    response = f"🐙 **GitHub Repositories** for '{query}'\n\n"
                    for repo in result["repositories"][:3]:
                        response += f"**⭐ {repo['name']}** ({repo['stars']} stars)\n"
                        response += f"   {repo['description'] or 'No description'}\n"
                        response += f"   Language: {repo['language'] or 'N/A'}\n\n"
                    
                    return {
                        "tool_used": "api",
                        "response": response
                    }
                else:
                    return {
                        "tool_used": "api",
                        "response": f"❌ GitHub search failed: {result.get('error', 'Unknown error')}"
                    }
            
            else:
                # Show available integrations
                status = api_tool.get_integration_status()
                response = "🔗 **Available API Integrations:**\n\n"
                for name, info in status.items():
                    status_icon = "✅" if info["available"] and info["has_api_key"] else "❌"
                    response += f"{status_icon} **{info['name']}**\n"
                
                response += "\nTry: 'weather in Tokyo', 'latest news', 'currency rates', 'github python'"
                
                return {
                    "tool_used": "api",
                    "response": response
                }
                
        except Exception as e:
            return {
                "tool_used": "api",
                "error": str(e),
                "response": f"❌ API integration error: {e}"
            }
    
    def _execute_chat_with_files(self, parameters: Dict, user_input: str, user_intent: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Execute chat with files operations"""
        try:
            chat_files_tool = self.tools["chat_files"]
            
            # Extract question from user input
            query = user_input.replace("chat with files", "").replace("ask about file", "").strip()
            
            if query:
                # Search for relevant content
                search_results = chat_files_tool.search_files(query, max_results=5)
                
                if search_results:
                    # Build context for AI response
                    context_info = chat_files_tool.chat_with_files(query)
                    
                    if context_info["success"]:
                        # Have AI generate response based on file contents
                        ai_response = self._get_ai_response(
                            f"Based on the file contents provided, please answer: {query}",
                            conversation_history,
                            context_info["context"]
                        )
                        
                        response = f"📚 **Answer from indexed files:**\n\n{ai_response}\n\n"
                        response += f"**Sources:** {len(context_info['sources'])} files\n"
                        for source in context_info["sources"][:3]:
                            response += f"• {source['file_name']} (relevance: {source['relevance']:.2f})\n"
                        
                        return {
                            "tool_used": "chat_files",
                            "response": response,
                            "sources": context_info["sources"]
                        }
                    else:
                        return {
                            "tool_used": "chat_files",
                            "response": f"❌ No relevant content found for: {query}",
                            "error": context_info.get("error")
                        }
                else:
                    return {
                        "tool_used": "chat_files",
                        "response": "❌ No indexed files found. Use the file manager to index documents first."
                    }
            else:
                # Show indexed files
                files = chat_files_tool.get_indexed_files()
                if files:
                    response = f"📁 **Indexed Files** ({len(files)} total):\n\n"
                    for file_info in files[:5]:
                        response += f"• **{file_info['file_name']}** ({file_info['chunk_count']} chunks)\n"
                        response += f"  Type: {file_info['file_type']}, Size: {file_info['file_size']} bytes\n\n"
                    
                    response += "\nAsk questions like: 'What does the document say about...?'"
                else:
                    response = "📁 **No files indexed yet**\n\nTo chat with files, first add them to the index using the file manager."
                
                return {
                    "tool_used": "chat_files",
                    "response": response
                }
                
        except Exception as e:
            return {
                "tool_used": "chat_files",
                "error": str(e),
                "response": f"❌ Chat with files error: {e}"
            }
    
    def _execute_model_management(self, parameters: Dict, user_input: str, user_intent: str) -> Dict[str, Any]:
        """Execute AI model management operations"""
        try:
            model_tool = self.tools["models"]
            user_lower = user_input.lower()
            
            # Model switching
            if any(phrase in user_lower for phrase in ["switch to", "use", "change to"]):
                # Extract model name
                model_name = None
                if "gemini" in user_lower:
                    model_name = "gemini-pro"
                elif "gpt" in user_lower or "openai" in user_lower:
                    model_name = "gpt-4"
                elif "claude" in user_lower:
                    model_name = "claude-3-sonnet"
                elif "kobold" in user_lower:
                    model_name = "koboldcpp"
                elif "llama" in user_lower:
                    model_name = "llama3"
                
                if model_name:
                    success = model_tool.switch_model(model_name)
                    if success:
                        config = model_tool.models[model_name]
                        return {
                            "tool_used": "models",
                            "response": f"✅ Switched to **{config.name}**\n\nCapabilities: {', '.join(config.specialties or ['general'])}"
                        }
                    else:
                        return {
                            "tool_used": "models",
                            "response": f"❌ Could not switch to {model_name}. Model may not be available."
                        }
            
            # Show available models
            elif "list" in user_lower or "available" in user_lower or "models" in user_lower:
                available_models = model_tool.get_available_models()
                
                response = "🤖 **Available AI Models:**\n\n"
                for name, config in available_models:
                    current_marker = "👈 " if name == model_tool.current_model else "   "
                    response += f"{current_marker}**{config.name}**\n"
                    response += f"     Specialties: {', '.join(config.specialties or ['general'])}\n"
                    response += f"     Context: {config.context_length:,} tokens\n\n"
                
                return {
                    "tool_used": "models",
                    "response": response
                }
            
            # Model statistics
            elif "stats" in user_lower or "statistics" in user_lower:
                stats = model_tool.get_model_stats()
                
                if stats:
                    response = "📊 **Model Usage Statistics:**\n\n"
                    for model_name, model_stats in stats.items():
                        response += f"**{model_name}:**\n"
                        response += f"   Requests: {model_stats['requests']}\n"
                        response += f"   Avg Response Time: {model_stats['avg_response_time']}s\n"
                        response += f"   Success Rate: {model_stats['success_rate']}%\n\n"
                else:
                    response = "📊 No usage statistics available yet."
                
                return {
                    "tool_used": "models",
                    "response": response
                }
            
            else:
                # General model info
                current_model = model_tool.current_model
                if current_model:
                    config = model_tool.models[current_model]
                    response = f"🤖 **Current Model:** {config.name}\n\n"
                    response += f"**Capabilities:** {', '.join(config.specialties or ['general'])}\n"
                    response += f"**Context Length:** {config.context_length:,} tokens\n\n"
                    response += "Try: 'switch to gemini', 'list models', 'model stats'"
                else:
                    response = "❌ No active model found."
                
                return {
                    "tool_used": "models",
                    "response": response
                }
                
        except Exception as e:
            return {
                "tool_used": "models",
                "error": str(e),
                "response": f"❌ Model management error: {e}"
            }
    
    def _handle_character_conversation(self, user_input: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Handle character-based conversation"""
        
        # Build conversation context with memory
        full_history = self._build_conversation_context(conversation_history)
        
        # Generate character response
        response = self._get_ai_response(user_input, full_history)
        
        # Save to memory
        self.memory_manager.save_conversation_turn(user_input, response)
        
        return {
            "tool_used": "character_chat",
            "response": response,
            "is_conversation": True
        }
    
    def _build_conversation_context(self, session_history: List[Dict] = None) -> List[Dict]:
        """Build conversation context from memory and session with better preservation"""
        # Start with session history if provided (this is the most recent context)
        full_history = []
        
        if session_history:
            # Convert session history to standardized format and preserve all context
            for msg in session_history:
                if msg.get("role") == "user":
                    full_history.append({
                        "role": "user",
                        "content": msg.get("content", ""),
                        "timestamp": msg.get("timestamp", "")
                    })
                elif msg.get("role") == "assistant":
                    full_history.append({
                        "role": "assistant", 
                        "content": msg.get("content", ""),
                        "sender": msg.get("sender", "AI"),
                        "timestamp": msg.get("timestamp", "")
                    })
        
        # Get persistent memory only if we don't have much session history
        if len(full_history) < 6:
            memory_history = self.memory_manager.get_conversation_history(limit=6)
            # Prepend memory history (older context)
            full_history = memory_history + full_history
        
        # Keep reasonable context window but preserve recent important exchanges
        if len(full_history) > 16:
            # Keep first 4 messages (initial context) and last 12 messages (recent context)
            if len(full_history) > 16:
                full_history = full_history[:2] + full_history[-14:]
        
        print(f"[SMART] Built conversation context with {len(full_history)} messages")
        return full_history
    
    def _get_ai_response(self, user_message: str, conversation_history: List[Dict] = None) -> str:
        """Get AI response with character system prompt and full conversation context"""
        try:
            if hasattr(self.brain, 'chat_with_character'):
                return self.brain.chat_with_character(user_message, conversation_history)
            elif hasattr(self.brain, '_make_request'):
                # Build context with character prompt
                character_prompt = self.character_manager.get_system_prompt()
                
                # Build comprehensive conversation context
                context = character_prompt + "\n\nConversation History:\n"
                
                if conversation_history:
                    # Include more context messages for better continuity
                    recent_messages = conversation_history[-10:]  # Last 10 messages
                    for msg in recent_messages:
                        role = msg.get("role", "user")
                        content = msg.get("content", "")
                        timestamp = msg.get("timestamp", "")
                        
                        if role == "user":
                            context += f"Human: {content}\n"
                        elif role == "assistant":
                            # Include sender info if available
                            sender = msg.get("sender", "Assistant")
                            context += f"{sender}: {content}\n"
                        
                        # Add a small separator for readability
                        if len(recent_messages) > 1:
                            context += "\n"
                
                # Add current user message
                context += f"\nHuman: {user_message}\n{self.character_manager.current_character.name}:"
                
                print(f"[SMART] Sending {len(conversation_history or [])} context messages to AI")
                
                return self.brain._make_request(context, temperature=0.7, max_tokens=1000)
            else:
                # Simple fallback
                return self.brain.generate_response(user_message)
                
        except Exception as e:
            print(f"[SMART] AI response error: {e}")
            return f"I apologize, but I'm having trouble generating a response right now. Error: {e}"
    
    def _format_search_results(self, results: List[Dict]) -> str:
        """Format search results for AI processing"""
        formatted = ""
        for i, result in enumerate(results[:5], 1):
            formatted += f"{i}. **{result.get('title', 'No title')}**\n"
            formatted += f"   URL: {result.get('url', 'No URL')}\n"
            if result.get('snippet'):
                formatted += f"   Description: {result['snippet']}\n"
            formatted += "\n"
        return formatted
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            "brain_available": self.brain is not None,
            "brain_type": type(self.brain).__name__ if self.brain else None,
            "tools_loaded": list(self.tools.keys()),
            "character": self.character_manager.get_character_info(),
            "memory_enabled": True
        }
