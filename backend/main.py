from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from schemas import ChatRequest, ChatResponse
from memory import get_memory, add_memory
from llm import generate_response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
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
    return FileResponse(os.path.join(frontend_path, "index.html"))
