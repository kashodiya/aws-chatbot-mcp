


#!/usr/bin/env python3

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from aws_chatbot.config import settings
from aws_chatbot.llm_driven_agent import LLMDrivenAWSAgent as AWSAgent

async def main():
    """Main entry point for the AWS chatbot CLI"""
    print("🚀 Starting AWS Chatbot...")
    print(f"📍 Region: {settings.aws_region}")
    print(f"🔧 Profile: {settings.aws_profile_name}")
    print(f"🤖 Model: {settings.llm_model}")
    print(f"🔒 Read-only: {settings.read_operations_only}")
    print("-" * 50)
    
    # Initialize the AWS agent
    try:
        agent = AWSAgent()
        await agent.start()
        
        print("✅ AWS Agent initialized successfully!")
        print("💬 You can now interact with AWS services using natural language.")
        print("Type 'quit' or 'exit' to stop.\n")
        
        while True:
            try:
                # Get user input
                user_input = input("🗣️  You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Process the query
                print("🤔 AWS Assistant: ", end="", flush=True)
                response = await agent.process_query(user_input)
                print(response)
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Failed to initialize AWS Agent: {e}")
        print("Please check your configuration and try again.")
        sys.exit(1)
    finally:
        if 'agent' in locals():
            await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())


