
import asyncio
import time
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from .config import settings
from .conversation_tracker import get_conversation_tracker

print("🧠 [LLM_ADAPTER] LLM Adapter module loading...")

class CustomLLMAdapter:
    """Custom LLM adapter for non-OpenAI models served via LiteLLM or similar"""
    
    def __init__(self, model: Optional[str] = None, base_url: Optional[str] = None, api_key: Optional[str] = None):
        print("🧠 [LLM_ADAPTER] Initializing LLM Adapter...")
        self.model = model or settings.llm_model
        self.base_url = base_url or settings.llm_base_url
        self.api_key = api_key or settings.llm_api_key
        
        print(f"🧠 [LLM_ADAPTER] Model: {self.model}")
        print(f"🧠 [LLM_ADAPTER] Base URL: {self.base_url}")
        print(f"🧠 [LLM_ADAPTER] API Key: {'***' + self.api_key[-4:] if self.api_key else 'Not set'}")
        
        # Initialize OpenAI client with custom base URL
        print("🧠 [LLM_ADAPTER] Creating AsyncOpenAI client...")
        self.client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
        print("🧠 [LLM_ADAPTER] LLM Adapter initialized successfully")
    
    async def generate_str(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> str:
        """Generate a string response from the LLM"""
        print(f"🧠 [LLM_ADAPTER] Generating response for message: '{message[:100]}...'")
        print(f"🧠 [LLM_ADAPTER] System prompt provided: {system_prompt is not None}")
        print(f"🧠 [LLM_ADAPTER] Tools provided: {tools is not None}")
        
        tracker = get_conversation_tracker()
        
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            print(f"🧠 [LLM_ADAPTER] Added system prompt (length: {len(system_prompt)})")
        
        messages.append({"role": "user", "content": message})
        print(f"🧠 [LLM_ADAPTER] Total messages: {len(messages)}")
        
        # Log the LLM request
        print("🧠 [LLM_ADAPTER] Logging LLM request...")
        request_id = tracker.log_llm_request(
            messages=messages,
            tools=tools,
            model=self.model
        )
        print(f"🧠 [LLM_ADAPTER] Request ID: {request_id}")
        
        start_time = time.time()
        print(f"🧠 [LLM_ADAPTER] Making API call to model: {self.model}")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                **kwargs
            )
            
            duration_ms = (time.time() - start_time) * 1000
            content = response.choices[0].message.content or ""
            
            # Log the LLM response
            tracker.log_llm_response(
                response={"content": content, "raw_response": response.model_dump()},
                duration_ms=duration_ms
            )
            
            return content
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            error_msg = f"Error generating response: {str(e)}"
            
            # Log the error
            tracker.log_error(error_msg, "llm_generation_error")
            tracker.log_llm_response(
                response={"content": error_msg, "error": str(e)},
                duration_ms=duration_ms
            )
            
            return error_msg
    
    async def generate_with_tools(
        self,
        message: str,
        tools: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response with tool calling capability"""
        tracker = get_conversation_tracker()
        
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": message})
        
        # Log the LLM request with tools
        request_id = tracker.log_llm_request(
            messages=messages,
            tools=tools,
            model=self.model
        )
        
        start_time = time.time()
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                **kwargs
            )
            
            duration_ms = (time.time() - start_time) * 1000
            choice = response.choices[0]
            message_response = choice.message
            
            result = {
                "content": message_response.content or "",
                "tool_calls": []
            }
            
            if message_response.tool_calls:
                for tool_call in message_response.tool_calls:
                    tool_call_data = {
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    }
                    result["tool_calls"].append(tool_call_data)
                    
                    # Log each tool call
                    tracker.log_tool_call(
                        tool_name=tool_call.function.name,
                        arguments=tool_call.function.arguments,
                        tool_call_id=tool_call.id
                    )
            
            # Log the LLM response
            tracker.log_llm_response(
                response={
                    "content": result["content"],
                    "tool_calls": result["tool_calls"],
                    "raw_response": response.model_dump()
                },
                duration_ms=duration_ms
            )
            
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            error_msg = f"Error generating response with tools: {str(e)}"
            
            # Log the error
            tracker.log_error(error_msg, "llm_tool_generation_error")
            tracker.log_llm_response(
                response={"content": error_msg, "tool_calls": [], "error": str(e)},
                duration_ms=duration_ms
            )
            
            return {
                "content": error_msg,
                "tool_calls": []
            }

