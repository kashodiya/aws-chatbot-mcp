import asyncio
import json
import subprocess
from typing import Dict, Any, List, Optional
from .config import settings

class WorkingAWSAgent:
    """Working AWS Agent that provides natural language responses"""
    
    def __init__(self):
        self._initialized = False
    
    async def initialize(self):
        """Initialize the agent"""
        self._initialized = True
    
    async def start(self):
        """Start the agent"""
        await self.initialize()
        return self
    
    async def stop(self):
        """Stop the agent"""
        pass
    
    async def process_query(self, query: str) -> str:
        """Process a user query and return a natural language response"""
        if not self._initialized:
            return "Agent not initialized."
        
        # Simple query processing with natural language responses
        query_lower = query.lower()
        
        if "ec2" in query_lower and ("list" in query_lower or "show" in query_lower or "describe" in query_lower):
            try:
                result = await self.execute_command("aws ec2 describe-instances --region " + settings.aws_region)
                if result["success"]:
                    # Parse JSON and create natural language response
                    try:
                        data = json.loads(result['output'])
                        instances = []
                        for reservation in data.get('Reservations', []):
                            for instance in reservation.get('Instances', []):
                                instance_id = instance.get('InstanceId', 'Unknown')
                                state = instance.get('State', {}).get('Name', 'Unknown')
                                instance_type = instance.get('InstanceType', 'Unknown')
                                instances.append(f"- {instance_id} ({instance_type}) - {state}")
                        
                        if instances:
                            return f"I found {len(instances)} EC2 instance(s) in your account:\n\n" + "\n".join(instances)
                        else:
                            return "You don't have any EC2 instances in this region."
                    except json.JSONDecodeError:
                        return f"I found your EC2 instances, but had trouble parsing the response. Here's the raw data:\n\n```json\n{result['output']}\n```"
                else:
                    return f"I couldn't retrieve your EC2 instances. Error: {result['error']}"
            except Exception as e:
                return f"I encountered an error while checking your EC2 instances: {str(e)}"
        
        elif "s3" in query_lower and ("list" in query_lower or "show" in query_lower or "bucket" in query_lower):
            try:
                result = await self.execute_command("aws s3 ls")
                if result["success"]:
                    lines = result['output'].strip().split('\n')
                    if lines and lines[0]:
                        buckets = []
                        for line in lines:
                            if line.strip():
                                # Parse S3 ls output: "2023-01-01 12:00:00 bucket-name"
                                parts = line.strip().split()
                                if len(parts) >= 3:
                                    bucket_name = parts[-1]
                                    date = parts[0]
                                    buckets.append(f"- {bucket_name} (created: {date})")
                        
                        if buckets:
                            return f"I found {len(buckets)} S3 bucket(s) in your account:\n\n" + "\n".join(buckets)
                        else:
                            return "You don't have any S3 buckets."
                    else:
                        return "You don't have any S3 buckets."
                else:
                    return f"I couldn't retrieve your S3 buckets. Error: {result['error']}"
            except Exception as e:
                return f"I encountered an error while checking your S3 buckets: {str(e)}"
        
        elif "rds" in query_lower and ("list" in query_lower or "show" in query_lower or "database" in query_lower):
            try:
                result = await self.execute_command("aws rds describe-db-instances --region " + settings.aws_region)
                if result["success"]:
                    try:
                        data = json.loads(result['output'])
                        databases = []
                        for db in data.get('DBInstances', []):
                            db_id = db.get('DBInstanceIdentifier', 'Unknown')
                            engine = db.get('Engine', 'Unknown')
                            status = db.get('DBInstanceStatus', 'Unknown')
                            databases.append(f"- {db_id} ({engine}) - {status}")
                        
                        if databases:
                            return f"I found {len(databases)} RDS database(s) in your account:\n\n" + "\n".join(databases)
                        else:
                            return "You don't have any RDS databases in this region."
                    except json.JSONDecodeError:
                        return f"I found your RDS databases, but had trouble parsing the response. Here's the raw data:\n\n```json\n{result['output']}\n```"
                else:
                    return f"I couldn't retrieve your RDS databases. Error: {result['error']}"
            except Exception as e:
                return f"I encountered an error while checking your RDS databases: {str(e)}"
        
        elif "lambda" in query_lower and ("list" in query_lower or "show" in query_lower or "function" in query_lower):
            try:
                result = await self.execute_command("aws lambda list-functions --region " + settings.aws_region)
                if result["success"]:
                    try:
                        data = json.loads(result['output'])
                        functions = []
                        for func in data.get('Functions', []):
                            func_name = func.get('FunctionName', 'Unknown')
                            runtime = func.get('Runtime', 'Unknown')
                            functions.append(f"- {func_name} ({runtime})")
                        
                        if functions:
                            return f"I found {len(functions)} Lambda function(s) in your account:\n\n" + "\n".join(functions)
                        else:
                            return "You don't have any Lambda functions in this region."
                    except json.JSONDecodeError:
                        return f"I found your Lambda functions, but had trouble parsing the response. Here's the raw data:\n\n```json\n{result['output']}\n```"
                else:
                    return f"I couldn't retrieve your Lambda functions. Error: {result['error']}"
            except Exception as e:
                return f"I encountered an error while checking your Lambda functions: {str(e)}"
        
        elif "vpc" in query_lower and ("list" in query_lower or "show" in query_lower or "describe" in query_lower):
            try:
                result = await self.execute_command("aws ec2 describe-vpcs --region " + settings.aws_region)
                if result["success"]:
                    try:
                        data = json.loads(result['output'])
                        vpcs = []
                        for vpc in data.get('Vpcs', []):
                            vpc_id = vpc.get('VpcId', 'Unknown')
                            cidr = vpc.get('CidrBlock', 'Unknown')
                            state = vpc.get('State', 'Unknown')
                            is_default = vpc.get('IsDefault', False)
                            default_text = " (default)" if is_default else ""
                            vpcs.append(f"- {vpc_id} ({cidr}) - {state}{default_text}")
                        
                        if vpcs:
                            return f"I found {len(vpcs)} VPC(s) in your account:\n\n" + "\n".join(vpcs)
                        else:
                            return "You don't have any VPCs in this region."
                    except json.JSONDecodeError:
                        return f"I found your VPCs, but had trouble parsing the response. Here's the raw data:\n\n```json\n{result['output']}\n```"
                else:
                    return f"I couldn't retrieve your VPCs. Error: {result['error']}"
            except Exception as e:
                return f"I encountered an error while checking your VPCs: {str(e)}"
        
        else:
            return f"""I'm an AWS assistant that can help you manage your AWS resources! Here's what I can help you with:

🖥️  **EC2 Instances**: Ask me "List my EC2 instances" or "Show me my servers"
🪣  **S3 Buckets**: Ask me "Show my S3 buckets" or "List my storage"
🗄️  **RDS Databases**: Ask me "List my databases" or "Show RDS instances"
⚡  **Lambda Functions**: Ask me "Show my Lambda functions" or "List serverless functions"
🌐  **VPC Networks**: Ask me "Show my VPCs" or "List my networks"

Your query: "{query}"

I provide natural language responses instead of raw JSON data. Try asking about any of the services above!"""
    
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
