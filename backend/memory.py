import requests
import os
from dotenv import load_dotenv

load_dotenv()

HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")
BASE_URL = "https://api.hindsight.vectorize.io"

# Local fallback memory store
local_memory = {}


def get_memory(user_id, query):
    # Try Hindsight API first
    if HINDSIGHT_API_KEY:
        try:
            res = requests.post(
                f"{BASE_URL}/search",
                headers={
                    "Authorization": f"Bearer {HINDSIGHT_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "query": query,
                    "filters": {"user_id": user_id},
                    "top_k": 5
                },
                timeout=5
            )

            if res.status_code == 200:
                data = res.json()
                memories = data.get("results", [])
                return [
                    {"user": m.get("input", ""), "assistant": m.get("output", "")}
                    for m in memories
                ]
        except Exception as e:
            print("Hindsight API error, using local memory:", e)

    # Fallback to local memory
    return local_memory.get(user_id, [])[-5:]


def add_memory(user_id, user_input, response):
    # Always save locally
    if user_id not in local_memory:
        local_memory[user_id] = []
    local_memory[user_id].append({
        "user": user_input,
        "assistant": response
    })

    # Also try Hindsight API
    if HINDSIGHT_API_KEY:
        try:
            requests.post(
                f"{BASE_URL}/memories",
                headers={
                    "Authorization": f"Bearer {HINDSIGHT_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "input": user_input,
                    "output": response,
                    "metadata": {"user_id": user_id}
                },
                timeout=5
            )
        except Exception as e:
            print("Memory store error:", e)