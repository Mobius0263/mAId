"""
🚨 CRITICAL FIX APPLIED - NO MORE META-TEXT IN FILES!
=======================================================

PROBLEM IDENTIFIED:
The AI was writing ABOUT the content instead of writing the ACTUAL content

EXAMPLE OF THE PROBLEM:
❌ BAD: "This document contains the detailed specifications of the F-22 Raptor from our recent conversation"
✅ GOOD: "# F-22 Raptor Specifications
         Length: 62 ft 1 in (18.90 m)
         Wingspan: 44 ft 6 in (13.56 m)
         Height: 16 ft 8 in (5.08 m)"

THE FIX:
1. AGGRESSIVE CONTENT EXTRACTION - Captures ALL technical data
2. EXPLICIT PROMPT INSTRUCTIONS - Forces AI to write actual content
3. NO META-TEXT ALLOWED - Banned phrases like "This document contains..."

NEW PROMPT STRUCTURE:
"CRITICAL INSTRUCTIONS:
1. DO NOT write about what you're going to do - JUST DO IT
2. DO NOT say 'This document contains...' - PUT THE ACTUAL CONTENT
3. USE THE EXACT specifications, measurements, and data from the conversation
4. START IMMEDIATELY with the title and then the actual information"

WHAT GETS EXTRACTED NOW:
✅ • Length: 62 ft 1 in (18.90 m)
✅ • Wingspan: 44 ft 6 in (13.56 m)  
✅ • Height: 16 ft 8 in (5.08 m)
✅ • Empty Weight: 43,340 lb (19,700 kg)
✅ • Engine: 2× Pratt & Whitney F119-PW-100
✅ • Maximum Speed: Mach 2.25

WHAT GETS FILTERED OUT:
❌ "I found some information..."
❌ "Here's what I discovered..."
❌ "This information was found by searching..."
❌ "Based on our conversation..."

RESULT:
Files will now contain THE ACTUAL SPECIFICATIONS, not descriptions of them!
"""
