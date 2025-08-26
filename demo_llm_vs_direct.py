#!/usr/bin/env python3
"""
Demonstration script showing the difference between:
1. Direct command execution (old approach - WRONG)
2. LLM-driven decision making (new approach - CORRECT)
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from aws_chatbot.simple_agent import SimpleAWSAgent
from aws_chatbot.llm_driven_agent import LLMDrivenAWSAgent
from aws_chatbot.config import settings

async def demo_old_approach():
    """Demonstrate the OLD (incorrect) approach - direct command execution"""
    print("=" * 60)
    print("🚫 OLD APPROACH: Direct Command Execution (INCORRECT)")
    print("=" * 60)
    print("This approach uses hardcoded keyword matching and directly")
    print("executes AWS CLI commands without LLM reasoning.\n")
    
    agent = SimpleAWSAgent()
    await agent.start()
    
    test_queries = [
        "Show me my EC2 instances",
        "What S3 buckets do I have?",
        "Tell me about my Lambda functions",
        "How many databases are running?",
        "What's the weather like?"  # This will show the limitation
    ]
    
    for query in test_queries:
        print(f"👤 User: {query}")
        response = await agent.process_query(query)
        print(f"🤖 Agent: {response[:200]}{'...' if len(response) > 200 else ''}")
        print("-" * 40)
    
    await agent.stop()

async def demo_new_approach():
    """Demonstrate the NEW (correct) approach - LLM-driven decision making"""
    print("\n" + "=" * 60)
    print("✅ NEW APPROACH: LLM-Driven Decision Making (CORRECT)")
    print("=" * 60)
    print("This approach uses the LLM to understand queries and decide")
    print("what AWS commands to execute based on natural language.\n")
    
    agent = LLMDrivenAWSAgent()
    await agent.start()
    
    test_queries = [
        "Show me my EC2 instances",
        "What S3 buckets do I have?",
        "Tell me about my Lambda functions",
        "How many databases are running?",
        "What's the weather like?"  # This will show better handling
    ]
    
    for query in test_queries:
        print(f"👤 User: {query}")
        response = await agent.process_query(query)
        print(f"🤖 Agent: {response[:200]}{'...' if len(response) > 200 else ''}")
        print("-" * 40)
    
    await agent.stop()

async def demo_llm_command_suggestions():
    """Demonstrate how LLM suggests commands instead of hardcoded logic"""
    print("\n" + "=" * 60)
    print("🧠 LLM COMMAND SUGGESTIONS")
    print("=" * 60)
    print("See how the LLM suggests appropriate AWS CLI commands\n")
    
    agent = LLMDrivenAWSAgent()
    await agent.start()
    
    test_queries = [
        "I want to see all my running servers",
        "Show me storage usage",
        "List all my serverless functions",
        "What networking resources do I have?",
        "Show me my database backups"
    ]
    
    for query in test_queries:
        print(f"👤 User: {query}")
        suggestions = await agent.suggest_commands(query)
        print("🧠 LLM Suggested Commands:")
        for suggestion in suggestions[:3]:  # Show first 3 suggestions
            if "error" not in suggestion:
                print(f"   • {suggestion.get('command', 'N/A')}")
                print(f"     └─ {suggestion.get('description', 'N/A')}")
        print("-" * 40)
    
    await agent.stop()

async def main():
    """Main demonstration function"""
    print("🚀 AWS Chatbot: LLM vs Direct Command Execution Demo")
    print(f"🤖 Using LLM: {settings.llm_model}")
    print(f"🔗 LLM URL: {settings.llm_base_url}")
    print(f"📍 AWS Region: {settings.aws_region}")
    print()
    
    try:
        # Demo the old (incorrect) approach
        await demo_old_approach()
        
        # Demo the new (correct) approach
        await demo_new_approach()
        
        # Demo LLM command suggestions
        await demo_llm_command_suggestions()
        
        print("\n" + "=" * 60)
        print("📝 SUMMARY")
        print("=" * 60)
        print("❌ OLD APPROACH:")
        print("   • Uses hardcoded keyword matching")
        print("   • Directly executes commands without reasoning")
        print("   • Limited to predefined patterns")
        print("   • Cannot handle complex or ambiguous queries")
        print()
        print("✅ NEW APPROACH:")
        print("   • Uses LLM to understand natural language")
        print("   • LLM decides what commands to execute")
        print("   • Can handle complex and varied queries")
        print("   • Provides intelligent responses and explanations")
        print("   • Follows the MCP agent pattern correctly")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
