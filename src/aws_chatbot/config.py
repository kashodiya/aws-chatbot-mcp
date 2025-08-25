import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # LLM Configuration
    llm_model: str = Field(default="gpt-4", env="LLM_MODEL")
    llm_base_url: Optional[str] = Field(default=None, env="LLM_BASE_URL")
    llm_api_key: str = Field(default="", env="LLM_API_KEY")
    
    # AWS Configuration
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    aws_profile_name: str = Field(default="default", env="AWS_API_MCP_PROFILE_NAME")
    read_operations_only: bool = Field(default=False, env="READ_OPERATIONS_ONLY")
    require_mutation_consent: bool = Field(default=False, env="REQUIRE_MUTATION_CONSENT")
    
    # Web Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=50333, env="PORT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

settings = Settings()
