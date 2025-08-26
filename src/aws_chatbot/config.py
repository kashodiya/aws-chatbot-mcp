import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

print("🔧 [CONFIG] Starting configuration loading...")
print(f"🔧 [CONFIG] Current working directory: {os.getcwd()}")
print(f"🔧 [CONFIG] Looking for .env file at: {os.path.join(os.getcwd(), '.env')}")
print(f"🔧 [CONFIG] .env file exists: {os.path.exists('.env')}")

load_dotenv()
print("🔧 [CONFIG] Environment variables loaded from .env file")

class Settings(BaseSettings):
    # LLM Configuration
    llm_model: str = Field(default="US Claude 3.7 Sonnet By Anthropic (Served via LiteLLM)", env="LLM_MODEL")
    llm_base_url: Optional[str] = Field(default=None, env="LLM_BASE_URL")
    llm_api_key: str = Field(default="", env="LLM_API_KEY")
    
    # AWS Configuration
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    aws_profile_name: str = Field(default="default", env="AWS_API_MCP_PROFILE_NAME")
    read_operations_only: bool = Field(default=False, env="READ_OPERATIONS_ONLY")
    require_mutation_consent: bool = Field(default=False, env="REQUIRE_MUTATION_CONSENT")
    
    # Web Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=54491, env="PORT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

print("🔧 [CONFIG] Creating Settings instance...")
settings = Settings()

print("🔧 [CONFIG] Settings loaded successfully:")
print(f"🔧 [CONFIG] LLM Model: {settings.llm_model}")
print(f"🔧 [CONFIG] LLM Base URL: {settings.llm_base_url}")
print(f"🔧 [CONFIG] LLM API Key: {'***' + settings.llm_api_key[-4:] if settings.llm_api_key else 'Not set'}")
print(f"🔧 [CONFIG] AWS Region: {settings.aws_region}")
print(f"🔧 [CONFIG] AWS Profile: {settings.aws_profile_name}")
print(f"🔧 [CONFIG] Read Only: {settings.read_operations_only}")
print(f"🔧 [CONFIG] Host: {settings.host}")
print(f"🔧 [CONFIG] Port: {settings.port}")
print("🔧 [CONFIG] Configuration loading complete!")
