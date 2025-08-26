

print("🌐 [WEB_APP] Starting web application initialization...")

import asyncio
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from .llm_driven_agent import LLMDrivenAWSAgent as AWSAgent
from .config import settings
from .conversation_tracker import get_conversation_tracker, reset_conversation_tracker

print("🌐 [WEB_APP] All imports loaded successfully")
print(f"🌐 [WEB_APP] Settings loaded - Host: {settings.host}, Port: {settings.port}")

# Global agent instance
aws_agent = None
print("🌐 [WEB_APP] Global agent instance initialized as None")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the lifecycle of the AWS agent"""
    global aws_agent
    
    print("🚀 [LIFESPAN] Starting application lifespan management...")
    
    # Startup
    try:
        print("🚀 [LIFESPAN] Creating AWS Agent instance...")
        aws_agent = AWSAgent()
        print("🚀 [LIFESPAN] AWS Agent instance created, starting agent...")
        await aws_agent.start()
        print("🚀 [LIFESPAN] AWS Agent initialized successfully")
    except Exception as e:
        print(f"❌ [LIFESPAN] Failed to initialize AWS Agent: {e}")
        import traceback
        traceback.print_exc()
        aws_agent = None
    
    yield
    
    # Shutdown
    print("🛑 [LIFESPAN] Application shutdown initiated...")
    if aws_agent:
        print("🛑 [LIFESPAN] Shutting down AWS Agent...")
        try:
            await aws_agent.stop()
            print("🛑 [LIFESPAN] AWS Agent shutdown completed")
        except Exception as e:
            print(f"❌ [LIFESPAN] Error shutting down agent: {e}")
    else:
        print("🛑 [LIFESPAN] No AWS Agent to shutdown")

print("🌐 [WEB_APP] Creating FastAPI app...")
# Create FastAPI app
app = FastAPI(
    title="AWS Chatbot",
    description="AI-powered chatbot for AWS service management",
    version="1.0.0",
    lifespan=lifespan
)
print("🌐 [WEB_APP] FastAPI app created successfully")

print("🌐 [WEB_APP] Mounting static files and templates...")
# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
print("🌐 [WEB_APP] Static files and templates mounted successfully")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main chatbot interface"""
    print(f"🏠 [HOME] Serving home page to client: {request.client.host}")
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/conversation-viewer", response_class=HTMLResponse)
async def conversation_viewer(request: Request):
    """Serve the detailed conversation viewer interface"""
    return templates.TemplateResponse("conversation_viewer.html", {"request": request})

@app.post("/chat")
async def chat(request: Request, message: str = Form(...)):
    """Handle chat messages"""
    global aws_agent
    
    print(f"💬 [CHAT] Received chat message from {request.client.host}: '{message[:100]}...'")
    
    if not aws_agent:
        print("❌ [CHAT] AWS Agent not available")
        raise HTTPException(status_code=503, detail="AWS Agent not available")
    
    try:
        print(f"💬 [CHAT] Processing query with AWS Agent...")
        response = await aws_agent.process_query(message)
        print(f"✅ [CHAT] Query processed successfully, response length: {len(response)}")
        return JSONResponse({
            "success": True,
            "response": response,
            "message": message
        })
    except Exception as e:
        print(f"❌ [CHAT] Error processing query: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({
            "success": False,
            "error": str(e),
            "message": message
        }, status_code=500)

