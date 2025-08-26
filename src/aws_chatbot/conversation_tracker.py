"""
Enhanced Conversation Tracker for MCP Agent

This module provides detailed tracking of all conversations including:
- User messages
- LLM responses
- Tool calls and responses
- Internal agent reasoning
- MCP server interactions
"""

import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum


class EventType(Enum):
    USER_MESSAGE = "user_message"
    AGENT_RESPONSE = "agent_response"
    LLM_REQUEST = "llm_request"
    LLM_RESPONSE = "llm_response"
    TOOL_CALL = "tool_call"
    TOOL_RESPONSE = "tool_response"
    COMMAND_EXECUTION = "command_execution"
    COMMAND_RESULT = "command_result"
    AGENT_REASONING = "agent_reasoning"
    ERROR = "error"
    SYSTEM_EVENT = "system_event"


@dataclass
class ConversationEvent:
    """Represents a single event in the conversation"""
    id: str
    timestamp: str
    event_type: EventType
    content: Any
    metadata: Dict[str, Any]
    session_id: str
    parent_id: Optional[str] = None
    duration_ms: Optional[float] = None


class DetailedConversationTracker:
    """Enhanced conversation tracker that captures all interactions"""
    
    def __init__(self, session_id: Optional[str] = None, max_events: int = 1000):
        self.session_id = session_id or str(uuid.uuid4())
        self.max_events = max_events
        self.events: List[ConversationEvent] = []
        self.current_conversation_id: Optional[str] = None
        self._event_stack: List[str] = []  # For tracking nested events
        
    def start_conversation(self, user_message: str) -> str:
        """Start a new conversation turn"""
        conversation_id = str(uuid.uuid4())
        self.current_conversation_id = conversation_id
        
        event = ConversationEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            event_type=EventType.USER_MESSAGE,
            content=user_message,
            metadata={
                "conversation_id": conversation_id,
                "turn_number": len([e for e in self.events if e.event_type == EventType.USER_MESSAGE]) + 1
            },
            session_id=self.session_id
        )
        
        self._add_event(event)
        return conversation_id
    
    def log_llm_request(self, messages: List[Dict], tools: Optional[List[Dict]] = None, 
                       model: str = None, parent_id: Optional[str] = None) -> str:
        """Log an LLM request"""
        event_id = str(uuid.uuid4())
        
        event = ConversationEvent(
            id=event_id,
            timestamp=datetime.now().isoformat(),
            event_type=EventType.LLM_REQUEST,
            content={
                "messages": messages,
                "tools": tools,
                "model": model
            },
            metadata={
                "conversation_id": self.current_conversation_id,
                "message_count": len(messages),
                "has_tools": tools is not None,
                "tool_count": len(tools) if tools else 0
            },
            session_id=self.session_id,
            parent_id=parent_id
        )
        
        self._add_event(event)
        self._event_stack.append(event_id)
        return event_id
    
    def log_llm_response(self, response: Dict[str, Any], duration_ms: float = None) -> str:
        """Log an LLM response"""
        event_id = str(uuid.uuid4())
        parent_id = self._event_stack.pop() if self._event_stack else None
        
        # Extract tool calls if present
        tool_calls = response.get("tool_calls", [])
        content = response.get("content", "")
        
        event = ConversationEvent(
            id=event_id,
            timestamp=datetime.now().isoformat(),
            event_type=EventType.LLM_RESPONSE,
            content={
                "content": content,
                "tool_calls": tool_calls,
                "raw_response": response
            },
            metadata={
                "conversation_id": self.current_conversation_id,
                "has_content": bool(content),
                "has_tool_calls": bool(tool_calls),
                "tool_call_count": len(tool_calls)
            },
            session_id=self.session_id,
            parent_id=parent_id,
            duration_ms=duration_ms
        )
        
        self._add_event(event)
        return event_id
    
    def log_tool_call(self, tool_name: str, arguments: Dict[str, Any], 
                     tool_call_id: str = None, parent_id: Optional[str] = None) -> str:
        """Log a tool call"""
        event_id = str(uuid.uuid4())
        
        event = ConversationEvent(
            id=event_id,
            timestamp=datetime.now().isoformat(),
            event_type=EventType.TOOL_CALL,
            content={
                "tool_name": tool_name,
                "arguments": arguments,
                "tool_call_id": tool_call_id
            },
            metadata={
                "conversation_id": self.current_conversation_id,
                "argument_count": len(arguments)
            },
            session_id=self.session_id,
            parent_id=parent_id
        )
        
        self._add_event(event)
        self._event_stack.append(event_id)
        return event_id
    
    def log_tool_response(self, result: Any, success: bool = True, 
                         error: str = None, duration_ms: float = None) -> str:
        """Log a tool response"""
        event_id = str(uuid.uuid4())
        parent_id = self._event_stack.pop() if self._event_stack else None
        
        event = ConversationEvent(
            id=event_id,
            timestamp=datetime.now().isoformat(),
            event_type=EventType.TOOL_RESPONSE,
            content={
                "result": result,
                "success": success,
                "error": error
            },
            metadata={
                "conversation_id": self.current_conversation_id,
                "success": success,
                "has_error": error is not None
            },
            session_id=self.session_id,
            parent_id=parent_id,
            duration_ms=duration_ms
        )
        
        self._add_event(event)
        return event_id
    
    def log_command_execution(self, command: str, parent_id: Optional[str] = None) -> str:
        """Log command execution"""
        event_id = str(uuid.uuid4())
        
        event = ConversationEvent(
            id=event_id,
            timestamp=datetime.now().isoformat(),
            event_type=EventType.COMMAND_EXECUTION,
            content={"command": command},
            metadata={
                "conversation_id": self.current_conversation_id,
                "command_length": len(command)
            },
            session_id=self.session_id,
            parent_id=parent_id
        )
        
        self._add_event(event)
        self._event_stack.append(event_id)
        return event_id
    
    def log_command_result(self, result: Dict[str, Any], duration_ms: float = None) -> str:
        """Log command execution result"""
        event_id = str(uuid.uuid4())
        parent_id = self._event_stack.pop() if self._event_stack else None
        
        event = ConversationEvent(
            id=event_id,
            timestamp=datetime.now().isoformat(),
            event_type=EventType.COMMAND_RESULT,
            content=result,
            metadata={
                "conversation_id": self.current_conversation_id,
                "success": result.get("success", False),
                "has_output": bool(result.get("output")),
                "has_error": bool(result.get("error"))
            },
            session_id=self.session_id,
            parent_id=parent_id,
            duration_ms=duration_ms
        )
        
        self._add_event(event)
        return event_id
    
    def log_agent_reasoning(self, reasoning: str, reasoning_type: str = "general", 
                           parent_id: Optional[str] = None) -> str:
        """Log agent internal reasoning"""
        event_id = str(uuid.uuid4())
        
        event = ConversationEvent(
            id=event_id,
            timestamp=datetime.now().isoformat(),
            event_type=EventType.AGENT_REASONING,
            content={
                "reasoning": reasoning,
                "type": reasoning_type
            },
            metadata={
                "conversation_id": self.current_conversation_id,
                "reasoning_type": reasoning_type,
                "reasoning_length": len(reasoning)
            },
            session_id=self.session_id,
            parent_id=parent_id
        )
        
        self._add_event(event)
        return event_id
    
    def log_agent_response(self, response: str, parent_id: Optional[str] = None) -> str:
        """Log final agent response to user"""
        event_id = str(uuid.uuid4())
        
        event = ConversationEvent(
            id=event_id,
            timestamp=datetime.now().isoformat(),
            event_type=EventType.AGENT_RESPONSE,
            content=response,
            metadata={
                "conversation_id": self.current_conversation_id,
                "response_length": len(response)
            },
            session_id=self.session_id,
            parent_id=parent_id
        )
        
        self._add_event(event)
        return event_id
    
    def log_error(self, error: str, error_type: str = "general", 
                 parent_id: Optional[str] = None) -> str:
        """Log an error"""
        event_id = str(uuid.uuid4())
        
        event = ConversationEvent(
            id=event_id,
            timestamp=datetime.now().isoformat(),
            event_type=EventType.ERROR,
            content={
                "error": error,
                "type": error_type
            },
            metadata={
                "conversation_id": self.current_conversation_id,
                "error_type": error_type
            },
            session_id=self.session_id,
            parent_id=parent_id
        )
        
        self._add_event(event)
        return event_id
    
    def _add_event(self, event: ConversationEvent):
        """Add event to the tracker"""
        self.events.append(event)
        
        # Maintain max events limit
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
    
    def get_conversation_events(self, conversation_id: str) -> List[ConversationEvent]:
        """Get all events for a specific conversation"""
        return [e for e in self.events if e.metadata.get("conversation_id") == conversation_id]
    
    def get_conversation_tree(self, conversation_id: str) -> Dict[str, Any]:
        """Get conversation events organized as a tree structure"""
        events = self.get_conversation_events(conversation_id)
        
        # Create a map of events by ID
        event_map = {e.id: e for e in events}
        
        # Build tree structure
        tree = {"events": [], "children": {}}
        
        for event in events:
            event_dict = asdict(event)
            event_dict["event_type"] = event.event_type.value
            
            if event.parent_id and event.parent_id in event_map:
                # This is a child event
                if event.parent_id not in tree["children"]:
                    tree["children"][event.parent_id] = []
                tree["children"][event.parent_id].append(event_dict)
            else:
                # This is a root event
                tree["events"].append(event_dict)
        
        return tree
    
    def get_recent_events(self, limit: int = 50) -> List[ConversationEvent]:
        """Get recent events"""
        return self.events[-limit:]
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of the entire session"""
        if not self.events:
            return {"total_events": 0, "conversations": 0}
        
        conversation_ids = set()
        event_counts = {}
        
        for event in self.events:
            if event.metadata.get("conversation_id"):
                conversation_ids.add(event.metadata["conversation_id"])
            
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        return {
            "session_id": self.session_id,
            "total_events": len(self.events),
            "conversations": len(conversation_ids),
            "event_counts": event_counts,
            "first_event": self.events[0].timestamp if self.events else None,
            "last_event": self.events[-1].timestamp if self.events else None
        }
    
    def export_conversation(self, conversation_id: str, format: str = "json") -> str:
        """Export a conversation in the specified format"""
        tree = self.get_conversation_tree(conversation_id)
        
        if format.lower() == "json":
            return json.dumps(tree, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def export_session(self, format: str = "json") -> str:
        """Export the entire session"""
        session_data = {
            "session_id": self.session_id,
            "summary": self.get_session_summary(),
            "events": [asdict(e) for e in self.events]
        }
        
        # Convert enum values to strings
        for event in session_data["events"]:
            event["event_type"] = event["event_type"].value if hasattr(event["event_type"], "value") else str(event["event_type"])
        
        if format.lower() == "json":
            return json.dumps(session_data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def clear_session(self):
        """Clear all events in the session"""
        self.events.clear()
        self.current_conversation_id = None
        self._event_stack.clear()


# Global tracker instance
_global_tracker: Optional[DetailedConversationTracker] = None


def get_conversation_tracker(session_id: Optional[str] = None) -> DetailedConversationTracker:
    """Get or create the global conversation tracker"""
    global _global_tracker
    
    if _global_tracker is None or (session_id and _global_tracker.session_id != session_id):
        _global_tracker = DetailedConversationTracker(session_id)
    
    return _global_tracker


def reset_conversation_tracker():
    """Reset the global conversation tracker"""
    global _global_tracker
    _global_tracker = None
