"""
Quick Test - Essential functionality check
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "src"))

def quick_test():
    """Quick test of core functionality"""
    print("⚡ AI Companion Quick Test")
    print("=" * 30)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Environment
    try:
        from dotenv import load_dotenv
        import os
        load_dotenv()
        
        if os.getenv('GEMINI_API_KEY') and os.getenv('BRAVE_SEARCH_API_KEY'):
            print("✅ Environment configuration")
            tests_passed += 1
        else:
            print("❌ Environment configuration")
    except Exception as e:
        print(f"❌ Environment configuration: {e}")
    
    # Test 2: Core system
    try:
        from core.smart_orchestrator import SmartAIOrchestrator
        orchestrator = SmartAIOrchestrator()
        
        if orchestrator.brain and len(orchestrator.tools) > 0:
            print("✅ Core system")
            tests_passed += 1
        else:
            print("❌ Core system")
    except Exception as e:
        print(f"❌ Core system: {e}")
    
    # Test 3: Memory
    try:
        from core.memory_manager import get_memory_manager
        memory = get_memory_manager()
        stats = memory.get_memory_stats()
        
        if stats['memory_enabled']:
            print("✅ Memory system")
            tests_passed += 1
        else:
            print("❌ Memory system")
    except Exception as e:
        print(f"❌ Memory system: {e}")
    
    # Test 4: Basic conversation
    try:
        result = orchestrator.process_command("Hello! Test message.")
        
        if result.get('response'):
            print("✅ Basic conversation")
            tests_passed += 1
        else:
            print("❌ Basic conversation")
    except Exception as e:
        print(f"❌ Basic conversation: {e}")
    
    # Summary
    print(f"\n🎯 Result: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All systems operational!")
    else:
        print("⚠️ Some issues detected. Run 'python test_suite.py' for details.")

if __name__ == "__main__":
    quick_test()
