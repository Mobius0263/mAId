"""
Improved file creation with topic-agnostic content generation
This fixes the issues with F/A-18 hardcoding and makes the system adaptable to any topic
"""

def improved_content_prompt(user_input, file_type, relevant_info):
    """Generate a topic-agnostic content prompt for AI"""
    return f"""Create professional content for a {file_type.upper()} file based on: "{user_input}"

**Information from our conversation:**
{relevant_info}

**Instructions:**
- Focus ONLY on the topic/information the user wants documented
- Use appropriate formatting for {file_type.upper()} files
- Create clean, professional content without any chat messages or assistant responses
- Structure the information logically and professionally
- Adapt the format to best present the specific topic being discussed

Generate ONLY the file content - no explanations, no meta-text:"""

def extract_factual_content_improved(conversation_history, user_request):
    """Extract factual content without topic-specific hardcoding"""
    if not conversation_history:
        return user_request
    
    factual_content = []
    
    for msg in conversation_history[-8:]:  # Last 8 messages
        role = msg.get("role", "")
        content = msg.get("content", "")
        
        # Include user questions and requests
        if role == "user" and content and len(content.strip()) > 10:
            factual_content.append(f"User request: {content}")
        
        # Extract factual information from assistant responses
        elif role == "assistant":
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                
                # Skip conversational elements
                if any(phrase in line.lower() for phrase in [
                    "i found", "here's what", "let me", "i can help", "i'll", 
                    "successfully created", "location:", "assistant", "based on our",
                    "search results summary", "this information was found"
                ]):
                    continue
                
                # Include lines with structured content (any topic)
                if any(indicator in line for indicator in ["**", "##", "###", "-", "•", ":"]):
                    if not line.startswith(("I ", "Here", "Let", "You", "This", "Based")):
                        factual_content.append(line)
                # Include lines that look like specifications or data
                elif any(term in line.lower() for term in [":", "specifications", "features", "description"]):
                    if not line.startswith(("I ", "Here", "Let", "You", "This", "Based")):
                        factual_content.append(line)
    
    return '\n'.join(factual_content) if factual_content else user_request

def extract_search_terms_generic(user_input):
    """Extract search terms without hardcoded topic references"""
    import re
    
    # Extract quoted terms first
    quoted_terms = re.findall(r'["\']([^"\']+)["\']', user_input)
    if quoted_terms:
        return f"*{quoted_terms[0]}*"
    
    # Extract terms after "named" or "called"
    filename_match = re.search(r'(?:named|called)\s+([^\s]+)', user_input, re.IGNORECASE)
    if filename_match:
        return f"*{filename_match.group(1)}*"
    
    # Extract key terms from the search query
    search_terms = re.findall(r'\b[a-zA-Z]{3,}\b', user_input.lower())
    # Filter out common words
    common_words = {'find', 'search', 'look', 'for', 'files', 'named', 'called', 'document', 'file', 'the', 'and', 'with'}
    key_terms = [term for term in search_terms if term not in common_words]
    
    if key_terms:
        return f"*{key_terms[0]}*"
    
    return "*"

# This shows the improved approach that's adaptable to any topic
print("Enhanced content generation - topic agnostic and professionally formatted")
