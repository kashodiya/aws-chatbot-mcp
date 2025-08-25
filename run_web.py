


#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import uvicorn
from aws_chatbot.config import settings

if __name__ == "__main__":
    print("🚀 Starting AWS Chatbot Web Server...")
    print(f"🌐 Server: http://{settings.host}:{settings.port}")
    print(f"📍 Region: {settings.aws_region}")
    print(f"🤖 Model: {settings.llm_model}")
    print(f"🔒 Read-only: {settings.read_operations_only}")
    print("-" * 50)
    
    uvicorn.run(
        "aws_chatbot.web_app:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        reload_dirs=["src"]
    )


