


import asyncio
import subprocess
import json
from typing import Dict, Any, List, Optional
from .config import settings

class SimpleAWSAgent:
    """Simple AWS Agent that directly calls AWS CLI without MCP for testing"""
    
    def __init__(self):
        self._initialized = False
    
    async def initialize(self):
        """Initialize the simple agent"""
        self._initialized = True
    
    async def start(self):
        """Start the agent"""
        await self.initialize()
        return self
    
    async def stop(self):
        """Stop the agent"""
        pass
    
    async def process_query(self, query: str) -> str:
        """Process a user query and return a response"""
        if not self._initialized:
            return "Agent not initialized."
        
        # Simple query processing - suggest AWS commands based on keywords
        query_lower = query.lower()
        
        if "ec2" in query_lower and ("list" in query_lower or "show" in query_lower or "describe" in query_lower):
            try:
                result = await self.execute_command("aws ec2 describe-instances --region " + settings.aws_region)
                if result["success"]:
                    return f"Here are your EC2 instances:\n\n```json\n{result['output']}\n```"
                else:
                    return f"Error listing EC2 instances: {result['error']}"
            except Exception as e:
                return f"Error executing EC2 command: {str(e)}"
        
        elif "s3" in query_lower and ("list" in query_lower or "show" in query_lower or "bucket" in query_lower):
            try:
                result = await self.execute_command("aws s3 ls")
                if result["success"]:
                    return f"Here are your S3 buckets:\n\n```\n{result['output']}\n```"
                else:
                    return f"Error listing S3 buckets: {result['error']}"
            except Exception as e:
                return f"Error executing S3 command: {str(e)}"
        
        elif "rds" in query_lower and ("list" in query_lower or "show" in query_lower or "database" in query_lower):
            try:
                result = await self.execute_command("aws rds describe-db-instances --region " + settings.aws_region)
                if result["success"]:
                    return f"Here are your RDS databases:\n\n```json\n{result['output']}\n```"
                else:
                    return f"Error listing RDS databases: {result['error']}"
            except Exception as e:
                return f"Error executing RDS command: {str(e)}"
        
        elif "lambda" in query_lower and ("list" in query_lower or "show" in query_lower or "function" in query_lower):
            try:
                result = await self.execute_command("aws lambda list-functions --region " + settings.aws_region)
                if result["success"]:
                    return f"Here are your Lambda functions:\n\n```json\n{result['output']}\n```"
                else:
                    return f"Error listing Lambda functions: {result['error']}"
            except Exception as e:
                return f"Error executing Lambda command: {str(e)}"
        
        elif "vpc" in query_lower and ("list" in query_lower or "show" in query_lower or "describe" in query_lower):
            try:
                result = await self.execute_command("aws ec2 describe-vpcs --region " + settings.aws_region)
                if result["success"]:
                    return f"Here are your VPCs:\n\n```json\n{result['output']}\n```"
                else:
                    return f"Error listing VPCs: {result['error']}"
            except Exception as e:
                return f"Error executing VPC command: {str(e)}"
        
        else:
            return f"""I can help you with AWS services! Try asking me about:

- **EC2 instances**: "List EC2 instances" or "Show me my EC2 servers"
- **S3 buckets**: "Show S3 buckets" or "List my S3 storage"
- **RDS databases**: "List RDS databases" or "Show my databases"
- **Lambda functions**: "List Lambda functions" or "Show my serverless functions"
- **VPC information**: "Show VPC information" or "List my VPCs"

Your query: "{query}"

Note: This is a simplified demo version. The full MCP-powered agent will provide more comprehensive AWS service support."""
    
    async def suggest_commands(self, query: str) -> List[Dict[str, Any]]:
        """Suggest AWS CLI commands for a query"""
        query_lower = query.lower()
        suggestions = []
        
        if "ec2" in query_lower:
            suggestions.append({
                "command": f"aws ec2 describe-instances --region {settings.aws_region}",
                "description": "List all EC2 instances",
                "service": "EC2"
            })
        
        if "s3" in query_lower:
            suggestions.append({
                "command": "aws s3 ls",
                "description": "List all S3 buckets",
                "service": "S3"
            })
        
        if "rds" in query_lower:
            suggestions.append({
                "command": f"aws rds describe-db-instances --region {settings.aws_region}",
                "description": "List all RDS database instances",
                "service": "RDS"
            })
        
        if "lambda" in query_lower:
            suggestions.append({
                "command": f"aws lambda list-functions --region {settings.aws_region}",
                "description": "List all Lambda functions",
                "service": "Lambda"
            })
        
        if not suggestions:
            suggestions = [
                {
                    "command": f"aws ec2 describe-instances --region {settings.aws_region}",
                    "description": "List EC2 instances",
                    "service": "EC2"
                },
                {
                    "command": "aws s3 ls",
                    "description": "List S3 buckets",
                    "service": "S3"
                }
            ]
        
        return suggestions
    
    async def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute an AWS CLI command"""
        if not self._initialized:
            return {
                "success": False,
                "error": "Agent not initialized",
                "command": command
            }
        
        try:
            # Check if AWS CLI is available by trying to run aws --version
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


