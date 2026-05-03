from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from schemas import ChatRequest, ChatResponse
from memory import get_memory, add_memory
from llm import generate_response

app = FastAPI(title="ElectionGuide API", description="Interactive Voting Assistant")

@app.get("/health")
def health_check() -> dict:
    """Health check endpoint for Cloud Run."""
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> dict:
    """Handles chat messages and returns AI responses."""
    user_id = request.user_id
    user_input = request.message

    memory = get_memory(user_id, user_input)
    response = generate_response(user_input, memory)
    add_memory(user_id, user_input, response)

    return {"response": response}

# Serve frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
def serve_index():
    """Serves the main HTML interface."""
    return FileResponse(os.path.join(frontend_path, "index.html"))
