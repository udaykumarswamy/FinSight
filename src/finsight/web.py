"""
Web server for FinSight UI using FastAPI.
"""
import asyncio
import json
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os
import threading
from queue import Queue

# Load environment variables
load_dotenv()

from finsight.agent import Agent

app = FastAPI(title="FinSight Web UI")

# Create templates directory if it doesn't exist
templates_dir = os.path.join(os.path.dirname(__file__), "..", "..", "templates")
static_dir = os.path.join(os.path.dirname(__file__), "..", "..", "static")

os.makedirs(templates_dir, exist_ok=True)
os.makedirs(static_dir, exist_ok=True)

templates = Jinja2Templates(directory=templates_dir)

# Store active query queues for SSE streaming
active_queues: dict[str, Queue] = {}

# Store agent instances per session to maintain conversation context
session_agents: dict[str, Agent] = {}


def get_or_create_agent(session_id: str) -> Agent:
    """Get an existing agent for a session or create a new one."""
    if session_id not in session_agents:
        session_agents[session_id] = Agent()
    return session_agents[session_id]


def run_agent_with_streaming(query: str, query_id: str, session_id: str):
    """Run the agent and stream progress updates to the queue."""
    queue = active_queues.get(query_id)
    if not queue:
        return
    
    # Get or create agent for this session to maintain conversation context
    agent = get_or_create_agent(session_id)
    
    # Add user message to conversation history to maintain context
    agent.conversation_history.add_user_message(query)
    
    try:
        # Send initial message
        queue.put({"type": "status", "message": "Starting analysis...", "data": None})
        
        # Subscribe to logger messages
        def log_callback(msg: str):
            """Callback to stream log messages to the queue."""
            if queue:
                queue.put({"type": "log", "message": msg, "data": None})
        
        # Subscribe to the logger
        agent.logger.subscribe(log_callback)
        
        try:
            # Run the agent
            queue.put({"type": "status", "message": "Processing your query...", "data": None})
            result = agent.run(query)
            
            # Handle both old string format and new dict format
            if isinstance(result, dict):
                answer = result.get("answer", "")
                plot_data = result.get("plot_data", None)
            else:
                # Fallback for old format (string)
                answer = str(result)
                plot_data = None
            
            # Send plot data if available
            if plot_data:
                queue.put({"type": "plot", "message": "Chart data available", "data": plot_data})
            
            # Send final answer
            queue.put({"type": "answer", "message": "Analysis complete!", "data": answer})
        finally:
            # Unsubscribe from logger
            agent.logger.unsubscribe(log_callback)
        
        queue.put({"type": "done", "message": "", "data": None})
        
    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        queue.put({"type": "error", "message": error_msg, "data": None})
        queue.put({"type": "done", "message": "", "data": None})
    finally:
        # Clean up after a delay
        def cleanup():
            import time
            time.sleep(5)
            if query_id in active_queues:
                del active_queues[query_id]
        
        threading.Thread(target=cleanup, daemon=True).start()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main UI page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/query")
async def process_query(request: Request):
    """Process a user query and return a query ID for SSE streaming."""
    data = await request.json()
    query = data.get("query", "").strip()
    session_id = data.get("session_id", None)
    
    if not query:
        return {"error": "Query cannot be empty", "query_id": None}
    
    import uuid
    # Generate session_id if not provided
    if not session_id:
        session_id = str(uuid.uuid4())
    
    query_id = str(uuid.uuid4())
    queue = Queue()
    active_queues[query_id] = queue
    
    # Start agent in a separate thread
    thread = threading.Thread(
        target=run_agent_with_streaming,
        args=(query, query_id, session_id),
        daemon=True
    )
    thread.start()
    
    return {"query_id": query_id, "session_id": session_id, "status": "started"}


@app.post("/api/clear-session")
async def clear_session(request: Request):
    """Clear a session's agent and conversation history."""
    data = await request.json()
    session_id = data.get("session_id", None)
    
    if session_id and session_id in session_agents:
        del session_agents[session_id]
        return {"status": "cleared", "message": "Session cleared successfully"}
    
    return {"status": "not_found", "message": "Session not found"}


@app.get("/api/stream/{query_id}")
async def stream_updates(query_id: str):
    """Stream updates for a query using Server-Sent Events."""
    queue = active_queues.get(query_id)
    
    if not queue:
        return StreamingResponse(
            iter([b'data: {"type": "error", "message": "Query not found"}\n\n']),
            media_type="text/event-stream"
        )
    
    async def event_generator():
        while True:
            try:
                # Wait for message with timeout
                try:
                    message = queue.get(timeout=1)
                except:
                    # Send heartbeat
                    yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
                    continue
                
                if message["type"] == "done":
                    yield f"data: {json.dumps(message)}\n\n"
                    break
                
                yield f"data: {json.dumps(message)}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                break
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


def main():
    """Entry point for the web server."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()

