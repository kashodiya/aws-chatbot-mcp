#!/usr/bin/env python3
"""
Demonstration of the Memory Feature in AWS Chatbot

This script shows how the LLM-driven AWS agent uses conversation memory
to provide context-aware responses and handle follow-up questions.
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from aws_chatbot.llm_driven_agent import LLMDrivenAWSAgent
from aws_chatbot.config import settings

async def demo_memory_feature():
    """Demonstrate the memory feature with a conversation flow"""
    
    print("🧠 AWS Chatbot Memory Feature Demo")
    print("=" * 50)
    print(f"🤖 Using LLM: {settings.llm_model}")
    print(f"🔗 LLM URL: {settings.llm_base_url}")
    print(f"📍 AWS Region: {settings.aws_region}")
    print()
    
    # Initialize the agent
    agent = LLMDrivenAWSAgent()
    await agent.initialize()
    
    # Conversation flow demonstrating memory
    conversation_flow = [
        "List my EC2 instances",
        "How many instances were there?",
        "Show me my S3 buckets", 
        "What was the first command I asked about?",
        "Can you show me more details about the instances?",
        "What services have I asked about so far?"
    ]
    
    print("🗣️  Starting conversation with memory-aware responses...")
    print()
    
    for i, query in enumerate(conversation_flow, 1):
        print(f"👤 User ({i}): {query}")
        
        # Get memory stats before processing
        memory_stats = agent.get_memory_stats()
        print(f"📊 Memory: {memory_stats['total_interactions']} interactions, {len(memory_stats['recent_commands'])} recent commands")
        
        # Process the query
        response = await agent.process_query(query)
        print(f"🤖 Agent: {response}")
        
        # Show memory context after processing
        if i > 1:  # After first interaction
            print(f"🧠 Context: {memory_stats['context_summary'][:100]}...")
        
        print("-" * 50)
        print()
    
    print("📈 Final Memory Statistics:")
    final_stats = agent.get_memory_stats()
    print(f"   Total Interactions: {final_stats['total_interactions']}")
    print(f"   Recent Commands: {final_stats['recent_commands']}")
    print()
    
    print("🔄 Testing Memory Persistence...")
    print("   Asking follow-up question that requires context...")
    
    follow_up = "What was the output of the EC2 command?"
    print(f"👤 User: {follow_up}")
    response = await agent.process_query(follow_up)
    print(f"🤖 Agent: {response}")
    print()
    
    print("🧹 Testing Memory Clear...")
    agent.clear_memory()
    cleared_stats = agent.get_memory_stats()
    print(f"   Memory after clear: {cleared_stats['total_interactions']} interactions")
    
    # Test that context is lost after clearing
    print("   Asking same follow-up question after memory clear...")
    print(f"👤 User: {follow_up}")
    response = await agent.process_query(follow_up)
    print(f"🤖 Agent: {response}")
    print()
    
    print("✅ Memory Feature Demo Complete!")
    print()
    print("Key Memory Features Demonstrated:")
    print("  ✓ Conversation history tracking")
    print("  ✓ Context-aware follow-up responses")
    print("  ✓ Command execution memory")
    print("  ✓ Memory statistics and management")
    print("  ✓ Memory clearing functionality")

async def demo_command_suggestions():
    """Demonstrate memory-aware command suggestions"""
    
    print("\n🎯 Memory-Aware Command Suggestions Demo")
    print("=" * 50)
    
    agent = LLMDrivenAWSAgent()
    await agent.initialize()
    
    # First, establish some context
    print("👤 User: List my EC2 instances")
    await agent.process_query("List my EC2 instances")
    
    print("👤 User: Show my S3 buckets")  
    await agent.process_query("Show my S3 buckets")
    
    # Now test context-aware suggestions
    print("\n🧠 Getting suggestions with conversation context...")
    
    context_queries = [
        "show me more details about those instances",
        "how can I stop them?",
        "what about the buckets I saw earlier?"
    ]
    
    for query in context_queries:
        print(f"\n👤 User: {query}")
        suggestions = await agent.suggest_commands(query)
        
        print("💡 Suggested Commands:")
        for i, suggestion in enumerate(suggestions[:3], 1):  # Show top 3
            if 'error' not in suggestion:
                context_aware = suggestion.get('context_aware', False)
                context_indicator = "🧠" if context_aware else "📝"
                print(f"   {i}. {context_indicator} {suggestion['command']}")
                print(f"      {suggestion['description']}")
                print(f"      Service: {suggestion['service']}")
            else:
                print(f"   ❌ {suggestion['error']}")

if __name__ == "__main__":
    async def main():
        try:
            await demo_memory_feature()
            await demo_command_suggestions()
        except KeyboardInterrupt:
            print("\n👋 Demo interrupted by user")
        except Exception as e:
            print(f"\n❌ Demo error: {e}")
    
    asyncio.run(main())
