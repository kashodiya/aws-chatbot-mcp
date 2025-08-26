


#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import uvicorn
import os
from aws_chatbot.config import settings

if __name__ == "__main__":
    print("🚀 [RUN_WEB] Starting AWS Chatbot Web Server initialization...")
    print(f"🚀 [RUN_WEB] Current working directory: {os.getcwd()}")
    print(f"🚀 [RUN_WEB] Python path: {sys.path[:3]}...")
    
    # Force the correct model
    print("🚀 [RUN_WEB] Setting environment variables...")
    os.environ["LLM_MODEL"] = "US Claude 3.7 Sonnet By Anthropic (Served via LiteLLM)"
    os.environ["LLM_BASE_URL"] = "http://ec2-98-86-51-242.compute-1.amazonaws.com:7177"
    os.environ["LLM_API_KEY"] = "sk-123123123"
    
    print("🚀 [RUN_WEB] Environment variables set:")
    print(f"🚀 [RUN_WEB] LLM_MODEL: {os.environ.get('LLM_MODEL')}")
    print(f"🚀 [RUN_WEB] LLM_BASE_URL: {os.environ.get('LLM_BASE_URL')}")
    print(f"🚀 [RUN_WEB] LLM_API_KEY: {os.environ.get('LLM_API_KEY')}")
    
    print("🚀 Starting AWS Chatbot Web Server...")
    print(f"🌐 Server: http://{settings.host}:{settings.port}")
    print(f"📍 Region: {settings.aws_region}")
    print(f"🤖 Model: {os.environ.get('LLM_MODEL', settings.llm_model)}")
    print(f"🔒 Read-only: {settings.read_operations_only}")
    print("-" * 50)
    
    print("🚀 [RUN_WEB] Starting uvicorn server...")
    uvicorn.run(
        "aws_chatbot.web_app:app",
        host="0.0.0.0",
        port=54491,
        reload=True,
        reload_dirs=["src"]
    )