@app.post("/api/chat")
async def api_chat(request: Request):
    """API endpoint for chat messages (JSON)"""
    global aws_agent
    
    if not aws_agent:
        raise HTTPException(status_code=503, detail="AWS Agent not available")
    
    try:
        data = await request.json()
        message = data.get("message", "")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        response = await aws_agent.process_query(message)
        
        # Get memory statistics
        memory_stats = aws_agent.get_memory_stats()
        
        return JSONResponse({
            "success": True,
            "response": response,
            "message": message,
            "memory": {
                "total_interactions": memory_stats['total_interactions'],
                "recent_commands_count": len(memory_stats['recent_commands']),
                "has_context": memory_stats['total_interactions'] > 0
            }
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.get("/api/suggest")
async def suggest_commands(query: str):
    """Suggest AWS CLI commands for a query"""
    global aws_agent
    
    if not aws_agent:
        raise HTTPException(status_code=503, detail="AWS Agent not available")
    
    try:
        suggestions = await aws_agent.suggest_commands(query)
        return JSONResponse({
            "success": True,
            "suggestions": suggestions,
            "query": query
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e),
            "query": query
        }, status_code=500)

@app.post("/api/execute")
async def execute_command(request: Request):
    """Execute an AWS CLI command"""
    global aws_agent
    
    if not aws_agent:
        raise HTTPException(status_code=503, detail="AWS Agent not available")
    
    try:
        data = await request.json()
        command = data.get("command", "")
        
        if not command:
            raise HTTPException(status_code=400, detail="Command is required")
        
        result = await aws_agent.execute_command(command)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.get("/api/memory")
async def get_memory_stats():
    """Get conversation memory statistics"""
    global aws_agent
    
    if not aws_agent:
        raise HTTPException(status_code=503, detail="AWS Agent not available")
    
    try:
        memory_stats = aws_agent.get_memory_stats()
        return JSONResponse({
            "success": True,
            "memory": memory_stats
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.post("/api/memory/clear")
async def clear_memory():
    """Clear conversation memory"""
    global aws_agent
    
    if not aws_agent:
        raise HTTPException(status_code=503, detail="AWS Agent not available")
    
    try:
        aws_agent.clear_memory()
        return JSONResponse({
            "success": True,
            "message": "Memory cleared successfully"
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.get("/api/conversation/detailed")
async def get_detailed_conversation(
    conversation_id: Optional[str] = Query(None, description="Specific conversation ID"),
    limit: int = Query(50, description="Number of recent events to return")
):
    """Get detailed conversation events including LLM-tool interactions"""
    try:
        tracker = get_conversation_tracker()
        
        if conversation_id:
            # Get specific conversation as tree structure
            conversation_tree = tracker.get_conversation_tree(conversation_id)
            return JSONResponse({
                "success": True,
                "conversation_id": conversation_id,
                "data": conversation_tree
            })
        else:
            # Get recent events
            recent_events = tracker.get_recent_events(limit)
            events_data = []
            
            for event in recent_events:
                event_dict = {
                    "id": event.id,
                    "timestamp": event.timestamp,
                    "event_type": event.event_type.value,
                    "content": event.content,
                    "metadata": event.metadata,
                    "session_id": event.session_id,
                    "parent_id": event.parent_id,
                    "duration_ms": event.duration_ms
                }
                events_data.append(event_dict)
            
            return JSONResponse({
                "success": True,
                "events": events_data,
                "total_events": len(events_data)
            })
            
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.get("/api/conversation/export")
async def export_conversation(
    conversation_id: Optional[str] = Query(None, description="Specific conversation ID to export"),
    format: str = Query("json", description="Export format (json)")
):
    """Export conversation data"""
    try:
        tracker = get_conversation_tracker()
        
        if conversation_id:
            exported_data = tracker.export_conversation(conversation_id, format)
            filename = f"conversation_{conversation_id}.{format}"
        else:
            exported_data = tracker.export_session(format)
            filename = f"session_{tracker.session_id}.{format}"
        
        return JSONResponse({
            "success": True,
            "data": exported_data,
            "filename": filename
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.get("/api/conversation/summary")
async def get_conversation_summary():
    """Get session summary with conversation statistics"""
    try:
        tracker = get_conversation_tracker()
        summary = tracker.get_session_summary()
        
        return JSONResponse({
            "success": True,
            "summary": summary
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.post("/api/conversation/clear")
async def clear_detailed_conversation():
    """Clear detailed conversation tracking"""
    try:
        tracker = get_conversation_tracker()
        tracker.clear_session()
        
        return JSONResponse({
            "success": True,
            "message": "Detailed conversation tracking cleared"
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.get("/api/conversation/events/filter")
async def filter_conversation_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    conversation_id: Optional[str] = Query(None, description="Filter by conversation ID"),
    limit: int = Query(100, description="Maximum number of events to return")
):
    """Filter conversation events by type or conversation ID"""
    try:
        tracker = get_conversation_tracker()
        
        if conversation_id:
            events = tracker.get_conversation_events(conversation_id)
        else:
            events = tracker.get_recent_events(limit * 2)  # Get more to filter
        
        # Filter by event type if specified
        if event_type:
            events = [e for e in events if e.event_type.value == event_type]
        
        # Limit results
        events = events[:limit]
        
        events_data = []
        for event in events:
            event_dict = {
                "id": event.id,
                "timestamp": event.timestamp,
                "event_type": event.event_type.value,
                "content": event.content,
                "metadata": event.metadata,
                "session_id": event.session_id,
                "parent_id": event.parent_id,
                "duration_ms": event.duration_ms
            }
            events_data.append(event_dict)
        
        return JSONResponse({
            "success": True,
            "events": events_data,
            "filters": {
                "event_type": event_type,
                "conversation_id": conversation_id,
                "limit": limit
            },
            "total_events": len(events_data)
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global aws_agent
    
    print(f"🏥 [HEALTH] Health check requested")
    print(f"🏥 [HEALTH] AWS Agent available: {aws_agent is not None}")
    
    memory_info = {}
    detailed_tracking_info = {}
    
    if aws_agent:
        try:
            print(f"🏥 [HEALTH] Getting memory stats from AWS Agent...")
            memory_stats = aws_agent.get_memory_stats()
            memory_info = {
                "total_interactions": memory_stats['total_interactions'],
                "recent_commands_count": len(memory_stats['recent_commands'])
            }
            print(f"🏥 [HEALTH] Memory stats retrieved: {memory_info}")
        except Exception as e:
            print(f"❌ [HEALTH] Error getting memory stats: {e}")
            memory_info = {"error": "Could not retrieve memory stats"}
    else:
        print(f"🏥 [HEALTH] AWS Agent not available, skipping memory stats")
    
    try:
        print(f"🏥 [HEALTH] Getting conversation tracker...")
        tracker = get_conversation_tracker()
        summary = tracker.get_session_summary()
        detailed_tracking_info = {
            "session_id": summary.get("session_id"),
            "total_events": summary.get("total_events", 0),
            "conversations": summary.get("conversations", 0),
            "event_counts": summary.get("event_counts", {})
        }
        print(f"🏥 [HEALTH] Tracking info retrieved: {detailed_tracking_info}")
    except Exception as e:
        print(f"❌ [HEALTH] Error getting tracking info: {e}")
        detailed_tracking_info = {"error": "Could not retrieve detailed tracking info"}
    
    response_data = {
        "status": "healthy",
        "agent_available": aws_agent is not None,
        "memory": memory_info,
        "detailed_tracking": detailed_tracking_info,
        "settings": {
            "aws_region": settings.aws_region,
            "read_only": settings.read_operations_only,
            "model": settings.llm_model
        }
    }
    
    print(f"🏥 [HEALTH] Returning health response: {response_data}")
    return JSONResponse(response_data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "aws_chatbot.web_app:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )


