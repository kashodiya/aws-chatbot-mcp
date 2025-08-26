

import asyncio
import json
from typing import Dict, Any
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from .working_agent import WorkingAWSAgent as AWSAgent
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
        return JSONResponse({
            "success": True,
            "response": response,
            "message": message
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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global aws_agent
    
    return JSONResponse({
        "status": "healthy",
        "agent_available": aws_agent is not None,
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


