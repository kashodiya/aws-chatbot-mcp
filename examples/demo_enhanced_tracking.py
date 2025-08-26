#!/usr/bin/env python3
"""
Demonstration of Enhanced Conversation Tracking in AWS Chatbot

This script shows how the enhanced conversation tracker captures all
LLM-to-tool interactions, providing complete visibility into the
agent's decision-making process.
"""

import asyncio
import sys
import os
import json

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aws_chatbot.llm_driven_agent import LLMDrivenAWSAgent
from aws_chatbot.conversation_tracker import get_conversation_tracker, reset_conversation_tracker
from aws_chatbot.config import settings

async def demo_enhanced_tracking():
    """Demonstrate the enhanced conversation tracking capabilities"""
    
    print("🔍 Enhanced Conversation Tracking Demo")
    print("=" * 60)
    print(f"🤖 Using LLM: {settings.llm_model}")
    print(f"🔗 LLM URL: {settings.llm_base_url}")
    print(f"📍 AWS Region: {settings.aws_region}")
    print()
    
    # Reset tracking to start fresh
    reset_conversation_tracker()
    
    # Initialize the agent
    agent = LLMDrivenAWSAgent()
    await agent.initialize()
    
    # Get the conversation tracker
    tracker = get_conversation_tracker()
    
    print("🎯 Starting conversation with detailed tracking...")
    print()
    
    # Conversation flow that will generate various types of events
    queries = [
        "List my EC2 instances",
        "How many instances were there?",
        "Show me my S3 buckets",
        "What was the first command I asked about?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"👤 User ({i}): {query}")
        
        # Show tracking stats before processing
        summary = tracker.get_session_summary()
        print(f"📊 Events before: {summary['total_events']}")
        
        # Process the query (this will generate multiple tracking events)
        response = await agent.process_query(query)
        print(f"🤖 Agent: {response}")
        
        # Show tracking stats after processing
        summary = tracker.get_session_summary()
        print(f"📊 Events after: {summary['total_events']}")
        print(f"📈 Event types: {summary.get('event_counts', {})}")
        print("-" * 60)
        print()
    
    print("🔍 Detailed Event Analysis:")
    print("=" * 60)
    
    # Get all events and analyze them
    recent_events = tracker.get_recent_events(100)
    
    print(f"📋 Total Events Captured: {len(recent_events)}")
    print()
    
    # Group events by conversation
    conversations = {}
    for event in recent_events:
        conv_id = event.metadata.get('conversation_id')
        if conv_id:
            if conv_id not in conversations:
                conversations[conv_id] = []
            conversations[conv_id].append(event)
    
    print(f"💬 Conversations Tracked: {len(conversations)}")
    print()
    
    # Show detailed breakdown for each conversation
    for i, (conv_id, events) in enumerate(conversations.items(), 1):
        print(f"🗣️  Conversation {i} (ID: {conv_id[:8]}...):")
        
        # Find the user message to show what this conversation was about
        user_message = next((e for e in events if e.event_type.value == 'user_message'), None)
        if user_message:
            print(f"   Query: {user_message.content}")
        
        # Show event flow
        print(f"   Event Flow ({len(events)} events):")
        for event in events:
            duration = f" ({event.duration_ms:.1f}ms)" if event.duration_ms else ""
            print(f"     • {event.event_type.value}{duration}")
            
            # Show key details for important events
            if event.event_type.value == 'llm_request':
                content = event.content
                print(f"       → Model: {content.get('model', 'N/A')}")
                print(f"       → Messages: {len(content.get('messages', []))}")
                print(f"       → Tools: {len(content.get('tools', []))}")
            
            elif event.event_type.value == 'tool_call':
                content = event.content
                print(f"       → Tool: {content.get('tool_name', 'N/A')}")
                print(f"       → Args: {len(content.get('arguments', {}))}")
            
            elif event.event_type.value == 'command_execution':
                content = event.content
                print(f"       → Command: {content.get('command', 'N/A')}")
            
            elif event.event_type.value == 'agent_reasoning':
                content = event.content
                print(f"       → Type: {content.get('type', 'N/A')}")
                print(f"       → Reasoning: {content.get('reasoning', 'N/A')[:50]}...")
        
        print()
    
    print("📊 Event Type Summary:")
    print("=" * 30)
    
    event_counts = {}
    total_duration = 0
    events_with_duration = 0
    
    for event in recent_events:
        event_type = event.event_type.value
        event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        if event.duration_ms:
            total_duration += event.duration_ms
            events_with_duration += 1
    
    for event_type, count in sorted(event_counts.items()):
        print(f"  {event_type}: {count}")
    
    if events_with_duration > 0:
        avg_duration = total_duration / events_with_duration
        print(f"\n⏱️  Average Event Duration: {avg_duration:.1f}ms")
    
    print()
    
    print("💾 Export Capabilities Demo:")
    print("=" * 40)
    
    # Export session data
    session_export = tracker.export_session()
    export_size = len(session_export)
    print(f"📄 Session Export Size: {export_size:,} characters")
    
    # Show a sample of the exported data
    export_data = json.loads(session_export)
    print(f"📋 Export Structure:")
    print(f"   • Session ID: {export_data['session_id']}")
    print(f"   • Total Events: {len(export_data['events'])}")
    print(f"   • Summary: {export_data['summary']}")
    
    # Export individual conversations
    for i, conv_id in enumerate(conversations.keys(), 1):
        conv_export = tracker.export_conversation(conv_id)
        conv_size = len(conv_export)
        print(f"   • Conversation {i} Export: {conv_size:,} characters")
    
    print()
    
    print("🎉 Enhanced Tracking Demo Complete!")
    print()
    print("Key Features Demonstrated:")
    print("  ✓ Complete LLM request/response tracking")
    print("  ✓ Tool call and response logging")
    print("  ✓ Command execution monitoring")
    print("  ✓ Agent reasoning capture")
    print("  ✓ Performance timing data")
    print("  ✓ Conversation tree structure")
    print("  ✓ Export capabilities")
    print("  ✓ Real-time event statistics")
    print()
    print("🌐 Web Interface:")
    print("  • Main Chat: http://localhost:8000/")
    print("  • Detailed Viewer: http://localhost:8000/conversation-viewer")
    print("  • API Endpoints:")
    print("    - GET /api/conversation/detailed")
    print("    - GET /api/conversation/summary")
    print("    - GET /api/conversation/export")
    print("    - GET /api/conversation/events/filter")

async def demo_api_endpoints():
    """Demonstrate the API endpoints for accessing conversation data"""
    
    print("\n🔌 API Endpoints Demo")
    print("=" * 40)
    
    # This would typically be done via HTTP requests, but we'll simulate it
    tracker = get_conversation_tracker()
    
    print("Available API Endpoints:")
    print()
    
    print("1. GET /api/conversation/detailed")
    print("   → Returns recent conversation events")
    print("   → Parameters: limit, conversation_id")
    print()
    
    print("2. GET /api/conversation/summary")
    print("   → Returns session statistics")
    summary = tracker.get_session_summary()
    print(f"   → Example: {summary}")
    print()
    
    print("3. GET /api/conversation/export")
    print("   → Exports conversation data as JSON")
    print("   → Parameters: conversation_id, format")
    print()
    
    print("4. GET /api/conversation/events/filter")
    print("   → Filters events by type or conversation")
    print("   → Parameters: event_type, conversation_id, limit")
    print()
    
    print("5. POST /api/conversation/clear")
    print("   → Clears all tracking data")
    print()
    
    print("6. GET /health")
    print("   → Enhanced with detailed tracking info")
    print()

if __name__ == "__main__":
    async def main():
        try:
            await demo_enhanced_tracking()
            await demo_api_endpoints()
        except KeyboardInterrupt:
            print("\n👋 Demo interrupted by user")
        except Exception as e:
            print(f"\n❌ Demo error: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(main())

