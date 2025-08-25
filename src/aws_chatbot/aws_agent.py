

import asyncio
import json
import os
import tempfile
from typing import Dict, Any, List, Optional
from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from .config import settings

class AWSAgent:
    """AWS Agent that uses MCP servers to interact with AWS services"""
    
    def __init__(self):
        self.app = None
        self.agent = None
        self.llm = None
        self._initialized = False
        self._app_context = None
    
    async def initialize(self):
        """Initialize the AWS agent with MCP servers"""
        if self._initialized:
            return
        
        # Create MCP configuration
        mcp_config = {
            "execution_engine": "asyncio",
            "logger": {
                "transports": ["console"],
                "level": "info"
            },
            "mcp": {
                "servers": {
                    "aws-api": {
                        "command": "uvx",
                        "args": ["awslabs.aws-api-mcp-server@latest"],
                        "env": {
                            "AWS_REGION": settings.aws_region,
                            "AWS_API_MCP_PROFILE_NAME": settings.aws_profile_name,
                            "READ_OPERATIONS_ONLY": str(settings.read_operations_only).lower(),
                            "REQUIRE_MUTATION_CONSENT": str(settings.require_mutation_consent).lower()
                        }
                    }
                }
            }
        }
        
        # Save config to temporary file
        config_path = "mcp_agent.config.yaml"
        import yaml
        with open(config_path, 'w') as f:
            yaml.dump(mcp_config, f)
        
        # Create the MCP app
        self.app = MCPApp(name="aws_chatbot_agent")
        
        # Initialize the agent
        self.agent = Agent(
            name="aws_assistant",
            instruction="""You are an AWS assistant that can help users interact with AWS services.
            You have access to AWS CLI commands through the MCP server.
            
            When users ask about AWS resources:
            1. Use the suggest_aws_commands tool to find appropriate CLI commands if available
            2. Execute the commands using call_aws tool
            3. Provide clear, helpful explanations of the results
            4. If operations might modify resources, explain what will happen before executing
            
            Always be helpful, accurate, and security-conscious.""",
            server_names=["aws-api"]
        )
        
        self._initialized = True
    
    async def start(self):
        """Start the agent and initialize MCP connections"""
        await self.initialize()
        
        # Start the MCP app
        self._app_context = self.app.run()
        mcp_agent_app = await self._app_context.__aenter__()
        self.logger = mcp_agent_app.logger
        
        # Start the agent
        await self.agent.__aenter__()
        
        # Initialize MCP servers and get available tools
        tools = await self.agent.list_tools()
        self.logger.info("Available AWS tools:", data=[tool["name"] for tool in tools])
        
        # Create custom LLM configuration for OpenAI-compatible API
        from openai import AsyncOpenAI
        
        # Create OpenAI client with custom configuration
        openai_client = AsyncOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key
        )
        
        # Attach LLM to agent
        self.llm = await self.agent.attach_llm(
            OpenAIAugmentedLLM,
            model=settings.llm_model,
            client=openai_client
        )
        
        return self
    
    async def stop(self):
        """Stop the agent and clean up resources"""
        if self.agent:
            await self.agent.__aexit__(None, None, None)
        if self._app_context:
            await self._app_context.__aexit__(None, None, None)
    
    async def process_query(self, query: str) -> str:
        """Process a user query and return the response"""
        if not self._initialized or not self.llm:
            return "Agent not initialized. Please start the agent first."
        
        try:
            # Use the LLM with AWS tools to process the query
            response = await self.llm.generate_str(
                message=query
            )
            
            return response
        except Exception as e:
            return f"Error processing query: {str(e)}"
    
    async def suggest_commands(self, query: str) -> List[Dict[str, Any]]:
        """Suggest AWS CLI commands for a given query"""
        if not self._initialized or not self.llm:
            return [{"error": "Agent not initialized"}]
        
        try:
            # Try to use the suggest_aws_commands tool if available
            tools = await self.agent.list_tools()
            suggest_tool = next((tool for tool in tools if tool["name"] == "suggest_aws_commands"), None)
            
            if suggest_tool:
                # Use the MCP tool to suggest commands
                result = await self.agent.call_tool("suggest_aws_commands", {"query": query})
                return result.get("suggestions", [])
            else:
                # Fallback to basic suggestions
                return [
                    {
                        "command": "aws ec2 describe-instances",
                        "description": "List EC2 instances",
                        "parameters": {}
                    }
                ]
        except Exception as e:
            return [{"error": f"Error suggesting commands: {str(e)}"}]
    
    async def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute an AWS CLI command"""
        if not self._initialized or not self.agent:
            return {
                "success": False,
                "error": "Agent not initialized",
                "command": command
            }
        
        try:
            # Use the call_aws tool from the MCP server
            result = await self.agent.call_tool("call_aws", {"command": command})
            
            return {
                "success": True,
                "output": result.get("output", ""),
                "command": command
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing command: {str(e)}",
                "command": command
            }


