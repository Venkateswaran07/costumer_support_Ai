# 🗳️ ElectionGuide (Interactive Voting Assistant)

An intelligent, interactive assistant that helps users understand the election process, voting timelines, registration steps, and voter ID requirements in an easy-to-follow, step-by-step manner.

---

## 📌 What Is This Project?

This is a **full-stack AI assistant** built to simplify the democratic process. Unlike generic search engines, this agent:

- **Provides clear, step-by-step guidance** on how to register and vote
- **Formats timelines and dates clearly** using Markdown tables
- **Remembers past questions** within the session to provide context-aware help
- **Stays neutral and informative**, focusing purely on the 'how-to' of voting

---

## 🔧 Technologies Used & How We Used Them

### 1. 🐍 Python (Backend Language)
**What:** Python is the core programming language for the backend server.  
**How we used it:** All backend logic — API handling, LLM calls, memory management, and data validation — is written in Python. We chose Python for its rich ecosystem of AI/ML libraries and simplicity.

---

### 2. ⚡ FastAPI (Web Framework)
**What:** FastAPI is a modern, high-performance Python web framework for building APIs.  
**How we used it:**  
- Created a `POST /chat` endpoint in `main.py` that receives user messages and returns AI responses
- Added **CORS middleware** so the frontend (running on a different origin) can communicate with the backend
- Used FastAPI's automatic request validation with Pydantic models

```python
# main.py — API endpoint
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    memory = get_memory(user_id, user_input)
    response = generate_response(user_input, memory)
    add_memory(user_id, user_input, response)
    return {"response": response}
```

---

### 3. 🦙 Groq Cloud API + LLaMA 3.3 70B (LLM Engine)
**What:** Groq provides ultra-fast inference for open-source LLMs. We use the **LLaMA 3.3 70B Versatile** model.  
**How we used it:**  
- In `llm.py`, we send a structured prompt to the Groq API via HTTP POST request
- The prompt includes the user's current issue + their past conversation history
- The model is instructed to act as a neutral election assistant, formatting timelines and steps clearly using Markdown tables
- We use the OpenAI-compatible chat completions endpoint (`/v1/chat/completions`)

```python
# llm.py — Sending prompt to Groq
data = {
    "model": "llama-3.3-70b-versatile",
    "messages": [
        {"role": "user", "content": prompt}
    ]
}
response = requests.post("https://api.groq.com/openai/v1/chat/completions",
                         headers=headers, json=data)
```

**Why Groq?** It runs LLMs on custom LPU hardware, delivering responses in milliseconds — much faster than traditional GPU-based inference.

---

### 4. 🧠 Hindsight Vector Database (Long-Term Memory)
**What:** Hindsight (by Vectorize) is a vector database API that stores and retrieves memories using semantic search.  
**How we used it:**  
- In `memory.py`, when a user sends a message, we **search** Hindsight for semantically similar past interactions
- After the AI responds, we **store** the new interaction (question + answer) in Hindsight
- This allows the agent to recall relevant past conversations even across server restarts
- We retrieve the **top 5 most relevant** past interactions to include in the LLM prompt

```python
# memory.py — Semantic search for past interactions
res = requests.post(f"{BASE_URL}/search", json={
    "query": query,
    "filters": {"user_id": user_id},
    "top_k": 5
})
```

---

### 5. 💾 In-Memory Fallback (Local Memory)
**What:** A Python dictionary that stores conversations in RAM.  
**How we used it:**  
- If the Hindsight API is unavailable or the API key is not configured, the system **automatically falls back** to local memory
- Conversations are stored per `user_id` and the last 5 interactions are used for context
- This ensures the app **never crashes** due to external API failures

```python
# memory.py — Local fallback
local_memory = {}

def get_memory(user_id, query):
    # Try Hindsight first, fall back to local
    return local_memory.get(user_id, [])[-5:]
```

---

### 6. 📐 Pydantic (Data Validation)
**What:** Pydantic is a Python library for data validation using type annotations.  
**How we used it:**  
- Defined `ChatRequest` and `ChatResponse` models in `schemas.py`
- FastAPI automatically validates incoming JSON requests against these models
- If a user sends invalid data (e.g., missing `message` field), the API returns a clear error

```python
# schemas.py
class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
```

---

### 7. 🔐 python-dotenv (Environment Configuration)
**What:** A library that loads environment variables from a `.env` file.  
**How we used it:**  
- API keys (`GROQ_API_KEY`, `HINDSIGHT_API_KEY`) are stored in a `.env` file
- `config.py` loads these at startup using `load_dotenv()`
- Keys are **never hardcoded** in source code — the `.env` file is excluded from Git via `.gitignore`

```python
# config.py
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
```

---

### 8. 🌐 HTML + CSS + JavaScript (Frontend)
**What:** Standard web technologies for the user interface.  
**How we used it:**

| File | Purpose |
|------|---------|
| `index.html` | Page structure — chat box, input field, send button |
| `style.css` | Styling — layout, chat box borders, font |
| `app.js` | Logic — sends messages to backend via `fetch()`, displays responses |

