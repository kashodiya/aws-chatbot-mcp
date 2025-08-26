import asyncio
import json
import subprocess
from typing import Dict, Any, List, Optional
from .config import settings
from .llm_adapter import CustomLLMAdapter

class LLMDrivenAWSAgent:
    """LLM-driven AWS Agent that uses the LLM to determine what commands to execute"""
    
    def __init__(self):
        self._initialized = False
        self.llm = None
    
    async def initialize(self):
        """Initialize the agent with LLM"""
        if self._initialized:
            return
            
        # Initialize the LLM adapter
        self.llm = CustomLLMAdapter()
        self._initialized = True
    
    async def start(self):
        """Start the agent"""
        await self.initialize()
        return self
    
    async def stop(self):
        """Stop the agent"""
        pass
    
    async def process_query(self, query: str) -> str:
        """Process a user query using LLM to determine appropriate actions"""
        if not self._initialized or not self.llm:
            return "Agent not initialized."
        
        # System prompt that instructs the LLM on how to handle AWS queries
        system_prompt = f"""You are an AWS assistant that helps users interact with AWS services. 

Your capabilities:
- You can suggest and execute AWS CLI commands
- You have access to AWS region: {settings.aws_region}
- You should provide helpful, natural language responses
- When users ask about AWS resources, determine the appropriate AWS CLI commands to run

Available AWS services you can help with:
- EC2 (instances, security groups, key pairs, etc.)
- S3 (buckets, objects, etc.)
- RDS (databases, snapshots, etc.)
- Lambda (functions, layers, etc.)
- VPC (networks, subnets, route tables, etc.)
- IAM (users, roles, policies, etc.)
- CloudFormation (stacks, templates, etc.)
- And many more AWS services

When responding:
1. If the user asks about listing/describing AWS resources, suggest the appropriate AWS CLI command
2. Format your response as JSON with this structure:
   {{
     "action": "execute_command" | "provide_info" | "ask_clarification",
     "command": "aws cli command to execute (if action is execute_command)",
     "explanation": "Brief explanation of what the command does",
     "response": "Natural language response to the user"
   }}

Examples:
- User: "List my EC2 instances" -> action: "execute_command", command: "aws ec2 describe-instances --region {settings.aws_region}"
- User: "Show my S3 buckets" -> action: "execute_command", command: "aws s3 ls"
- User: "What is AWS?" -> action: "provide_info", response: explanation about AWS

Always be helpful and security-conscious. If a command might modify resources, explain what it will do first."""

        try:
            # Use LLM to determine what to do with the query
            llm_response = await self.llm.generate_str(
                message=query,
                system_prompt=system_prompt
            )
            
            # Try to parse the LLM response as JSON
            try:
                response_data = json.loads(llm_response)
                action = response_data.get("action", "provide_info")
                
                if action == "execute_command":
                    command = response_data.get("command", "")
                    explanation = response_data.get("explanation", "")
                    
                    if command:
                        # Execute the command suggested by the LLM
                        result = await self.execute_command(command)
                        
                        if result["success"]:
                            # Use LLM to format the command output into a natural language response
                            format_prompt = f"""The user asked: "{query}"

I executed the AWS CLI command: {command}

The command output was:
{result['output']}

Please provide a helpful, natural language summary of this information. Make it easy to understand and highlight the most important details. If there are no resources found, mention that clearly."""

                            formatted_response = await self.llm.generate_str(
                                message="Please format this AWS CLI output into a natural language response.",
                                system_prompt=format_prompt
                            )
                            
                            return formatted_response
                        else:
                            return f"I tried to {explanation.lower()}, but encountered an error: {result['error']}"
                    else:
                        return response_data.get("response", "I'm not sure how to help with that query.")
                
                elif action == "ask_clarification":
                    return response_data.get("response", "Could you please provide more details about what you'd like to do?")
                
                else:  # provide_info
                    return response_data.get("response", "I'm here to help you with AWS services!")
                    
            except json.JSONDecodeError:
                # If LLM response isn't valid JSON, return it as-is
                return llm_response
                
        except Exception as e:
            return f"I encountered an error while processing your query: {str(e)}"
    
    async def suggest_commands(self, query: str) -> List[Dict[str, Any]]:
        """Use LLM to suggest AWS CLI commands for a query"""
        if not self._initialized or not self.llm:
            return [{"error": "Agent not initialized"}]
        
        system_prompt = f"""You are an AWS CLI expert. Given a user query, suggest appropriate AWS CLI commands.

Respond with a JSON array of command suggestions. Each suggestion should have:
- "command": the full AWS CLI command
- "description": what the command does
- "service": the AWS service (e.g., "EC2", "S3", "RDS")

Use region {settings.aws_region} for commands that require a region.

Examples:
User: "show my instances" -> [{{"command": "aws ec2 describe-instances --region {settings.aws_region}", "description": "List all EC2 instances", "service": "EC2"}}]
User: "list buckets" -> [{{"command": "aws s3 ls", "description": "List all S3 buckets", "service": "S3"}}]"""

        try:
            llm_response = await self.llm.generate_str(
                message=f"Suggest AWS CLI commands for: {query}",
                system_prompt=system_prompt
            )
            
            # Try to parse as JSON array
            try:
                suggestions = json.loads(llm_response)
                if isinstance(suggestions, list):
                    return suggestions
                else:
                    return [{"error": "Invalid response format from LLM"}]
            except json.JSONDecodeError:
                # Fallback: create a basic suggestion
                return [{
                    "command": "aws help",
                    "description": "Get help with AWS CLI commands",
                    "service": "General",
                    "note": f"LLM response: {llm_response}"
                }]
                
        except Exception as e:
            return [{"error": f"Error getting suggestions: {str(e)}"}]
    
    async def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute an AWS CLI command (this should only be called after LLM determines it's appropriate)"""
        if not self._initialized:
            return {
                "success": False,
                "error": "Agent not initialized",
                "command": command
            }
        
        try:
            # Check if AWS CLI is available
            result = subprocess.run(
                ["aws", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": "AWS CLI not found. Please install AWS CLI and configure your credentials.",
                    "command": command
                }
            
            # Execute the AWS CLI command
            cmd_parts = command.split()
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "output": result.stdout,
                    "command": command
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr or "Command failed",
                    "command": command
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out",
                "command": command
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing command: {str(e)}",
                "command": command
            }
