"""
Intelligent Tool Selection System
Uses AI reasoning to select appropriate tools based on user intent
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ToolCapability:
    """Description of what a tool can do"""
    name: str
    description: str
    capabilities: List[str]
    example_uses: List[str]
    when_to_use: str
    when_not_to_use: str


class IntelligentToolSelector:
    """AI-powered tool selection based on user intent"""
    
    def __init__(self):
        """Initialize the intelligent tool selector"""
        self.tool_capabilities = self._define_tool_capabilities()
    
    def _define_tool_capabilities(self) -> Dict[str, ToolCapability]:
        """Define what each tool can do and when to use it - Enhanced with PyGPT features"""
        return {
            # === ENHANCED FILE MANAGEMENT ===
            "files": ToolCapability(
                name="files",
                description="Advanced file management with search, compression, backup, and batch operations",
                capabilities=[
                    "Advanced file search with multiple criteria",
                    "Batch file operations (copy, move, delete)",
                    "File compression and extraction (ZIP, TAR)",
                    "File backup and recovery",
                    "Directory tree visualization",
                    "File bookmarks and quick access",
                    "Disk usage analysis",
                    "File metadata and hash calculation"
                ],
                example_uses=[
                    "Find all PDF files modified this week",
                    "Compress my project folders",
                    "Backup important documents",
                    "Show directory tree of my workspace",
                    "Search for files containing specific text"
                ],
                when_to_use="When user needs advanced file operations, organization, or management beyond basic file tasks",
                when_not_to_use="When looking for information online or when simple file tasks are sufficient"
            ),
            
            # === CHAT WITH FILES ===
            "chat_files": ToolCapability(
                name="chat_files",
                description="Intelligent conversation with document contents using embeddings and RAG",
                capabilities=[
                    "Index documents for intelligent search",
                    "Chat with PDF, DOCX, and text files",
                    "Semantic search across document contents",
                    "Answer questions based on document content",
                    "Summarize and analyze indexed documents",
                    "Multi-document knowledge synthesis"
                ],
                example_uses=[
                    "What does my research paper say about AI ethics?",
                    "Summarize the main points from my meeting notes",
                    "Find references to 'machine learning' in my documents",
                    "Answer questions about my project documentation"
                ],
                when_to_use="When user wants to converse with or get insights from document contents",
                when_not_to_use="When user wants basic file management or web search"
            ),
            
            # === AUDIO PROCESSING ===
            "audio": ToolCapability(
                name="audio",
                description="Text-to-speech and speech-to-text processing with multiple providers",
                capabilities=[
                    "Convert text to speech with natural voices",
                    "Multiple TTS providers (Edge TTS, OpenAI)",
                    "Speech-to-text transcription",
                    "Voice selection and customization",
                    "Audio file processing",
                    "Multi-language support"
                ],
                example_uses=[
                    "Read this text aloud",
                    "Convert my notes to speech",
                    "Transcribe this audio recording",
                    "Generate speech from my document",
                    "Create audio version of my text"
                ],
                when_to_use="When user wants text-to-speech, speech-to-text, or audio processing",
                when_not_to_use="When no audio processing is needed"
            ),
            
            # === CODE INTERPRETER ===
            "code": ToolCapability(
                name="code",
                description="Secure code execution environment supporting multiple programming languages",
                capabilities=[
                    "Execute Python, JavaScript, Bash, PowerShell code",
                    "Data visualization and plotting",
                    "Secure sandboxed execution",
                    "Code analysis and debugging",
                    "Package installation and management",
                    "Output capture and formatting"
                ],
                example_uses=[
                    "Run this Python script",
                    "Execute JavaScript code",
                    "Create a data visualization",
                    "Test this code snippet",
                    "Calculate mathematical formulas"
                ],
                when_to_use="When user wants to execute code, perform calculations, or create visualizations",
                when_not_to_use="When no code execution is required"
            ),
            
            # === DOCUMENT PROCESSING ===
            "documents": ToolCapability(
                name="documents",
                description="Advanced document analysis for PDF, DOCX, Excel, PowerPoint, and other formats",
                capabilities=[
                    "Extract text from PDFs and Word documents",
                    "Analyze spreadsheet data and charts",
                    "Process PowerPoint presentations",
                    "Document summarization and analysis",
                    "Key point extraction",
                    "Multi-format document support"
                ],
                example_uses=[
                    "Analyze this PDF report",
                    "Summarize my Word document",
                    "Extract data from Excel spreadsheet",
                    "Process PowerPoint presentation content",
                    "Get key points from documents"
                ],
                when_to_use="When user wants to analyze, summarize, or extract information from documents",
                when_not_to_use="When simple file operations are sufficient or when web search is needed"
            ),
            
            # === API INTEGRATIONS ===
            "api": ToolCapability(
                name="api",
                description="Access external APIs for weather, news, GitHub, currency, and translation services",
                capabilities=[
                    "Weather information and forecasts",
                    "Latest news and article search",
                    "GitHub repository search",
                    "Currency exchange rates",
                    "Language translation",
                    "Generic REST API requests"
                ],
                example_uses=[
                    "What's the weather in Tokyo?",
                    "Get latest tech news",
                    "Search GitHub for Python projects",
                    "Current USD to EUR exchange rate",
                    "Translate text to Spanish"
                ],
                when_to_use="When user needs real-time information from external services",
                when_not_to_use="When information is available locally or through web search"
            ),
            
            # === MULTI-MODEL MANAGEMENT ===
            "models": ToolCapability(
                name="models",
                description="Intelligent AI model switching and management across multiple providers",
                capabilities=[
                    "Switch between AI models (Gemini, GPT-4, Claude)",
                    "Auto-select best model for tasks",
                    "Model performance statistics",
                    "Context length optimization",
                    "Cost and speed optimization",
                    "Local and cloud model support"
                ],
                example_uses=[
                    "Switch to GPT-4 for this task",
                    "Use Claude for writing",
                    "Show available AI models",
                    "Get model usage statistics",
                    "Auto-select best model for coding"
                ],
                when_to_use="When user wants to change AI models or optimize model selection",
                when_not_to_use="When current model is sufficient for the task"
            ),
            
            # === ENHANCED VISION ===
            "vision": ToolCapability(
                name="vision",
                description="Advanced image analysis with multiple vision models and comprehensive features",
                capabilities=[
                    "Multi-model image analysis (GPT-4V, Gemini Vision, BLIP-2)",
                    "Object detection and recognition",
                    "OCR and text extraction",
                    "Face detection and analysis",
                    "Color analysis and dominant colors",
                    "Image annotation and markup",
                    "Batch image processing"
                ],
                example_uses=[
                    "Analyze this screenshot",
                    "Describe what's in this image",
                    "Extract text from this picture",
                    "Detect objects in photos",
                    "Get color palette from image"
                ],
                when_to_use="When user needs visual analysis, image understanding, or screenshot processing",
                when_not_to_use="When no visual content is involved"
            ),
            
            # === WEB SEARCH ===
            "search": ToolCapability(
                name="search",
                description="Search the internet for information, articles, news, and online resources",
                capabilities=[
                    "Find current information and news",
                    "Research topics, concepts, and facts",
                    "Look up definitions and explanations",
                    "Find tutorials and how-to guides",
                    "Get recent updates on topics",
                    "Find websites, articles, and online resources"
                ],
                example_uses=[
                    "What's the latest news about AI?",
                    "How does machine learning work?",
                    "Find information about Python programming",
                    "Search for restaurants near me",
                    "Research current events"
                ],
                when_to_use="When user wants information from the internet, current events, or online research",
                when_not_to_use="When looking for files on the computer or when local tools are more appropriate"
            ),
            
            # === MEMORY ===
            "memory": ToolCapability(
                name="memory",
                description="Access and manage conversation history and memory across sessions",
                capabilities=[
                    "Retrieve conversation history",
                    "Show memory statistics",
                    "Remember previous discussions",
                    "Provide conversation summaries",
                    "Track ongoing projects and context"
                ],
                example_uses=[
                    "What did we discuss yesterday?",
                    "Show my conversation history",
                    "Remember this for later",
                    "What was I working on last time?",
                    "Show memory statistics"
                ],
                when_to_use="When user wants to recall previous conversations or manage memory",
                when_not_to_use="When asking new questions unrelated to conversation history"
            ),
            
            # === CHARACTER CHAT ===
            "character_chat": ToolCapability(
                name="character_chat",
                description="General conversation with AI character personalities",
                capabilities=[
                    "Natural conversation",
                    "Character-driven responses",
                    "Context-aware dialogue",
                    "Personality-based interactions",
                    "Casual chat and discussion"
                ],
                example_uses=[
                    "How are you today?",
                    "Tell me a joke",
                    "What do you think about...",
                    "Let's have a conversation",
                    "I need someone to talk to"
                ],
                when_to_use="When user wants general conversation or no specific tool is needed",
                when_not_to_use="When user has a specific task that requires a specialized tool"
            )
        }
    
    def analyze_user_intent(self, user_input: str, conversation_context: List[Dict] = None) -> Dict[str, Any]:
        """
        Analyze user input to determine intent and select appropriate tool
        
        Args:
            user_input: The user's request
            conversation_context: Recent conversation for context
            
        Returns:
            Analysis result with tool selection and reasoning
        """
        
        # Create the analysis prompt
        tools_description = self._create_tools_description()
        
        analysis_prompt = f"""Analyze this user request and determine the best tool to use:

USER REQUEST: "{user_input}"

AVAILABLE TOOLS:
{tools_description}

ANALYSIS INSTRUCTIONS:
1. Carefully read the user's request
2. Consider what they're actually trying to accomplish
3. Think about the context and likely intent
4. Choose the most appropriate tool based on the capabilities
5. Provide clear reasoning for your choice

Important context clues:
- "Search for files" or "find files" = USE FILES TOOL (local computer search)
- "Search for information" or "look up" = USE WEB SEARCH (internet search)
- File paths, folder names, file extensions = FILES TOOL
- "What's on my screen" or "screenshot" = VISION TOOL
- "What did we discuss" or conversation history = MEMORY TOOL
- General questions, conversation, advice = CHARACTER CHAT

Respond with this exact JSON format:
{{
    "selected_tool": "tool_name",
    "confidence": 0.95,
    "reasoning": "Clear explanation of why this tool was selected",
    "user_intent": "What the user is trying to accomplish",
    "parameters": {{
        "key": "value for tool execution"
    }}
}}"""

        return {
            "analysis_prompt": analysis_prompt,
            "tools_available": list(self.tool_capabilities.keys())
        }
    
    def _create_tools_description(self) -> str:
        """Create a description of all available tools for the AI"""
        descriptions = []
        
        for tool_name, capability in self.tool_capabilities.items():
            desc = f"""
**{capability.name} ({tool_name})**
- Purpose: {capability.description}
- When to use: {capability.when_to_use}
- When NOT to use: {capability.when_not_to_use}
- Examples: {', '.join(capability.example_uses[:3])}
"""
            descriptions.append(desc)
        
        return "\n".join(descriptions)
    
    def get_tool_info(self, tool_name: str) -> Optional[ToolCapability]:
        """Get detailed information about a specific tool"""
        return self.tool_capabilities.get(tool_name)
    
    def list_all_tools(self) -> Dict[str, str]:
        """Get a summary of all available tools"""
        return {
            name: cap.description 
            for name, cap in self.tool_capabilities.items()
        }


# Global tool selector instance  
_tool_selector = None

def get_tool_selector() -> IntelligentToolSelector:
    """Get the global tool selector instance"""
    global _tool_selector
    if _tool_selector is None:
        _tool_selector = IntelligentToolSelector()
    return _tool_selector
