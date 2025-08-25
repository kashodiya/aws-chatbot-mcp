
import asyncio
from typing import Dict, Any, List, Optional
from mcp_agent.workflows.llm.base import BaseLLM
from openai import AsyncOpenAI
from .config import settings

class CustomLLMAdapter(BaseLLM):
    """Custom LLM adapter for non-OpenAI models served via LiteLLM or similar"""
    
    def __init__(self, model: Optional[str] = None, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.model = model or settings.llm_model
        self.base_url = base_url or settings.llm_base_url
        self.api_key = api_key or settings.llm_api_key
        
        # Initialize OpenAI client with custom base URL
        self.client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
    
    async def generate_str(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> str:
        """Generate a string response from the LLM"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": message})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                **kwargs
            )
            
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    async def generate_with_tools(
        self,
        message: str,
        tools: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response with tool calling capability"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": message})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                **kwargs
            )
            
            choice = response.choices[0]
            message_response = choice.message
            
            result = {
                "content": message_response.content or "",
                "tool_calls": []
            }
            
            if message_response.tool_calls:
                for tool_call in message_response.tool_calls:
                    result["tool_calls"].append({
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    })
            
            return result
        except Exception as e:
            return {
                "content": f"Error generating response with tools: {str(e)}",
                "tool_calls": []
            }

