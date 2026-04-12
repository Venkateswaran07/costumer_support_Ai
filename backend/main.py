from fastapi import FastAPI
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

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    user_id = request.user_id
    user_input = request.message

    memory = get_memory(user_id, user_input)

    response = generate_response(user_input, memory)

    add_memory(user_id, user_input, response)

    return {"response": response}