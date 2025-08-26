import asyncio
import json
import subprocess
from typing import Dict, Any, List, Optional
from datetime import datetime
from .config import settings
from .llm_adapter import CustomLLMAdapter

class ConversationMemory:
    """Simple conversation memory to track user interactions and AWS command results"""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.history: List[Dict[str, Any]] = []
    
    def add_interaction(self, user_query: str, agent_response: str, command_executed: Optional[str] = None, command_result: Optional[str] = None):
        """Add a user-agent interaction to memory"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_query": user_query,
            "agent_response": agent_response,
            "command_executed": command_executed,
            "command_result": command_result
        }
        
        self.history.append(interaction)
        
        # Keep only the most recent interactions
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_context_summary(self) -> str:
        """Get a summary of recent conversation for context"""
        if not self.history:
            return "No previous conversation history."
        
        context_lines = ["Recent conversation context:"]
        
        for interaction in self.history[-5:]:  # Last 5 interactions
            context_lines.append(f"User: {interaction['user_query']}")
            if interaction['command_executed']:
                context_lines.append(f"Executed: {interaction['command_executed']}")
            context_lines.append(f"Assistant: {interaction['agent_response'][:100]}...")
            context_lines.append("---")
        
        return "\n".join(context_lines)
    
    def get_recent_commands(self) -> List[str]:
        """Get list of recently executed commands"""
        commands = []
        for interaction in self.history:
            if interaction['command_executed']:
                commands.append(interaction['command_executed'])
        return commands[-5:]  # Last 5 commands
    
    def clear(self):
        """Clear conversation history"""
        self.history.clear()

class LLMDrivenAWSAgent:
    """LLM-driven AWS Agent with conversation memory that uses the LLM to determine what commands to execute"""
    
    def __init__(self):
        self._initialized = False
        self.llm = None
        self.memory = ConversationMemory()
    
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
        """Process a user query using LLM with conversation memory"""
        if not self._initialized or not self.llm:
            return "Agent not initialized."
        
        # Get conversation context for memory-aware responses
        context_summary = self.memory.get_context_summary()
        recent_commands = self.memory.get_recent_commands()
        
        # Enhanced system prompt with memory context
        system_prompt = f"""You are an AWS assistant that helps users interact with AWS services. You have memory of previous conversations and can reference past interactions.

CONVERSATION CONTEXT:
{context_summary}

RECENTLY EXECUTED COMMANDS:
{', '.join(recent_commands) if recent_commands else 'None'}

Your capabilities:
- You can suggest and execute AWS CLI commands
- You have access to AWS region: {settings.aws_region}
- You remember previous conversations and can reference them
- You can answer follow-up questions about previous commands or results
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

IMPORTANT: Use conversation context to provide better responses:
- If user asks "how many?" or "which ones?" refer to previous command results
- If user says "show me more details" about something mentioned before, use appropriate commands
- If user references "the instances" or "those buckets", understand from context what they mean

When responding:
1. If the user asks about listing/describing AWS resources, suggest the appropriate AWS CLI command
2. If the user is asking follow-up questions, use conversation context to understand what they're referring to
3. Format your response as JSON with this structure:
   {{
     "action": "execute_command" | "provide_info" | "ask_clarification",
     "command": "aws cli command to execute (if action is execute_command)",
     "explanation": "Brief explanation of what the command does",
     "response": "Natural language response to the user",
     "context_used": "true/false - whether you used conversation context"
   }}

Examples:
- User: "List my EC2 instances" -> action: "execute_command", command: "aws ec2 describe-instances --region {settings.aws_region}"
- User: "How many were there?" (after listing instances) -> action: "provide_info", response: reference previous results
- User: "Show me S3 buckets" -> action: "execute_command", command: "aws s3 ls"
- User: "What is AWS?" -> action: "provide_info", response: explanation about AWS

