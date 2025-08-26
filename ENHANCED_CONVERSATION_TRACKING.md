
# Enhanced Conversation Tracking for MCP Agent

This document describes the enhanced conversation tracking system that provides complete visibility into all LLM-to-tool interactions in the AWS Chatbot MCP Agent.

## Overview

The enhanced conversation tracking system captures every aspect of the agent's decision-making process, including:

- User messages and agent responses
- LLM requests and responses (with timing)
- Tool calls and their results
- Command executions and outputs
- Internal agent reasoning
- Error handling and debugging information

## Features

### 🔍 Complete Conversation Visibility

- **LLM Interactions**: Full request/response logging with model, messages, and tools
- **Tool Calls**: Detailed logging of tool invocations and results
- **Command Execution**: AWS CLI command tracking with timing and results
- **Agent Reasoning**: Internal decision-making process capture
- **Error Tracking**: Comprehensive error logging and debugging

### 📊 Real-time Analytics

- **Session Statistics**: Total events, conversations, and event type breakdowns
- **Performance Metrics**: Timing data for LLM calls, tool executions, and commands
- **Conversation Trees**: Hierarchical view of related events
- **Event Filtering**: Filter by type, conversation, or time period

### 💾 Export Capabilities

- **JSON Export**: Complete session or individual conversation export
- **Structured Data**: Well-organized data for analysis and debugging
- **API Access**: RESTful endpoints for programmatic access

### 🌐 Web Interface

- **Main Chat Interface**: Enhanced with tracking statistics
- **Detailed Viewer**: Comprehensive conversation analysis tool
- **Real-time Updates**: Live tracking information and statistics

## Architecture

### Core Components

1. **DetailedConversationTracker**: Main tracking class that captures all events
2. **ConversationEvent**: Individual event data structure
3. **EventType**: Enumeration of all trackable event types
4. **Enhanced LLM Adapter**: Modified to log all LLM interactions
5. **Enhanced Agent**: Modified to log reasoning and decision-making

### Event Types

- `USER_MESSAGE`: User input to the agent
- `AGENT_RESPONSE`: Final agent response to user
- `LLM_REQUEST`: Request sent to the LLM (with model, messages, tools)
- `LLM_RESPONSE`: Response from the LLM (with content, tool calls, timing)
- `TOOL_CALL`: Tool invocation (with name, arguments)
- `TOOL_RESPONSE`: Tool execution result (with success, output, timing)
- `COMMAND_EXECUTION`: AWS CLI command execution
- `COMMAND_RESULT`: Command execution result (with output, errors, timing)
- `AGENT_REASONING`: Internal agent decision-making process
- `ERROR`: Error events with context and debugging information
- `SYSTEM_EVENT`: System-level events and notifications

## API Endpoints

### GET /api/conversation/detailed
Returns detailed conversation events with full LLM-tool interaction data.

**Parameters:**
- `conversation_id` (optional): Specific conversation ID
- `limit` (optional): Number of recent events to return (default: 50)

**Response:**
```json
{
  "success": true,
  "events": [
    {
      "id": "event-uuid",
      "timestamp": "2025-01-01T12:00:00Z",
      "event_type": "llm_request",
      "content": {
        "messages": [...],
        "tools": [...],
        "model": "gpt-4"
      },
      "metadata": {
        "conversation_id": "conv-uuid",
        "message_count": 2,
        "has_tools": true,
        "tool_count": 5
      },
      "session_id": "session-uuid",
      "parent_id": null,
      "duration_ms": 1250.5
    }
  ],
  "total_events": 25
}
```

### GET /api/conversation/summary
Returns session-level statistics and summaries.

**Response:**
```json
{
  "success": true,
  "summary": {
    "session_id": "session-uuid",
    "total_events": 150,
    "conversations": 5,
    "event_counts": {
      "user_message": 5,
      "agent_response": 5,
      "llm_request": 8,
      "llm_response": 8,
      "tool_call": 12,
      "tool_response": 12,
      "command_execution": 3,
      "command_result": 3,
      "agent_reasoning": 10
    },
    "first_event": "2025-01-01T12:00:00Z",
    "last_event": "2025-01-01T12:30:00Z"
  }
}
```

### GET /api/conversation/export
Exports conversation data in JSON format.

**Parameters:**
- `conversation_id` (optional): Specific conversation to export
- `format` (optional): Export format (currently only "json")

**Response:**
```json
{
  "success": true,
  "data": "{ ... exported JSON data ... }",
  "filename": "session_uuid.json"
}
```

