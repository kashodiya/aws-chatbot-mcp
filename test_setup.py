


#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all imports work correctly"""
    try:
        print("Testing imports...")
        
        # Test configuration
        from aws_chatbot.config import settings
        print("✅ Configuration loaded successfully")
        print(f"   - AWS Region: {settings.aws_region}")
        print(f"   - LLM Model: {settings.llm_model}")
        
        # Test AWS agent import
        from aws_chatbot.aws_agent import AWSAgent
        print("✅ AWS Agent imported successfully")
        
        # Test web app import
        from aws_chatbot.web_app import app
        print("✅ Web app imported successfully")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test configuration with example values"""
    try:
        print("\nTesting configuration...")
        
        # Set some example environment variables
        os.environ["LLM_MODEL"] = "test-model"
        os.environ["LLM_BASE_URL"] = "http://localhost:8000"
        os.environ["LLM_API_KEY"] = "test-key"
        os.environ["AWS_REGION"] = "us-west-2"
        
        # Reload settings
        from aws_chatbot.config import Settings
        test_settings = Settings()
        
        print(f"✅ Model: {test_settings.llm_model}")
        print(f"✅ Base URL: {test_settings.llm_base_url}")
        print(f"✅ Region: {test_settings.aws_region}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing AWS Chatbot Setup")
    print("=" * 40)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test configuration
    if not test_config():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 All tests passed! Setup is working correctly.")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and configure your settings")
        print("2. Run 'uv run run_web.py' to start the web server")
        print("3. Run 'uv run run_cli.py' to start the CLI interface")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()