Always be helpful and security-conscious. If a command might modify resources, explain what it will do first."""

        try:
            # Use LLM to determine what to do with the query (with memory context)
            llm_response = await self.llm.generate_str(
                message=query,
                system_prompt=system_prompt
            )
            
            # Try to parse the LLM response as JSON
            try:
                response_data = json.loads(llm_response)
                action = response_data.get("action", "provide_info")
                command_executed = None
                command_result = None
                final_response = ""
                
                if action == "execute_command":
                    command = response_data.get("command", "")
                    explanation = response_data.get("explanation", "")
                    
                    if command:
                        command_executed = command
                        # Execute the command suggested by the LLM
                        result = await self.execute_command(command)
                        command_result = result.get('output', '') if result['success'] else result.get('error', '')
                        
                        if result["success"]:
                            # Use LLM to format the command output into a natural language response
                            format_prompt = f"""The user asked: "{query}"

CONVERSATION CONTEXT:
{context_summary}

I executed the AWS CLI command: {command}

The command output was:
{result['output']}

Please provide a helpful, natural language summary of this information. Make it easy to understand and highlight the most important details. If there are no resources found, mention that clearly. 

If this is a follow-up question referencing previous conversation, acknowledge the context appropriately."""

                            formatted_response = await self.llm.generate_str(
                                message="Please format this AWS CLI output into a natural language response.",
                                system_prompt=format_prompt
                            )
                            
                            final_response = formatted_response
                        else:
                            final_response = f"I tried to {explanation.lower()}, but encountered an error: {result['error']}"
                    else:
                        final_response = response_data.get("response", "I'm not sure how to help with that query.")
                
                elif action == "ask_clarification":
                    final_response = response_data.get("response", "Could you please provide more details about what you'd like to do?")
                
                else:  # provide_info
                    final_response = response_data.get("response", "I'm here to help you with AWS services!")
                
                # Store this interaction in memory
                self.memory.add_interaction(
                    user_query=query,
                    agent_response=final_response,
                    command_executed=command_executed,
                    command_result=command_result
                )
                
                return final_response
                    
            except json.JSONDecodeError:
                # If LLM response isn't valid JSON, return it as-is
                final_response = llm_response
                self.memory.add_interaction(
                    user_query=query,
                    agent_response=final_response
                )
                return final_response
                
        except Exception as e:
            error_response = f"I encountered an error while processing your query: {str(e)}"
            self.memory.add_interaction(
                user_query=query,
                agent_response=error_response
            )
            return error_response
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics and recent interactions"""
        return {
            "total_interactions": len(self.memory.history),
            "recent_commands": self.memory.get_recent_commands(),
            "context_summary": self.memory.get_context_summary()
        }
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()
    
    async def suggest_commands(self, query: str) -> List[Dict[str, Any]]:
        """Use LLM to suggest AWS CLI commands for a query with memory context"""
        if not self._initialized or not self.llm:
            return [{"error": "Agent not initialized"}]
        
        # Get conversation context for better command suggestions
        context_summary = self.memory.get_context_summary()
        recent_commands = self.memory.get_recent_commands()
        
        system_prompt = f"""You are an AWS CLI expert. Given a user query and conversation context, suggest appropriate AWS CLI commands.

CONVERSATION CONTEXT:
{context_summary}

RECENTLY EXECUTED COMMANDS:
{', '.join(recent_commands) if recent_commands else 'None'}

Consider the conversation context when suggesting commands:
- If user is asking follow-up questions, suggest commands that build on previous queries
- If user references "those instances" or "the buckets", understand from context what they mean
- Suggest more specific commands if previous general commands were executed

Respond with a JSON array of command suggestions. Each suggestion should have:
- "command": the full AWS CLI command
- "description": what the command does
- "service": the AWS service (e.g., "EC2", "S3", "RDS")
- "context_aware": true/false - whether this suggestion uses conversation context

Use region {settings.aws_region} for commands that require a region.

Examples:
User: "show my instances" -> [{{"command": "aws ec2 describe-instances --region {settings.aws_region}", "description": "List all EC2 instances", "service": "EC2", "context_aware": false}}]
User: "get more details about them" (after listing instances) -> [{{"command": "aws ec2 describe-instances --region {settings.aws_region} --query 'Reservations[*].Instances[*].[InstanceId,State.Name,InstanceType,PublicIpAddress]' --output table", "description": "Get detailed information about EC2 instances in table format", "service": "EC2", "context_aware": true}}]"""

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