### GET /api/conversation/events/filter
Filters events by type, conversation, or other criteria.

**Parameters:**
- `event_type` (optional): Filter by specific event type
- `conversation_id` (optional): Filter by conversation ID
- `limit` (optional): Maximum events to return (default: 100)

### POST /api/conversation/clear
Clears all conversation tracking data.

**Response:**
```json
{
  "success": true,
  "message": "Detailed conversation tracking cleared"
}
```

### GET /health (Enhanced)
Health check endpoint now includes detailed tracking information.

**Response:**
```json
{
  "status": "healthy",
  "agent_available": true,
  "memory": {
    "total_interactions": 5,
    "recent_commands_count": 3
  },
  "detailed_tracking": {
    "session_id": "session-uuid",
    "total_events": 150,
    "conversations": 5,
    "event_counts": { ... }
  },
  "settings": { ... }
}
```

## Web Interface

### Main Chat Interface (/)
Enhanced with real-time tracking statistics:
- Session event count
- Active conversations
- Top event types
- Link to detailed viewer

### Detailed Conversation Viewer (/conversation-viewer)
Comprehensive analysis interface featuring:
- **Event Timeline**: Chronological view of all events
- **Event Filtering**: Filter by type, conversation, or time
- **Event Details**: Expandable cards with full event data
- **Session Statistics**: Real-time tracking metrics
- **Export Functions**: Download conversation data
- **Tree View**: Hierarchical event relationships (coming soon)

## Usage Examples

### Basic Usage

```python
from aws_chatbot.conversation_tracker import get_conversation_tracker

# Get the global tracker
tracker = get_conversation_tracker()

# Start a conversation
conversation_id = tracker.start_conversation("List my EC2 instances")

# The agent automatically logs all events during processing
response = await agent.process_query("List my EC2 instances")

# Get conversation events
events = tracker.get_conversation_events(conversation_id)

# Export conversation
exported_data = tracker.export_conversation(conversation_id)
```

### Advanced Analysis

```python
# Get session summary
summary = tracker.get_session_summary()
print(f"Total events: {summary['total_events']}")
print(f"Event breakdown: {summary['event_counts']}")

# Filter events by type
llm_requests = [e for e in tracker.get_recent_events(100) 
                if e.event_type.value == 'llm_request']

# Analyze performance
durations = [e.duration_ms for e in tracker.get_recent_events(100) 
             if e.duration_ms is not None]
avg_duration = sum(durations) / len(durations) if durations else 0
```

## Configuration

### Enable Debug Logging
Update `mcp_agent.config.yaml`:

```yaml
logger:
  level: debug
  transports: [console, file]
  path: "logs/mcp-agent-detailed.jsonl"
```

### Tracking Settings
The conversation tracker can be configured with:

```python
tracker = DetailedConversationTracker(
    session_id="custom-session-id",
    max_events=2000  # Maximum events to keep in memory
)
```

## Performance Considerations

- **Memory Usage**: Events are kept in memory with configurable limits
- **Storage**: File-based logging available for persistence
- **Performance Impact**: Minimal overhead (~1-2ms per event)
- **Scalability**: Designed for single-session use; consider external storage for multi-session deployments

## Security and Privacy

- **Sensitive Data**: Be aware that all LLM interactions are logged
- **API Keys**: Ensure API keys are not logged in request/response data
- **Data Retention**: Implement appropriate data retention policies
- **Access Control**: Secure the conversation viewer and API endpoints

## Troubleshooting

### Common Issues

1. **Missing Events**: Ensure the tracker is initialized before agent operations
2. **Memory Usage**: Adjust `max_events` if memory usage is too high
3. **Performance**: Disable detailed tracking in production if performance is critical
4. **Export Errors**: Check that the session has events before exporting

### Debug Mode

Enable debug logging to see detailed tracking information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- **Tree View**: Visual representation of event hierarchies
- **Real-time Streaming**: WebSocket-based live event streaming
- **Advanced Filtering**: More sophisticated event filtering options
- **Performance Analytics**: Detailed performance analysis and optimization suggestions
- **Integration**: Integration with external monitoring and analytics systems
- **Persistence**: Database-backed storage for long-term retention

## Contributing

To contribute to the enhanced conversation tracking system:

1. Follow the existing event structure and naming conventions
2. Add appropriate metadata to new event types
3. Update the web interface for new event types
4. Add tests for new tracking functionality
5. Update documentation for new features

## License

This enhanced conversation tracking system is part of the AWS Chatbot MCP Agent project and follows the same license terms.