```javascript
// app.js — Sending a message to the backend
const res = await fetch("http://127.0.0.1:8000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: "user1", message: message })
});
const data = await res.json();
addMessage("AI: " + data.response);
```

---

### 9. 🚀 Uvicorn (ASGI Server)
**What:** Uvicorn is a lightning-fast ASGI server for running FastAPI applications.  
**How we used it:**  
- We run the backend with `uvicorn main:app --reload`
- The `--reload` flag enables hot-reloading during development
- The server runs at `http://127.0.0.1:8000`

---

## 🏗️ Architecture Diagram

```
┌─────────────────────┐         ┌──────────────────────────────┐
│                     │  HTTP   │                              │
│   Frontend (HTML)   │◄──────►│   Backend (FastAPI + Python)  │
│   - index.html      │  POST   │   - main.py (API server)     │
│   - app.js          │ /chat   │   - llm.py (Groq LLM calls)  │
│   - style.css       │         │   - memory.py (memory store)  │
│                     │         │   - schemas.py (data models)  │
│                     │         │   - config.py (env config)    │
└─────────────────────┘         └──────────────────────────────┘
                                          │
                                          │ API Calls
                                          ▼
                                ┌───────────────────┐
                                │   Groq Cloud API  │
                                │ (LLaMA 3.3 70B)   │
                                └───────────────────┘
                                          │
                                          ▼
                                ┌───────────────────┐
                                │  Hindsight API     │
                                │ (Vector Memory DB) │
                                │ + Local Fallback   │
                                └───────────────────┘
```

---

## ⚙️ How the Chat Flow Works

```
User types a message
        │
        ▼
Frontend (app.js) sends POST /chat
        │
        ▼
Backend (main.py) receives the request
        │
        ├──► memory.py: Search for past conversations
        │    (Hindsight API → fallback to local memory)
        │
        ├──► llm.py: Build prompt with history + user issue
        │    Send to Groq API → get AI response
        │
        ├──► memory.py: Save new interaction
        │
        ▼
Return AI response → Frontend displays it
```

---

## 📂 Project Structure

```
costumer_support_Ai/
│
├── frontend/                   # Client-side UI
│   ├── index.html              # Main HTML page with chat interface
│   ├── app.js                  # Chat logic — fetch API calls to backend
│   └── style.css               # Basic styling for the chat box
│
├── backend/                    # Server-side logic
│   ├── main.py                 # FastAPI app — /chat endpoint + CORS
│   ├── llm.py                  # LLM integration — prompt building + Groq API
│   ├── memory.py               # Dual memory — Hindsight API + local fallback
│   ├── schemas.py              # Pydantic models — ChatRequest, ChatResponse
│   └── config.py               # Environment config — loads API keys from .env
│
├── article.md                  # Detailed article about the building process
├── Video Project 4.mp4         # Walkthrough/Demo video
├── requirements.txt            # Python dependencies
├── .env                        # API keys (excluded from Git)
├── .gitignore                  # Files to exclude from version control
└── README.md                   # Project documentation (this file)
```

---

## 🚀 Setup & Installation

### Prerequisites
- **Python 3.10+**
- A **[Groq API Key](https://console.groq.com/keys)** (free tier available)
- *(Optional)* A Hindsight API Key for persistent vector memory

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Venkateswaran07/costumer_support_Ai.git
cd costumer_support_Ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file with your API keys
echo GROQ_API_KEY=your_key_here > .env
echo HINDSIGHT_API_KEY=your_key_here >> .env

# 4. Start the backend server
cd backend
uvicorn main:app --reload

# 5. Open frontend/index.html in your browser
```

---

## 📡 API Reference

### `POST /chat`

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | string | Unique identifier for the user |
| `message` | string | The user's support question/issue |

**Example Request:**
```json
{ "user_id": "user1", "message": "My payment failed" }
```

**Example Response:**
```json
{ "response": "I can help with that! First, please check if your card..." }
```

---

## 🧠 Key Features

| Feature | Description |
|---------|-------------|
| 🗳️ **Interactive Election Guide** | Provides clear, neutral voting instructions |
| 📅 **Timeline Formatting** | Automatically structures key dates into readable Markdown tables |
| 🧠 **Conversation Memory** | Remembers past interactions per user |
| 💾 **Dual Memory System** | Vector DB (Hindsight) + automatic local fallback |
| ⚡ **Ultra-Fast Responses** | Groq LPU delivers millisecond LLM inference |
| 🛡️ **Error Resilient** | Graceful handling — never crashes on API failures |
| 🔐 **Secure Config** | API keys in .env, excluded from Git |

---

## 📝 Future Improvements

- [ ] Premium UI with chat bubbles, typing indicators, and animations
- [ ] User authentication and session management
- [ ] File/image upload support for describing issues
- [ ] Auto-generate support tickets for unresolved issues
- [ ] Admin dashboard to monitor all conversations
- [ ] Deploy to cloud (Render / Railway / Vercel)
- [ ] Add multi-language support

---

## 👨‍💻 Author

**Venkateswaran**  
GitHub: [@Venkateswaran07](https://github.com/Venkateswaran07)

---

## 📄 License

This project is for educational and personal use.
