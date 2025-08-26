

import asyncio
import json
from typing import Dict, Any
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from .llm_driven_agent import LLMDrivenAWSAgent as AWSAgent
from .config import settings

# Global agent instance
aws_agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the lifecycle of the AWS agent"""
    global aws_agent
    
    # Startup
    try:
        aws_agent = AWSAgent()
        await aws_agent.start()
        print("AWS Agent initialized successfully")
    except Exception as e:
        print(f"Failed to initialize AWS Agent: {e}")
        import traceback
        traceback.print_exc()
        aws_agent = None
    
    yield
    
    # Shutdown
    if aws_agent:
        print("Shutting down AWS Agent")
        try:
            await aws_agent.stop()
        except Exception as e:
            print(f"Error shutting down agent: {e}")

# Create FastAPI app
app = FastAPI(
    title="AWS Chatbot",
    description="AI-powered chatbot for AWS service management",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main chatbot interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(request: Request, message: str = Form(...)):
    """Handle chat messages"""
    global aws_agent
    
    if not aws_agent:
        raise HTTPException(status_code=503, detail="AWS Agent not available")
    
    try:
        response = await aws_agent.process_query(message)
        return JSONResponse({
            "success": True,
            "response": response,
            "message": message
        })
    except Exception as e:
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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global aws_agent
    
    memory_info = {}
    if aws_agent:
        try:
            memory_stats = aws_agent.get_memory_stats()
            memory_info = {
                "total_interactions": memory_stats['total_interactions'],
                "recent_commands_count": len(memory_stats['recent_commands'])
            }
        except:
            memory_info = {"error": "Could not retrieve memory stats"}
    
    return JSONResponse({
        "status": "healthy",
        "agent_available": aws_agent is not None,
        "memory": memory_info,
        "settings": {
            "aws_region": settings.aws_region,
            "read_only": settings.read_operations_only,
            "model": settings.llm_model
        }
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "aws_chatbot.web_app:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )


