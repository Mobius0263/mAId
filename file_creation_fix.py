"""
Enhanced file creation with context-aware content generation
Fix for avoiding assistant responses in file content
"""

def extract_factual_content(conversation_history, user_request):
    """Extract only factual information from conversation, excluding AI responses"""
    if not conversation_history:
        return user_request
    
    factual_content = []
    
    for msg in conversation_history[-8:]:  # Last 8 messages
        role = msg.get("role", "")
        content = msg.get("content", "")
        
        # Include user questions
        if role == "user" and content and len(content.strip()) > 10:
            factual_content.append(f"User request: {content}")
        
        # Extract only factual information from assistant responses
        elif role == "assistant":
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                
                # Skip conversational parts
                if any(phrase in line.lower() for phrase in [
                    "i found", "here's what", "let me", "i can help", "i'll", 
                    "successfully created", "location:", "assistant", "based on our"
                ]):
                    continue
                
                # Include factual information (specifications, data, etc.)
                if any(indicator in line for indicator in ["**", "##", "###", "-", "•", ":"]):
                    if not line.startswith(("I ", "Here", "Let", "You", "This", "Based")):
                        factual_content.append(line)
    
    return '\n'.join(factual_content) if factual_content else user_request

def generate_clean_content_prompt(user_input, file_type, relevant_info):
    """Generate a clean prompt for AI content generation"""
    return f"""Create professional content for a {file_type.upper()} file based on: "{user_input}"

Context: {relevant_info}

Requirements:
- Focus ONLY on the requested topic/information
- Use proper formatting for {file_type.upper()} files
- NO chat messages, assistant responses, or meta-commentary
- Professional document structure
- Include only factual content and information

Generate the file content:"""

# This patch can be integrated into the main smart_orchestrator.py file
