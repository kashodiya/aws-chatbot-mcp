



#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from aws_chatbot.main import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())



