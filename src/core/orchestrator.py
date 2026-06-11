"""
AI Companion Orchestrator
This is the main coordination layer that brings all tools together.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from core.memory_manager import get_memory_manager

class AICompanionOrchestrator:
    """Main orchestrator that coordinates all AI companion tools"""
    
    def __init__(self):
        self.tools = {}
        self.brain = None  # The 7B model (KoboldCPP)
        self.pending_deletions = {}  # Store pending deletion requests by user session
        self._last_pending_deletion = None  # Simple storage for testing
        self.memory_manager = get_memory_manager()  # Conversation memory
        self._load_tools()
        self._load_brain()
    
    def _load_brain(self):
        """Load the main AI brain (try Gemini first, then KoboldCPP as fallback)"""
        brain_loaded = False
        
        # Try Gemini API first with timeout protection
        try:
            print("  🔄 Attempting Gemini connection...")
            import threading
            import time
            
            gemini_client = None
            gemini_error = None
            
            def load_gemini():
                nonlocal gemini_client, gemini_error
                try:
                    from core.gemini_client import GeminiClient
                    client = GeminiClient()
                    if client.model:
                        gemini_client = client
                    else:
                        gemini_error = "Gemini model not initialized"
                except Exception as e:
                    gemini_error = str(e)
            
            # Start Gemini loading in thread with timeout
            thread = threading.Thread(target=load_gemini, daemon=True)
            thread.start()
            thread.join(timeout=10)  # 10 second timeout
            
            if thread.is_alive():
                print("  ⚠️  Gemini connection timed out (10s)")
            elif gemini_client:
                self.brain = gemini_client
                self.brain_type = "gemini"
                print("  [SUCCESS] Gemini brain loaded")
                brain_loaded = True
            elif gemini_error:
                print(f"  ⚠️  Gemini brain failed: {gemini_error}")
            else:
                print("  ⚠️  Gemini brain failed to connect")
                
        except Exception as e:
            print(f"  ⚠️  Gemini brain loading failed: {e}")
        
        # Fallback to KoboldCPP if Gemini isn't available
        if not brain_loaded:
            try:
                print("  🔄 Attempting KoboldCPP connection...")
                
                kobold_client = None
                kobold_error = None
                
                def load_kobold():
                    nonlocal kobold_client, kobold_error
                    try:
                        from core.koboldcpp_client import KoboldCPPClient
                        client = KoboldCPPClient()
                        if client:
                            kobold_client = client
                        else:
                            kobold_error = "KoboldCPP client not initialized"
                    except Exception as e:
                        kobold_error = str(e)
                
                # Start KoboldCPP loading in thread with timeout
                thread = threading.Thread(target=load_kobold, daemon=True)
                thread.start()
                thread.join(timeout=10)  # 10 second timeout
                
                if thread.is_alive():
                    print("  ⚠️  KoboldCPP connection timed out (10s)")
                elif kobold_client:
                    self.brain = kobold_client
                    self.brain_type = "koboldcpp"
                    print("  [SUCCESS] KoboldCPP brain loaded")
                    brain_loaded = True
                elif kobold_error:
                    print(f"  ❌ KoboldCPP brain failed: {kobold_error}")
                else:
                    print("  ❌ KoboldCPP brain failed to connect")
                    
            except Exception as e:
                print(f"  ❌ KoboldCPP brain loading failed: {e}")
        
        if not brain_loaded:
            print("  ❌ No AI brain available! Please configure Gemini API or KoboldCPP")
            self.brain = None
            self.brain_type = None
    
    def _load_tools(self):
        """Load all available tools"""
        print("[INFO] Loading AI Companion tools...")
        
        # Load enhanced web search with multiple providers
        try:
            from tools.search.multi_searcher import MultiSearcher
            self.tools['search'] = MultiSearcher()
            
            # Show which search providers are available
            status = self.tools['search'].get_provider_status()
            providers = status['available_providers']
            primary = status['primary_provider']
            
            if providers:
                provider_list = ", ".join([p.title() for p in providers])
                print(f"  [SUCCESS] Web Search tool loaded - Providers: {provider_list}")
                if primary:
                    print(f"            Primary provider: {primary.title()}")
            else:
                print("  ⚠️  Web Search tool loaded but no API keys configured")
                print("       Configure Brave Search or Google Custom Search API")
        except Exception as e:
            print(f"  ❌ Web Search tool failed: {e}")
            # Fallback to original searcher
            try:
                from tools.search.searcher import WebSearcher
                self.tools['search'] = WebSearcher()
                print("  [FALLBACK] Using original Brave-only searcher")
            except Exception as fallback_error:
                print(f"  ❌ Fallback searcher also failed: {fallback_error}")
        
        # Load vision analysis - temporarily disabled due to hanging issue
        try:
            print("  ⚠️ Vision Analysis: Temporarily disabled (causing hang)")
            # from tools.vision.analyzer import VisionAnalyzer
            # self.tools['vision'] = VisionAnalyzer()
            # print("  ✅ Vision Analysis tool loaded")
        except Exception as e:
            print(f"  ❌ Vision Analysis tool failed: {e}")
        
        # Load file management
        try:
            from tools.files.file_manager import FileManager
            self.tools['files'] = FileManager()
            print("  ✅ File Management tool loaded")
        except Exception as e:
            print(f"  ❌ File Management tool failed: {e}")
        
        # Placeholder for other tools
        print("  ⚠️  Audio Processing: Not implemented yet")
        print("  ⚠️  Task Scheduling: Not implemented yet")
    
    def chat_with_character(self, user_input: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Have a regular conversation with the AI character (not tool-focused)
        
        Args:
            user_input: User's message
            conversation_history: Previous conversation messages
            
        Returns:
            Dictionary with AI's character response
        """
        if not self.brain:
            return {
                "error": "AI brain not available",
                "response": "Sorry, I'm not fully initialized yet. Please wait a moment."
            }
        
        try:
            # Merge session history with persistent memory
            full_history = self._build_full_conversation_history(conversation_history)
            
            response = self.brain.chat_with_character(user_input, full_history)
            if response:
                # Save this conversation turn to persistent memory
                self.memory_manager.save_conversation_turn(user_input, response)
                
                return {
                    "response": response,
                    "tool_used": "character_chat",
                    "is_conversation": True
                }
            else:
                return {
                    "error": "No response from AI",
                    "response": "I'm having trouble responding right now. Could you try again?"
                }
        except Exception as e:
            return {
                "error": f"Character chat error: {e}",
                "response": "Sorry, I encountered an error while thinking. Could you rephrase that?"
            }
    
    def _build_full_conversation_history(self, session_history: List[Dict[str, str]] = None) -> List[Dict[str, str]]:
        """
        Build full conversation history by merging persistent memory with current session
        
        Args:
            session_history: Current session conversation history
            
        Returns:
            Combined conversation history with persistent memory context
        """
        try:
            # Get persistent conversation history
            persistent_history = self.memory_manager.get_conversation_history(limit=10)
            
            # Start with persistent history
            full_history = persistent_history.copy()
            
            # Add current session history if provided
            if session_history:
                # Filter out any "thinking" messages or system messages
                clean_session_history = [
                    msg for msg in session_history 
                    if not (msg.get("content", "").startswith("🤔") or 
                           msg.get("content", "").startswith("❌"))
                ]
                full_history.extend(clean_session_history)
            
            # Limit total context to prevent token overflow
            max_total_messages = 15
            if len(full_history) > max_total_messages:
                # Keep the most recent messages
                full_history = full_history[-max_total_messages:]
            
            return full_history
            
        except Exception as e:
            print(f"[MEMORY] Error building conversation history: {e}")
            # Fallback to session history only
            return session_history or []
    
    def should_use_tools(self, user_input: str) -> bool:
        """
        Determine if the user input requires tools or is just conversation
        
        Args:
            user_input: The user's message
            
        Returns:
            True if tools should be used, False for regular conversation
        """
        tool_keywords = [
            'search', 'find', 'look up', 'google', 'research',
            'screenshot', 'image', 'picture', 'visual', 'see',
            'file', 'document', 'create', 'save', 'write', 'edit', 'read', 'open', 'delete', 'remove',
            'folder', 'directory', 'list', 'browse', 'explore',
            'docx', 'txt', 'markdown', 'html', 'json', 'python',
            'desktop', 'documents', 'downloads',
            'schedule', 'remind', 'calendar', 'appointment',
            'audio', 'voice', 'sound', 'music',
            'translate', 'translation', 'language', 'convert to',
            'memory', 'remember', 'conversation history', 'what did we talk about',
            'memory status', 'conversation stats'
        ]
        
        user_lower = user_input.lower()
        return any(keyword in user_lower for keyword in tool_keywords)

    def process_command(self, user_input: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Process a user command - either use tools or have a conversation
        
        Args:
            user_input: User's message
            conversation_history: Previous conversation messages
        """
        # First, check if this looks like a tool request or just conversation
        if self.should_use_tools(user_input):
            result = self._process_tool_command(user_input)
        else:
            result = self.chat_with_character(user_input, conversation_history)
        
        # Save tool-based interactions to memory (character chat saves itself)
        if self.should_use_tools(user_input) and result and 'response' in result:
            try:
                response_text = result.get('response', '')
                tool_used = result.get('tool_used', 'unknown')
                
                # Add tool info to response for better context
                enhanced_response = response_text
                if tool_used != 'character_chat':
                    enhanced_response += f"\n\n[Used: {tool_used}]"
                
                self.memory_manager.save_conversation_turn(
                    user_input, 
                    enhanced_response,
                    {"tool_used": tool_used, "is_tool_interaction": True}
                )
            except Exception as e:
                print(f"[MEMORY] Failed to save tool interaction: {e}")
        
        return result
    
    def process_user_input(self, user_input: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Alias for process_command for consistency
        
        Args:
            user_input: User's message
            conversation_history: Previous conversation messages
        """
        return self.process_command(user_input, conversation_history)
    
    def _process_tool_command(self, user_input: str) -> Dict[str, Any]:
        """
        Process a user command using tools (original logic)
        """
        user_input_lower = user_input.lower()
        
        # Check if this might be a confirmation response to a pending deletion
        if self._is_confirmation_response(user_input):
            return self._handle_confirmation_response(user_input)
        
        # Check for multi-operation requests (create AND delete) - but not if it's primarily a delete request
        has_create = any(keyword in user_input_lower for keyword in ['write', 'create', 'save']) and not any(keyword in user_input_lower for keyword in ['delete', 'remove'])
        has_delete = any(keyword in user_input_lower for keyword in ['delete', 'remove'])
        
        # Additional check: if user mentions "file" or "document" in context of deletion, don't treat as create
        if has_delete:
            has_create = False  # If it's a deletion request, it's not a creation request
        
        # If the request is primarily about deletion, don't treat it as multi-operation
        is_primarily_delete = any(phrase in user_input_lower for phrase in [
            'can you delete', 'please delete', 'remove the file', 'delete the file',
            'delete it', 'remove it', 'get rid of', 'delete all', 'remove all',
            'delete files', 'remove files'
        ]) or has_delete
        
        if has_create and has_delete and not is_primarily_delete:
            print("[DEBUG] Detected multi-operation request (create + delete)")
            return self._handle_multi_file_operation(user_input)
        
        # Force direct file creation for file-related requests to avoid complex workflows
        # IMPORTANT: Only for creation requests with implementation keywords
        file_creation_condition1 = any(keyword in user_input_lower for keyword in ['write', 'create', 'save'])
        file_creation_condition2 = any(keyword in user_input_lower for keyword in ['algorithm', 'code', 'example', 'implementation'])
        
        print(f"[DEBUG] File creation check - Create keywords: {file_creation_condition1}, Implementation keywords: {file_creation_condition2}, Has_delete: {has_delete}")
        
        if file_creation_condition1 and file_creation_condition2 and not has_delete:
            print("[DEBUG] Forcing direct file creation route")
            return self._handle_file_creation_request(user_input)
        
        # Force direct file deletion for delete requests
        if has_delete:
            print("[DEBUG] Forcing direct file deletion route")
            
            # Check if this is a vague deletion request
            if self._is_vague_deletion_request(user_input):
                print("[DEBUG] Detected vague deletion request")
                result = self._handle_vague_deletion_request(user_input)
                # Store pending deletion for confirmation
                if 'pending_deletion' in result:
                    self._last_pending_deletion = result['pending_deletion']
                return result
            else:
                print("[DEBUG] Detected specific deletion request")
                return self._handle_file_deletion_request(user_input)
        
        # Continue with the rest of the tool processing
        print("[DEBUG] Continuing to AI-powered tool processing")
        return self._continue_tool_processing(user_input)
    
    def _execute_single_tool(self, decision: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Execute a single tool based on AI decision"""
        tool_name = decision.get("tool")
        action = decision.get("action", "general")
        params = decision.get("params", {})
        
        # Check if this is a file search (tool="search" but with file-related params)
        if (tool_name == "search" and 
            ("directory" in params or "pattern" in params or "file_type" in params)):
            print(f"[DEBUG] Detected file search request, routing to files tool")
            # This is actually a file search, route to files tool
            tool_name = "files"
            action = "search"
        
        if tool_name == "search" and "search" in self.tools:
            query = params.get("query", user_input)
            
            # Get raw search results
            search_data = self.tools["search"].search(query, count=5)
            
            if search_data.get("error"):
                return {
                    "tool_used": "web_search",
                    "query": query,
                    "response": f"❌ Search Error: {search_data['error']}"
                }
            
            # Have the AI analyze and summarize the search results
            if search_data.get("results") and self.brain:
                # Prepare search results for AI analysis
                results_text = f"Search query: {query}\n\nSearch results:\n"
                for i, result in enumerate(search_data["results"][:5], 1):
                    results_text += f"\n{i}. Title: {result['title']}\n"
                    results_text += f"   URL: {result['url']}\n"
                    results_text += f"   Description: {result['description']}\n"
                
                # Ask AI to analyze and summarize
                summary_prompt = f"""Based on these search results, provide a helpful and informative summary to answer the user's question: "{query}"

{results_text}

Please:
1. Summarize the key information found
2. Answer the user's question directly
3. Include relevant details from the search results
4. Be conversational and helpful
5. Include 1-2 most relevant URLs for further reading

Respond naturally as an AI assistant."""
                
                try:
                    ai_summary = self.brain.chat_completion([
                        {"role": "system", "content": "You are a helpful AI assistant that analyzes search results and provides informative summaries."},
                        {"role": "user", "content": summary_prompt}
                    ], temperature=0.7, max_tokens=1024)  # Increased tokens for detailed summaries
                    
                    return {
                        "tool_used": "web_search",
                        "query": query,
                        "response": ai_summary
                    }
                except Exception as e:
                    print(f"[DEBUG] AI summary error: {e}")
                    # Fallback to formatted results if AI summary fails
                    fallback = self.tools["search"].quick_search(query, max_results=5)
                    return {
                        "tool_used": "web_search",
                        "query": query,
                        "response": fallback
                    }
            else:
                # Fallback if no AI brain or no results
                result = self.tools["search"].quick_search(query, max_results=5)
                return {
                    "tool_used": "web_search",
                    "query": query,
                    "response": result
                }
        
        elif tool_name == "vision" and "vision" in self.tools:
            question = params.get("question", user_input)
            result = self.tools["vision"].analyze_screenshot(question)
            return {
                "tool_used": "vision_analysis",
                "ai_reasoning": decision.get("reasoning", ""),
                "question": question,
                "response": result
            }
        
        elif tool_name == "files" and "files" in self.tools:
            # Use action from decision, not from params
            file_action = action if action != "general" else params.get("action", "create")
            
            if file_action == "create":
                # Handle both new format (content/filename/location) and KoboldCPP format (path)
                if "path" in params:
                    # KoboldCPP workflow format - extract from path
                    file_path = params["path"]
                    
                    # Fix placeholder username in path
                    if "UserName" in file_path:
                        from pathlib import Path
                        actual_username = Path.home().name
                        file_path = file_path.replace("UserName", actual_username)
                        print(f"[DEBUG] Fixed username in path: {file_path}")
                    
                    from pathlib import Path
                    path_obj = Path(file_path)
                    filename = path_obj.stem  # filename without extension
                    file_type = path_obj.suffix[1:] if path_obj.suffix else "txt"  # extension without dot
                    location = str(path_obj.parent)
                    content = params.get("content", "Generated content")
                    print(f"[DEBUG] KoboldCPP format - path: {file_path}, filename: {filename}, type: {file_type}")
                else:
                    # Standard format
                    content = params.get("content", "Generated content")
                    filename = params.get("filename", "document")
                    location = params.get("location", "desktop")
                    file_type = params.get("file_type", "txt")
                
                result = self.tools["files"].create_file(content, filename, location, file_type)
                return {
                    "tool_used": "file_creation",
                    "ai_reasoning": decision.get("reasoning", ""),
                    "action": file_action,
                    "response": result.get("message", str(result))
                }
            
            elif file_action == "write":
                # Handle KoboldCPP's separate write action
                if "path" in params and "content" in params:
                    file_path = params["path"]
                    content = params["content"]
                    
                    # Fix placeholder username in path
                    if "UserName" in file_path:
                        from pathlib import Path
                        actual_username = Path.home().name
                        file_path = file_path.replace("UserName", actual_username)
                        print(f"[DEBUG] Fixed username in write path: {file_path}")
                    
                    # For write action, we can use the file manager's direct file writing
                    try:
                        from pathlib import Path
                        path_obj = Path(file_path)
                        # Ensure directory exists
                        path_obj.parent.mkdir(parents=True, exist_ok=True)
                        # Write content to file
                        path_obj.write_text(content, encoding='utf-8')
                        
                        return {
                            "tool_used": "file_writing",
                            "ai_reasoning": decision.get("reasoning", ""),
                            "action": file_action,
                            "response": f"✅ Content written to {file_path}"
                        }
                    except Exception as e:
                        return {
                            "tool_used": "file_writing",
                            "ai_reasoning": decision.get("reasoning", ""),
                            "action": file_action,
                            "response": f"❌ Write failed: {e}"
                        }
                else:
                    return {
                        "tool_used": "file_writing", 
                        "ai_reasoning": decision.get("reasoning", ""),
                        "action": file_action,
                        "response": "❌ Write action missing path or content"
                    }
            
            elif file_action == "list":
                directory = params.get("directory", None)
                result = self.tools["files"].list_directory(directory)
                return {
                    "tool_used": "directory_listing",
                    "ai_reasoning": decision.get("reasoning", ""),
                    "action": file_action,
                    "response": f"Found {result.get('count', 0)} items in {result.get('directory', 'directory')}"
                }
            
            elif file_action == "read":
                file_path = params.get("file_path", "")
                result = self.tools["files"].read_file(file_path)
                return {
                    "tool_used": "file_reading",
                    "ai_reasoning": decision.get("reasoning", ""),
                    "action": file_action,
                    "response": result.get("content", str(result))[:1000] + "..." if len(result.get("content", "")) > 1000 else result.get("content", str(result))
                }
            
            elif file_action == "delete":
                file_path = params.get("file_path", "")
                result = self.tools["files"].delete_file(file_path)
                return {
                    "tool_used": "file_deletion",
                    "ai_reasoning": decision.get("reasoning", ""),
                    "action": file_action,
                    "response": result.get("message", str(result))
                }
            
            elif file_action == "search":
                # Handle file search requests
                from pathlib import Path
                print(f"[DEBUG] Starting file search action...")
                directory = params.get("directory", "desktop")
                pattern = params.get("pattern", "*")
                file_type = params.get("file_type", None)
                
                print(f"[DEBUG] Raw params - directory: {directory}, pattern: {pattern}, file_type: {file_type}")
                
                # Convert shorthand directory names to full paths
                if directory.lower() == "desktop":
                    directory = str(Path.home() / "Desktop")
                elif directory.lower() == "documents":
                    directory = str(Path.home() / "Documents")
                elif directory.lower() == "downloads":
                    directory = str(Path.home() / "Downloads")
                
                print(f"[DEBUG] File search - Directory: {directory}, Pattern: {pattern}, Type: {file_type}")
                
                try:
                    result = self.tools["files"].find_files_by_pattern(directory, pattern, file_type)
                    print(f"[DEBUG] Search completed, result success: {result.get('success')}")
                    
                    if result.get("success"):
                        matching_files = result.get("matches", [])
                        print(f"[DEBUG] Found {len(matching_files)} matching files")
                        
                        if matching_files:
                            response = f"I found {len(matching_files)} file(s) matching your search:\n\n"
                            for i, file_info in enumerate(matching_files[:10], 1):
                                file_size_kb = round(file_info['size'] / 1024, 1) if file_info['size'] > 1024 else file_info['size']
                                size_unit = "KB" if file_info['size'] > 1024 else "bytes"
                                response += f"{i}. 📄 **{file_info['name']}** ({file_size_kb} {size_unit})\n"
                            
                            if len(matching_files) > 10:
                                response += f"\n... and {len(matching_files) - 10} more files"
                        else:
                            location_name = "Desktop" if "desktop" in directory.lower() else "Documents" if "documents" in directory.lower() else "Downloads" if "downloads" in directory.lower() else directory
                            response = f"I didn't find any files matching your search criteria in {location_name}."
                            if file_type:
                                response += f" (Looking for {file_type} files with pattern '{pattern}')"
                    else:
                        response = f"I couldn't search the directory: {result.get('error', 'Unknown error')}"
                        
                    print(f"[DEBUG] Generated response length: {len(response)} characters")
                    
                    return {
                        "tool_used": "file_search",
                        "ai_reasoning": decision.get("reasoning", ""),
                        "action": file_action,
                        "response": response
                    }
                    
                except Exception as e:
                    print(f"[DEBUG] File search error: {e}")
                    return {
                        "tool_used": "file_search",
                        "ai_reasoning": decision.get("reasoning", ""),
                        "action": file_action,
                        "response": f"I encountered an error while searching for files: {e}"
                    }
        
        else:
            return self._rule_based_routing(user_input)
    
    def _execute_workflow(self, workflow: List[Dict], user_input: str) -> Dict[str, Any]:
        """Execute a multi-tool workflow with timeout handling and result passing"""
        results = []
        search_results = None  # Store search results for file creation
        
        try:
            for i, step in enumerate(workflow):
                print(f"[DEBUG] Executing workflow step {i+1}/{len(workflow)}: {step.get('tool')} -> {step.get('action')}")
                
                # Handle search results injection for file creation
                if (search_results and 
                    step.get("tool") == "files" and 
                    step.get("action") == "create" and
                    step.get("params", {}).get("content") == "{SEARCH_RESULTS}"):
                    
                    print(f"[DEBUG] Injecting search results into file creation step")
                    print(f"[DEBUG] Search results length: {len(search_results)} characters")
                    # Replace placeholder with actual search results
                    step["params"]["content"] = search_results
                
                # Also check for other variations of the placeholder
                elif (search_results and 
                      step.get("tool") == "files" and 
                      step.get("action") == "create"):
                    
                    content = step.get("params", {}).get("content", "")
                    if "{SEARCH_RESULTS}" in str(content):
                        print(f"[DEBUG] Found {{SEARCH_RESULTS}} placeholder in content, replacing...")
                        step["params"]["content"] = str(content).replace("{SEARCH_RESULTS}", search_results)
                
                tool_result = self._execute_single_tool(step, user_input)
                results.append(tool_result)
                
                # Store search results for potential use in next steps
                if (step.get("tool") == "search" and 
                    tool_result.get("tool_used") == "web_search" and
                    tool_result.get("response")):
                    search_results = tool_result.get("response")
                    print(f"[DEBUG] Stored search results for workflow: {len(search_results)} characters")
                    print(f"[DEBUG] Search results preview: {search_results[:100]}...")
                
                # If any step fails critically, stop the workflow
                if tool_result.get("error") and "timeout" in str(tool_result.get("error", "")).lower():
                    print(f"[DEBUG] Workflow stopped due to timeout at step {i+1}")
                    break
        
        except Exception as e:
            print(f"[DEBUG] Workflow execution error: {e}")
            # Return partial results if we have any
            if results:
                results.append({
                    "error": f"Workflow interrupted: {e}",
                    "partial_completion": True
                })
        
        # Generate a comprehensive response
        if results:
            successful_steps = [r for r in results if not r.get("error")]
            failed_steps = [r for r in results if r.get("error")]
            
            response_parts = []
            if successful_steps:
                response_parts.append(f"✅ Successfully completed {len(successful_steps)} step(s)")
                
                # For search + file creation workflows, provide a summary
                search_step = next((r for r in successful_steps if r.get("tool_used") == "web_search"), None)
                file_step = next((r for r in successful_steps if r.get("tool_used") == "file_creation"), None)
                
                if search_step and file_step:
                    response_parts.append(f"🔍 Searched for: {search_step.get('query', 'information')}")
                    response_parts.append(f"📄 Created file with search results")
                    
            if failed_steps:
                response_parts.append(f"❌ {len(failed_steps)} step(s) encountered issues")
            
            return {
                "tool_used": "ai_workflow",
                "steps": results,
                "response": ". ".join(response_parts) + f". Total workflow steps: {len(workflow)}"
            }
        else:
            return {
                "tool_used": "ai_workflow",
                "steps": [],
                "response": "❌ Workflow could not be completed due to errors",
                "error": "No steps were successfully executed"
            }
    
    def _rule_based_routing(self, user_input: str) -> Dict[str, Any]:
        """
        Fallback rule-based routing when AI brain is not available
        """
        user_input_lower = user_input.lower()
        
        # Priority 1: File search operations (find files, search for files)
        if any(keyword in user_input_lower for keyword in ['find', 'search']) and any(keyword in user_input_lower for keyword in ['file', 'files', 'docx', 'txt', 'document', 'documents']) and any(keyword in user_input_lower for keyword in ['desktop', 'documents', 'downloads', 'folder', 'directory']):
            print("[DEBUG] Rule-based routing: Detected file search request")
            # Create a file search decision manually
            decision = {
                "tool": "files",
                "action": "search", 
                "params": {
                    "directory": "desktop" if "desktop" in user_input_lower else "documents" if "documents" in user_input_lower else "downloads" if "downloads" in user_input_lower else "desktop",
                    "pattern": "*.docx" if "docx" in user_input_lower else "*.txt" if "txt" in user_input_lower else "*",
                    "file_type": "docx" if "docx" in user_input_lower else "txt" if "txt" in user_input_lower else None
                }
            }
            return self._execute_single_tool(decision, user_input)
        
        # Priority 2: File creation with specific content
        elif any(keyword in user_input_lower for keyword in ['write', 'create', 'save', 'docx', 'document', 'file']) and any(keyword in user_input_lower for keyword in ['algorithm', 'code', 'example', 'implementation']):
            return self._handle_file_creation_request(user_input)
        
        # Priority 3: Web search  
        elif any(keyword in user_input_lower for keyword in ['search', 'find online', 'look up', 'google']):
            return self._handle_search_request(user_input)
        
        elif any(keyword in user_input_lower for keyword in ['translate', 'translation', 'convert to']):
            return self._handle_translation_request(user_input)
        
        elif any(keyword in user_input_lower for keyword in ['create file', 'write file', 'save', 'docx', 'document']):
            return self._handle_file_creation_request(user_input)
        
        elif any(keyword in user_input_lower for keyword in ['list', 'browse', 'directory', 'folder', 'files in']):
            return self._handle_directory_request(user_input)
        
        elif any(keyword in user_input_lower for keyword in ['screenshot', 'screen', 'see', 'analyze image']):
            return self._handle_vision_request(user_input)
        
        elif any(keyword in user_input_lower for keyword in ['search', 'screenshot']) and len(user_input_lower.split()) > 5:
            # Complex multi-tool request
            return self._handle_multi_tool_request(user_input)
        
        else:
            return {
                "response": "I understand you want me to help, but I'm not sure which tool to use. Try commands like:",
                "suggestions": [
                    "Search for information about AI models",
                    "Take a screenshot and analyze it",
                    "Look up recent news about technology"
                ]
            }
    
    def _handle_search_request(self, query: str) -> Dict[str, Any]:
        """Handle web search requests with AI analysis"""
        if 'search' not in self.tools:
            return {"error": "Web search tool not available"}
        
        # Extract search query (simple approach)
        search_terms = query.replace('search for', '').replace('look up', '').replace('find', '').strip()
        
        # Get raw search results
        search_data = self.tools['search'].search(search_terms, count=5)
        
        if search_data.get("error"):
            return {
                "tool_used": "web_search",
                "query": search_terms,
                "response": f"❌ Search Error: {search_data['error']}"
            }
        
        # Have the AI analyze and summarize the search results
        if search_data.get("results") and self.brain:
            # Prepare search results for AI analysis
            results_text = f"Search query: {search_terms}\n\nSearch results:\n"
            for i, result in enumerate(search_data["results"][:5], 1):
                results_text += f"\n{i}. Title: {result['title']}\n"
                results_text += f"   URL: {result['url']}\n"
                results_text += f"   Description: {result['description']}\n"
            
            # Ask AI to analyze and summarize
            summary_prompt = f"""Based on these search results, provide a helpful and informative summary to answer the user's question: "{search_terms}"

{results_text}

Please:
1. Summarize the key information found
2. Answer the user's question directly
3. Include relevant details from the search results
4. Be conversational and helpful
5. Include 1-2 most relevant URLs for further reading

Respond naturally as an AI assistant."""
            
            try:
                ai_summary = self.brain.chat_completion([
                    {"role": "system", "content": "You are a helpful AI assistant that analyzes search results and provides informative summaries."},
                    {"role": "user", "content": summary_prompt}
                ], temperature=0.7, max_tokens=1024)  # Increased tokens for detailed summaries
                
                return {
                    "tool_used": "web_search",
                    "query": search_terms,
                    "response": ai_summary
                }
            except Exception as e:
                print(f"[DEBUG] AI summary error: {e}")
                # Fallback to formatted results if AI summary fails
                fallback = self.tools['search'].quick_search(search_terms, max_results=5)
                return {
                    "tool_used": "web_search",
                    "query": search_terms,
                    "response": fallback
                }
        else:
            # Fallback if no AI brain or no results
            result = self.tools['search'].quick_search(search_terms, max_results=5)
            return {
                "tool_used": "web_search",
                "query": search_terms,
                "response": result
            }
    
    def _handle_translation_request(self, query: str) -> Dict[str, Any]:
        """Handle translation requests using the AI brain"""
        if not self.brain:
            return {"error": "AI translation not available - brain not loaded"}
        
        # Enhanced prompt for better translation
        translation_prompt = f"""You are a professional translator. Please help with this translation request: "{query}"

Guidelines:
1. If a target language is specified, translate accordingly
2. If no target language is specified, ask what language to translate to
3. Provide accurate, natural translations
4. For phrases or sentences, include context or notes if helpful
5. For single words, provide the translation and usage examples

Please respond naturally and helpfully."""
        
        try:
            translation_response = self.brain.chat_completion([
                {"role": "system", "content": "You are a helpful AI assistant with strong multilingual capabilities. You can translate between many languages accurately and naturally."},
                {"role": "user", "content": translation_prompt}
            ], temperature=0.3, max_tokens=800)  # Increased tokens for detailed translations
            
            return {
                "tool_used": "translation",
                "query": query,
                "response": translation_response
            }
        except Exception as e:
            print(f"[DEBUG] Translation error: {e}")
            return {
                "error": f"Translation failed: {e}",
                "response": "Sorry, I encountered an error while translating. Please try rephrasing your request."
            }
    
    def _handle_file_creation_request(self, query: str) -> Dict[str, Any]:
        """Handle file creation requests using AI to generate content"""
        print(f"[DEBUG] File creation request: {query}")
        
        if 'files' not in self.tools:
            return {"error": "File management tool not available"}
        
        if not self.brain:
            return {"error": "AI brain not available for content generation"}
        
        # Parse the request to understand what content to generate and where to save
        content_prompt = f"""Create a comprehensive document about: "{query}"

Write a complete, detailed explanation including:
- Introduction and overview
- Step-by-step implementation 
- Code examples with comments
- Performance analysis
- Usage examples
- Conclusion

Focus only on providing the actual content - do NOT mention tools, workflows, or file operations.
Write as if you're creating the final document content directly."""
        
        try:
            print("[DEBUG] Generating content with AI...")
            # Get AI-generated content and file details - Use dedicated file generation token limit
            file_gen_tokens = int(os.getenv("KOBOLDCPP_FILE_GENERATION_TOKENS", "4096"))
            print(f"[DEBUG] Using {file_gen_tokens} tokens for generation")
            
            ai_response = self.brain.chat_completion([
                {"role": "system", "content": "You are a helpful AI assistant that creates comprehensive, well-structured content for files. Focus on direct, useful content without meta-instructions."},
                {"role": "user", "content": content_prompt}
            ], temperature=0.7, max_tokens=file_gen_tokens)  # Use dedicated high token limit for file generation
            
            print(f"[DEBUG] AI response length: {len(ai_response) if ai_response else 0} characters")
            
            # Parse the AI response - simplified approach
            content = ai_response.strip() if ai_response else "Generated content based on your request."
            
            # Auto-detect file details from the original query
            filename, location, file_type = self._extract_file_details_from_query(query)
            print(f"[DEBUG] File details: {filename}.{file_type} in {location}")
            
            # Create the file
            result = self.tools['files'].create_file(content, filename, location, file_type)
            
            if result.get("success"):
                return {
                    "tool_used": "file_creation",
                    "query": query,
                    "response": f"✅ {result['message']}\n\nContent preview:\n{content[:200]}{'...' if len(content) > 200 else ''}"
                }
            else:
                return {
                    "tool_used": "file_creation",
                    "query": query,
                    "response": f"❌ File creation failed: {result.get('error', 'Unknown error')}"
                }
                
        except Exception as e:
            print(f"[DEBUG] File creation error: {e}")
            return {
                "error": f"File creation failed: {e}",
                "response": "Sorry, I encountered an error while creating the file. Please try again."
            }
    
    def _extract_file_details_from_query(self, query: str) -> tuple:
        """Extract filename, location, and file type from user query"""
        query_lower = query.lower()
        
        # Default values
        filename = "generated_document"
        location = "desktop"
        file_type = "txt"
        
        # Extract specific filename from quotes or 'named' pattern
        import re
        
        # Look for patterns like "named 'filename'" or "file named 'filename'"
        name_patterns = [
            r"named\s+['\"]([^'\"]+)['\"]",
            r"file\s+named\s+['\"]([^'\"]+)['\"]",
            r"call\s+it\s+['\"]([^'\"]+)['\"]",
            r"save\s+as\s+['\"]([^'\"]+)['\"]"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, query_lower)
            if match:
                filename = match.group(1).strip()
                print(f"[DEBUG] Extracted filename from pattern: {filename}")
                break
        
        # Detect file type from query
        if 'docx' in query_lower or 'word' in query_lower or 'document' in query_lower:
            file_type = 'docx'
        elif 'python' in query_lower or 'code' in query_lower or 'algorithm' in query_lower or '.py' in query_lower:
            file_type = 'py'
        elif 'markdown' in query_lower or '.md' in query_lower:
            file_type = 'md'
        elif 'html' in query_lower or 'web' in query_lower:
            file_type = 'html'
        elif 'json' in query_lower or 'data' in query_lower:
            file_type = 'json'
        
        # Detect location from query
        if 'documents' in query_lower:
            location = 'documents'
        elif 'downloads' in query_lower:
            location = 'downloads'
        else:
            location = 'desktop'  # default
        
        # Fallback filename extraction if no pattern matched
        if filename == "generated_document":
            if 'decrease and conquer' in query_lower:
                filename = "decrease_and_conquer_algorithm"
            elif 'binary search' in query_lower:
                filename = "binary_search_algorithm"
            elif 'algorithm' in query_lower:
                filename = "algorithm_implementation"
            elif 'code example' in query_lower:
                filename = "code_example"
        
        print(f"[DEBUG] File details: {filename}.{file_type} in {location}")
        return filename, location, file_type
    
    def _parse_file_creation_response(self, ai_response: str, original_query: str) -> tuple:
        """Parse AI response to extract content, filename, location, and file type"""
        try:
            # Default values
            content = "Generated content"
            filename = "document"
            location = "desktop"
            file_type = "txt"
            
            # Parse the structured response
            if "CONTENT:" in ai_response:
                content_part = ai_response.split("CONTENT:")[1]
                if "FILENAME:" in content_part:
                    content = content_part.split("FILENAME:")[0].strip()
                else:
                    content = content_part.strip()
            
            if "FILENAME:" in ai_response:
                filename_part = ai_response.split("FILENAME:")[1]
                if "LOCATION:" in filename_part:
                    filename = filename_part.split("LOCATION:")[0].strip()
                else:
                    filename = filename_part.strip()
            
            if "LOCATION:" in ai_response:
                location_part = ai_response.split("LOCATION:")[1]
                if "FILETYPE:" in location_part:
                    location = location_part.split("FILETYPE:")[0].strip()
                else:
                    location = location_part.strip()
            
            if "FILETYPE:" in ai_response:
                file_type = ai_response.split("FILETYPE:")[1].strip()
            
            # Validate and clean values
            location = location.lower() if location.lower() in ['desktop', 'documents', 'downloads'] else 'desktop'
            file_type = file_type.lower() if file_type.lower() in ['txt', 'docx', 'md', 'py', 'html', 'json'] else 'txt'
            
            # Auto-detect file type from query if not specified correctly
            query_lower = original_query.lower()
            if 'docx' in query_lower or 'word' in query_lower:
                file_type = 'docx'
            elif 'python' in query_lower or 'code' in query_lower or 'algorithm' in query_lower:
                file_type = 'py'
            elif 'markdown' in query_lower:
                file_type = 'md'
            elif 'html' in query_lower or 'web' in query_lower:
                file_type = 'html'
            elif 'json' in query_lower or 'data' in query_lower:
                file_type = 'json'
            
            return content, filename, location, file_type
            
        except Exception as e:
            print(f"[DEBUG] Parse error: {e}")
            # Fallback to simple content
            return ai_response, "generated_document", "desktop", "txt"
    
    def _handle_directory_request(self, query: str) -> Dict[str, Any]:
        """Handle directory listing and browsing requests"""
        if 'files' not in self.tools:
            return {"error": "File management tool not available"}
        
        # Extract directory from query or use default
        query_lower = query.lower()
        
        if 'desktop' in query_lower:
            directory = str(self.tools['files'].desktop)
        elif 'documents' in query_lower:
            directory = str(self.tools['files'].documents)
        elif 'downloads' in query_lower:
            directory = str(self.tools['files'].downloads)
        else:
            # Try to extract path from query or use current directory
            directory = None
        
        result = self.tools['files'].list_directory(directory)
        
        if result.get("success"):
            contents = result.get("contents", [])
            if contents:
                response = f"📁 Contents of {result['directory']}:\n\n"
                
                # Separate directories and files
                directories = [item for item in contents if item['type'] == 'directory']
                files = [item for item in contents if item['type'] == 'file']
                
                if directories:
                    response += "📂 Directories:\n"
                    for dir_item in directories[:10]:  # Limit to first 10
                        response += f"  • {dir_item['name']}/\n"
                    if len(directories) > 10:
                        response += f"  ... and {len(directories) - 10} more directories\n"
                    response += "\n"
                
                if files:
                    response += "📄 Files:\n"
                    for file_item in files[:15]:  # Limit to first 15
                        size = file_item.get('size', 0)
                        size_str = f" ({size:,} bytes)" if size else ""
                        response += f"  • {file_item['name']}{size_str}\n"
                    if len(files) > 15:
                        response += f"  ... and {len(files) - 15} more files\n"
                
                response += f"\nTotal: {len(directories)} directories, {len(files)} files"
            else:
                response = f"📁 {result['directory']} is empty"
            
            return {
                "tool_used": "directory_listing",
                "query": query,
                "response": response
            }
        else:
            return {
                "tool_used": "directory_listing",
                "query": query,
                "response": f"❌ Directory listing failed: {result.get('error', 'Unknown error')}"
            }
    
    def _handle_file_deletion_request(self, query: str) -> Dict[str, Any]:
        """Handle file deletion requests"""
        print(f"[DEBUG] File deletion request: {query}")
        
        if 'files' not in self.tools:
            return {"error": "File management tool not available"}
        
        # Try to extract file path from query using better pattern matching
        import re
        query_lower = query.lower()
        file_path = None
        
        # Look for patterns like "file named 'filename'" or "delete 'filename'"
        delete_patterns = [
            r"delete\s+['\"]([^'\"]+)['\"]",
            r"remove\s+['\"]([^'\"]+)['\"]",
            r"file\s+named\s+['\"]([^'\"]+)['\"]",
            r"['\"]([^'\"]+)['\"].*delete",
            r"['\"]([^'\"]+)['\"].*remove",
            r"named\s+['\"]([^'\"]+)['\"]"
        ]
        
        filename = None
        for pattern in delete_patterns:
            match = re.search(pattern, query_lower)
            if match:
                filename = match.group(1).strip()
                print(f"[DEBUG] Extracted filename for deletion: {filename}")
                break
        
        # If no pattern matched, try simple text extraction
        if not filename:
            # Look for common file references in text
            if 'document' in query_lower and ('desktop' in query_lower or 'delete' in query_lower):
                filename = 'document'
            elif 'test.txt' in query_lower:
                filename = 'test.txt'
            elif 'algorithm' in query_lower and 'txt' in query_lower:
                # Extract specific algorithm file names
                words = query_lower.split()
                for i, word in enumerate(words):
                    if 'algorithm' in word and i > 0:
                        # Try to get the full filename from previous words
                        potential_name = '_'.join(words[max(0, i-3):i+1])
                        if len(potential_name) > 4:  # Reasonable filename length
                            filename = potential_name
                            break
        
        if filename:
            # Determine file extension if not specified - PRESERVE user's explicit type mention
            if not any(filename.endswith(ext) for ext in ['.txt', '.docx', '.py', '.md', '.html', '.json']):
                # Try to infer extension from context - prioritize user's explicit mention
                if 'txt file' in query_lower or '.txt' in query_lower:
                    filename += '.txt'
                elif 'docx file' in query_lower or '.docx' in query_lower or 'word file' in query_lower:
                    filename += '.docx'
                elif 'python file' in query_lower or '.py' in query_lower:
                    filename += '.py'
                elif 'markdown file' in query_lower or '.md' in query_lower:
                    filename += '.md'
                else:
                    # If we can't determine the type, default based on context
                    if 'document' in filename.lower():
                        filename += '.docx'
                    else:
                        filename += '.txt'  # Default to txt for unclear cases
                        
                print(f"[DEBUG] Added extension to filename: {filename}")
        
        if filename:
            # Determine file extension if not specified
            if not any(filename.endswith(ext) for ext in ['.txt', '.docx', '.py', '.md', '.html', '.json']):
                # Try to infer extension from context - prioritize user's explicit mention
                if '.txt' in query_lower or 'txt file' in query_lower:
                    filename += '.txt'
                elif '.docx' in query_lower or 'docx file' in query_lower or 'word' in query_lower:
                    filename += '.docx'
                elif '.py' in query_lower or 'python file' in query_lower:
                    filename += '.py'
                elif '.md' in query_lower or 'markdown file' in query_lower:
                    filename += '.md'
                elif 'text' in query_lower:
                    filename += '.txt'
                else:
                    # If we can't determine the type, try to guess from filename
                    if 'document' in filename.lower():
                        filename += '.docx'
                    else:
                        filename += '.txt'  # Default to txt instead of docx
            
            # Determine location (default to desktop)
            if 'documents' in query_lower:
                location = str(Path.home() / "Documents")
            elif 'downloads' in query_lower:
                location = str(Path.home() / "Downloads")
            else:
                location = str(Path.home() / "Desktop")
            
            file_path = str(Path(location) / filename)
            print(f"[DEBUG] Constructed file path: {file_path}")
        
        if not file_path:
            return {
                "error": "Could not determine which file to delete",
                "response": "Please specify the filename more clearly. For example: 'delete document.docx' or 'remove the file named test.txt'"
            }
        
        result = self.tools['files'].delete_file(file_path)
        
        if result.get("success"):
            return {
                "tool_used": "file_deletion",
                "query": query,
                "response": result.get("message", "File deleted successfully")
            }
        else:
            return {
                "tool_used": "file_deletion",
                "query": query,
                "response": f"❌ File deletion failed: {result.get('error', 'Unknown error')}"
            }
    
    def _is_vague_deletion_request(self, query: str) -> bool:
        """Check if the deletion request is vague and needs clarification"""
        query_lower = query.lower()
        
        vague_patterns = [
            'delete all', 'remove all', 'delete every', 'remove every',
            'delete files', 'remove files', 'delete documents', 'remove documents',
            'starting with', 'ending with', 'containing', 'that contain',
            'like', 'similar to', 'matching', 'files in', 'txt files', 'docx files',
            'delete old', 'remove old', 'delete recent', 'remove recent'
        ]
        
        return any(pattern in query_lower for pattern in vague_patterns)
    
    def _handle_vague_deletion_request(self, query: str) -> Dict[str, Any]:
        """Handle vague deletion requests with pattern matching and confirmation"""
        print(f"[DEBUG] Handling vague deletion request: {query}")
        
        if 'files' not in self.tools:
            return {"error": "File management tool not available"}
        
        query_lower = query.lower()
        
        # Extract location
        if 'documents' in query_lower:
            location = str(Path.home() / "Documents")
            location_name = "Documents"
        elif 'downloads' in query_lower:
            location = str(Path.home() / "Downloads")
            location_name = "Downloads"
        else:
            location = str(Path.home() / "Desktop")
            location_name = "Desktop"
        
        # Extract file type
        file_type = None
        if 'txt file' in query_lower or '.txt' in query_lower:
            file_type = 'txt'
        elif 'docx file' in query_lower or '.docx' in query_lower or 'word file' in query_lower:
            file_type = 'docx'
        elif 'python file' in query_lower or '.py' in query_lower:
            file_type = 'py'
        elif 'markdown file' in query_lower or '.md' in query_lower:
            file_type = 'md'
        
        # Extract pattern
        import re
        pattern = "*"  # default to all files
        
        # Look for specific patterns
        if 'starting with' in query_lower:
            match = re.search(r"starting with ['\"]?([^'\"]+)['\"]?", query_lower)
            if match:
                pattern = f"{match.group(1).strip()}*"
        elif 'ending with' in query_lower:
            match = re.search(r"ending with ['\"]?([^'\"]+)['\"]?", query_lower)
            if match:
                pattern = f"*{match.group(1).strip()}"
        elif 'containing' in query_lower or 'that contain' in query_lower:
            match = re.search(r"(?:containing|that contain) ['\"]?([^'\"]+)['\"]?", query_lower)
            if match:
                pattern = f"*{match.group(1).strip()}*"
        elif 'like' in query_lower or 'similar to' in query_lower:
            match = re.search(r"(?:like|similar to) ['\"]?([^'\"]+)['\"]?", query_lower)
            if match:
                pattern = f"*{match.group(1).strip()}*"
        elif 'all' in query_lower and file_type:
            pattern = "*"  # will be filtered by file_type
        
        print(f"[DEBUG] Search criteria - Location: {location}, Pattern: {pattern}, Type: {file_type}")
        
        # Search for matching files
        search_result = self.tools['files'].find_files_by_pattern(location, pattern, file_type)
        
        if not search_result.get("success"):
            return {
                "tool_used": "vague_file_deletion",
                "query": query,
                "response": f"❌ Could not search for files: {search_result.get('error', 'Unknown error')}"
            }
        
        matching_files = search_result.get("matches", [])
        
        if not matching_files:
            return {
                "tool_used": "vague_file_deletion", 
                "query": query,
                "response": f"I couldn't find any files matching your criteria in {location_name}. " +
                          f"Pattern: '{pattern}'" + (f", Type: {file_type}" if file_type else "") + 
                          ". Could you be more specific about which files you want to delete?"
            }
        
        # Generate natural response with file list and confirmation request
        if len(matching_files) == 1:
            file_info = matching_files[0]
            file_size_kb = round(file_info['size'] / 1024, 1) if file_info['size'] > 1024 else file_info['size']
            size_unit = "KB" if file_info['size'] > 1024 else "bytes"
            
            response = f"I found 1 file matching your criteria in {location_name}:\n\n" + \
                      f"📄 **{file_info['name']}** ({file_size_kb} {size_unit})\n\n" + \
                      f"Are you sure you want to delete this file? Please confirm by saying 'yes, delete it' or 'cancel'."
        else:
            response = f"I found {len(matching_files)} files matching your criteria in {location_name}:\n\n"
            
            for i, file_info in enumerate(matching_files[:10], 1):  # Show up to 10 files
                file_size_kb = round(file_info['size'] / 1024, 1) if file_info['size'] > 1024 else file_info['size']
                size_unit = "KB" if file_info['size'] > 1024 else "bytes"
                response += f"{i}. 📄 **{file_info['name']}** ({file_size_kb} {size_unit})\n"
            
            if len(matching_files) > 10:
                response += f"... and {len(matching_files) - 10} more files\n"
            
            response += f"\nAre you sure you want to delete all {len(matching_files)} files? " + \
                       f"Please confirm by saying 'yes, delete all {len(matching_files)} files' or 'cancel'."
        
        # Store the pending deletion info for confirmation
        # (In a real implementation, you'd want to store this in session/context)
        
        return {
            "tool_used": "vague_file_deletion",
            "query": query,
            "response": response,
            "pending_deletion": {
                "files": [f["path"] for f in matching_files],
                "count": len(matching_files),
                "location": location_name
            }
        }
    
    def _handle_deletion_confirmation(self, user_input: str, pending_deletion: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user confirmation for pending file deletions"""
        user_input_lower = user_input.lower()
        
        # Check for confirmation patterns
        confirmation_patterns = [
            'yes', 'confirm', 'delete', 'proceed', 'do it', 'go ahead', 
            'delete all', 'delete them', 'remove them', 'yes delete'
        ]
        
        cancellation_patterns = [
            'no', 'cancel', 'stop', 'abort', 'nevermind', 'never mind', 'wait'
        ]
        
        is_confirmed = any(pattern in user_input_lower for pattern in confirmation_patterns)
        is_cancelled = any(pattern in user_input_lower for pattern in cancellation_patterns)
        
        if is_cancelled:
            return {
                "tool_used": "deletion_confirmation",
                "response": "Okay, I've cancelled the file deletion. No files were deleted."
            }
        
        if is_confirmed:
            # Proceed with deletion
            file_paths = pending_deletion.get("files", [])
            if not file_paths:
                return {
                    "tool_used": "deletion_confirmation",
                    "response": "There was an error with the deletion request. No files to delete."
                }
            
            # Use the multiple file deletion method
            deletion_result = self.tools['files'].delete_multiple_files(file_paths)
            
            if deletion_result.get("success"):
                successful = deletion_result.get("successful", 0)
                failed = deletion_result.get("failed", 0)
                location = pending_deletion.get("location", "the specified location")
                
                if failed == 0:
                    response = f"✅ Perfect! I've successfully deleted all {successful} files from {location}."
                else:
                    response = f"I've deleted {successful} files from {location}, but {failed} files couldn't be deleted (they might have been moved or are in use)."
                
                return {
                    "tool_used": "deletion_confirmation",
                    "response": response,
                    "deletion_result": deletion_result
                }
            else:
                return {
                    "tool_used": "deletion_confirmation", 
                    "response": f"❌ I encountered an error while deleting the files: {deletion_result.get('error', 'Unknown error')}"
                }
        else:
            # User input is ambiguous
            file_count = pending_deletion.get("count", 0)
            location = pending_deletion.get("location", "the location")
            
            return {
                "tool_used": "deletion_confirmation",
                "response": f"I'm not sure if you want to proceed. I have {file_count} files ready to delete from {location}. " +
                           f"Please say 'yes, delete them' to confirm or 'cancel' to stop."
            }
    
    def _is_confirmation_response(self, user_input: str) -> bool:
        """Check if user input looks like a confirmation response"""
        user_input_lower = user_input.lower().strip()
        
        # Only consider short responses as potential confirmations
        if len(user_input_lower.split()) > 15:
            return False
        
        # Check if we have a pending deletion
        if not (hasattr(self, '_last_pending_deletion') and self._last_pending_deletion):
            return False
        
        confirmation_patterns = [
            'yes', 'confirm', 'delete', 'proceed', 'do it', 'go ahead',
            'delete all', 'delete them', 'remove them', 'yes delete',
            'delete it', 'remove it', 'ok', 'okay', 'sure',
            'no', 'cancel', 'stop', 'abort', 'nevermind', 'never mind', 'wait', 'nope'
        ]
        
        return any(pattern in user_input_lower for pattern in confirmation_patterns)
    
    def _handle_confirmation_response(self, user_input: str) -> Dict[str, Any]:
        """Handle potential confirmation responses"""
        # For simplicity, we'll use a single pending deletion slot
        # In a real app, you'd want session-based storage
        
        if hasattr(self, '_last_pending_deletion') and self._last_pending_deletion:
            result = self._handle_deletion_confirmation(user_input, self._last_pending_deletion)
            # Clear the pending deletion after handling
            self._last_pending_deletion = None
            return result
        else:
            # No pending deletion, treat as regular command
            return self._process_tool_command_without_confirmation_check(user_input)
    
    def _process_tool_command_without_confirmation_check(self, user_input: str) -> Dict[str, Any]:
        """Process tool command without checking for confirmations (to avoid recursion)"""
        user_input_lower = user_input.lower()
        
        # Check for multi-operation requests (create AND delete) - but not if it's primarily a delete request
        has_create = any(keyword in user_input_lower for keyword in ['write', 'create', 'save']) and not any(keyword in user_input_lower for keyword in ['delete', 'remove'])
        has_delete = any(keyword in user_input_lower for keyword in ['delete', 'remove'])
        
        # Additional check: if user mentions "file" or "document" in context of deletion, don't treat as create
        if has_delete:
            has_create = False  # If it's a deletion request, it's not a creation request
        
        # If the request is primarily about deletion, don't treat it as multi-operation
        is_primarily_delete = any(phrase in user_input_lower for phrase in [
            'can you delete', 'please delete', 'remove the file', 'delete the file',
            'delete it', 'remove it', 'get rid of', 'delete all', 'remove all',
            'delete files', 'remove files'
        ]) or has_delete
        
        if has_create and has_delete and not is_primarily_delete:
            print("[DEBUG] Detected multi-operation request (create + delete)")
            return self._handle_multi_file_operation(user_input)
        
        # Force direct file creation for file-related requests to avoid complex workflows
        if any(keyword in user_input_lower for keyword in ['write', 'create', 'save', 'docx', 'document', 'file']) and any(keyword in user_input_lower for keyword in ['algorithm', 'code', 'example', 'implementation']) and not has_delete:
            print("[DEBUG] Forcing direct file creation route")
            return self._handle_file_creation_request(user_input)
        
        # Force direct file deletion for delete requests
        if has_delete:
            print("[DEBUG] Forcing direct file deletion route")
            
            # Check if this is a vague deletion request
            if self._is_vague_deletion_request(user_input):
                print("[DEBUG] Detected vague deletion request")
                result = self._handle_vague_deletion_request(user_input)
                # Store pending deletion for confirmation
                if 'pending_deletion' in result:
                    self._last_pending_deletion = result['pending_deletion']
                return result
            else:
                print("[DEBUG] Detected specific deletion request")
                return self._handle_file_deletion_request(user_input)
        
        # Continue with rest of logic...
        return self._continue_tool_processing(user_input)
    
    def _continue_tool_processing(self, user_input: str) -> Dict[str, Any]:
        """Continue with the original tool processing logic"""
        user_input_lower = user_input.lower()
        
        # Handle memory-related requests
        if any(keyword in user_input_lower for keyword in ['memory', 'conversation history', 'what did we talk about', 'memory status', 'conversation stats']):
            return self._handle_memory_request(user_input)
        
        # If we have the AI brain (KoboldCPP), use it to make decisions for other tools
        if self.brain:
            try:
                available_tools = list(self.tools.keys())
                decision = self.brain.decide_tool_action(user_input, available_tools)
                
                if "workflow" in decision:
                    # Multi-tool workflow
                    return self._execute_workflow(decision["workflow"], user_input)
                elif "tool" in decision:
                    # Single tool decision
                    return self._execute_single_tool(decision, user_input)
                else:
                    # Fallback to rule-based
                    return self._rule_based_routing(user_input)
                    
            except Exception as e:
                print(f"❌ AI decision error: {e}")
                return self._rule_based_routing(user_input)
        else:
            # Fallback to simple rule-based routing
            return self._rule_based_routing(user_input)
    
    def _handle_memory_request(self, user_input: str) -> Dict[str, Any]:
        """Handle memory and conversation history requests"""
        user_input_lower = user_input.lower()
        
        try:
            if any(keyword in user_input_lower for keyword in ['memory status', 'conversation stats', 'memory info']):
                # Get memory statistics
                stats = self.memory_manager.get_memory_stats()
                summary = self.memory_manager.get_conversation_summary()
                
                response = f"📊 **Conversation Memory Status**\n\n"
                response += f"💭 **Total conversations saved:** {stats['total_conversations']}\n"
                response += f"🕒 **Recent conversations (7 days):** {stats['recent_conversations']}\n"
                response += f"📅 **Total sessions:** {stats['total_sessions']}\n"
                response += f"🧠 **Memory enabled:** {'Yes' if stats['memory_enabled'] else 'No'}\n\n"
                response += f"📝 **Recent topics:** {summary}"
                
                return {
                    "tool_used": "conversation_memory",
                    "response": response
                }
                
            elif any(keyword in user_input_lower for keyword in ['what did we talk about', 'conversation history', 'previous conversations']):
                # Get recent conversation history
                history = self.memory_manager.get_conversation_history(limit=8)
                
                if not history:
                    response = "🤔 I don't have any previous conversation history stored yet. This might be our first conversation!"
                else:
                    response = "📚 **Recent Conversation History:**\n\n"
                    
                    # Group by conversation pairs
                    i = 0
                    conv_count = 0
                    while i < len(history) and conv_count < 4:  # Show last 4 conversation pairs
                        if history[i]['role'] == 'user':
                            user_msg = history[i]['content'][:100] + ("..." if len(history[i]['content']) > 100 else "")
                            
                            ai_msg = ""
                            if i + 1 < len(history) and history[i + 1]['role'] == 'assistant':
                                ai_msg = history[i + 1]['content'][:100] + ("..." if len(history[i + 1]['content']) > 100 else "")
                                i += 2
                            else:
                                i += 1
                            
                            response += f"**{conv_count + 1}.** You: {user_msg}\n"
                            if ai_msg:
                                response += f"    Me: {ai_msg}\n\n"
                            
                            conv_count += 1
                        else:
                            i += 1
                
                return {
                    "tool_used": "conversation_memory",
                    "response": response
                }
                
            else:
                # General memory-related query
                return {
                    "tool_used": "conversation_memory", 
                    "response": "🧠 I have conversation memory enabled! I can remember our previous conversations across sessions. You can ask me:\n\n• 'Show memory status' - to see memory statistics\n• 'What did we talk about?' - to see recent conversation history\n• Or just refer to previous conversations naturally!"
                }
                
        except Exception as e:
            return {
                "tool_used": "conversation_memory",
                "response": f"❌ Error accessing conversation memory: {e}"
            }

    def _handle_multi_file_operation(self, query: str) -> Dict[str, Any]:
        """Handle requests that involve both creating and deleting files"""
        print(f"[DEBUG] Multi-file operation request: {query}")
        
        results = []
        
        # First, handle file creation
        create_result = self._handle_file_creation_request(query)
        results.append({
            "operation": "create",
            "result": create_result
        })
        
        # Then, handle file deletion
        delete_result = self._handle_file_deletion_request(query)
        results.append({
            "operation": "delete", 
            "result": delete_result
        })
        
        # Combine results into a comprehensive response
        success_count = sum(1 for r in results if not r["result"].get("error"))
        
        response_parts = []
        for result in results:
            op = result["operation"]
            res = result["result"]
            if "response" in res:
                response_parts.append(f"{op.title()}: {res['response']}")
            elif "error" in res:
                response_parts.append(f"{op.title()}: ❌ {res['error']}")
        
        return {
            "tool_used": "multi_file_operation",
            "query": query,
            "operations": results,
            "response": "\n".join(response_parts)
        }
    
    def _handle_vision_request(self, query: str) -> Dict[str, Any]:
        if 'vision' not in self.tools:
            return {"error": "Vision analysis tool not available"}
        
        # Extract question from query
        if "what" in query.lower():
            question = query
        else:
            question = "What do you see in this image?"
        
        result = self.tools['vision'].analyze_screenshot(question)
        
        return {
            "tool_used": "vision_analysis",
            "question": question,
            "response": result
        }
    
    def _handle_multi_tool_request(self, query: str) -> Dict[str, Any]:
        """Handle requests that need multiple tools (like your MP3 example)"""
        # This is where the magic happens - coordinating multiple tools
        # For now, just a simple example
        
        steps = []
        
        if 'search' in query.lower() and 'screenshot' in query.lower():
            # Example: "Take a screenshot and search for information about what I see"
            
            # Step 1: Take screenshot
            if 'vision' in self.tools:
                vision_result = self.tools['vision'].analyze_screenshot()
                steps.append({
                    "step": 1,
                    "tool": "vision",
                    "result": vision_result
                })
                
                # Step 2: Search based on what we saw
                if vision_result.get('success') and 'search' in self.tools:
                    search_query = f"information about {vision_result.get('analysis', '')[:100]}"
                    search_result = self.tools['search'].quick_search(search_query, max_results=3)
                    steps.append({
                        "step": 2,
                        "tool": "search",
                        "result": search_result
                    })
        
        return {
            "tool_used": "multi_tool_workflow",
            "steps": steps,
            "response": f"Completed {len(steps)} steps to process your request."
        }
    
    def interactive_demo(self):
        """Run an interactive demo"""
        print("\n🤖 AI Companion Interactive Demo")
        print("=" * 50)
        print("Available commands:")
        print("  - 'search [topic]' - Search the web")
        print("  - 'screenshot' - Analyze current screen")
        print("  - 'create file [content]' - Create documents")
        print("  - 'list desktop' - Browse directories")
        print("  - 'translate [text] to [language]' - Translate text")
        print("  - 'help' - Show this help")
        print("  - 'quit' - Exit demo")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n🗣️  You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower() in ['help', '?']:
                    print("Available tools:", list(self.tools.keys()))
                    continue
                
                if not user_input:
                    continue
                
                print("🤖 Processing...")
                result = self.process_command(user_input)
                
                if 'error' in result:
                    print(f"❌ Error: {result['error']}")
                elif 'response' in result:
                    print(f"🤖 AI Companion: {result['response']}")
                    if 'suggestions' in result:
                        print("\n💡 Try these commands:")
                        for suggestion in result['suggestions']:
                            print(f"   - {suggestion}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main entry point"""
    orchestrator = AICompanionOrchestrator()
    orchestrator.interactive_demo()

if __name__ == "__main__":
    main()
