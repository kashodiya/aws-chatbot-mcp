#!/usr/bin/env python3

import sys
import asyncio
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aws_chatbot.simple_agent import SimpleAWSAgent

async def demo():
    """Demo the AWS chatbot functionality"""
    print("🚀 AWS Chatbot Demo")
    print("=" * 50)
    
    # Initialize the agent
    agent = SimpleAWSAgent()
    await agent.start()
    
    print("✅ Agent initialized successfully!")
    print("\nTry these sample queries:")
    
    # Sample queries
    queries = [
        "List EC2 instances",
        "Show S3 buckets", 
        "List RDS databases",
        "Show Lambda functions",
        "What can you help me with?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. Query: '{query}'")
        print("-" * 40)
        
        # Process the query
        response = await agent.process_query(query)
        print(f"Response: {response}")
        
        # Show suggested commands
        suggestions = await agent.suggest_commands(query)
        if suggestions:
            print(f"\nSuggested commands:")
            for suggestion in suggestions[:2]:  # Show first 2 suggestions
                if "error" not in suggestion:
                    print(f"  • {suggestion['command']} ({suggestion['service']})")
        
        print()
    
    print("=" * 50)
    print("🎉 Demo completed!")
    print("\nTo use the full application:")
    print("1. Configure your .env file with proper AWS credentials")
    print("2. Run 'uv run run_web.py' for the web interface")
    print("3. Run 'uv run run_cli.py' for the CLI interface")

if __name__ == "__main__":
    asyncio.run(demo())
