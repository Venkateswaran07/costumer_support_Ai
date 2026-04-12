import requests
import os
from dotenv import load_dotenv

load_dotenv()

HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")
BASE_URL = "https://api.hindsight.vectorize.io"
BANK_ID = "venkates123"

# Local fallback memory store
local_memory = {}


def get_memory(user_id, query):
    # Try Hindsight API first
    if HINDSIGHT_API_KEY:
        try:
            res = requests.post(
                f"{BASE_URL}/v1/default/banks/{BANK_ID}/memories/search",
                headers={
                    "Authorization": f"Bearer {HINDSIGHT_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "query": query
                },
                timeout=10
            )

            print("RECALL STATUS:", res.status_code)
            print("RECALL RESPONSE:", res.text[:500])

            if res.status_code == 200:
                data = res.json()
                results = data.get("results", [])
                return [
                    {"user": r.get("text", ""), "assistant": ""}
                    for r in results
                ]
        except Exception as e:
            print("Hindsight recall error, using local memory:", e)

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

    # Also try Hindsight API (retain)
    if HINDSIGHT_API_KEY:
        try:
            content = f"User ({user_id}) asked: {user_input}\nAssistant replied: {response}"
            res = requests.post(
                f"{BASE_URL}/v1/default/banks/{BANK_ID}/memories/retain",
                headers={
                    "Authorization": f"Bearer {HINDSIGHT_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "messages": [
                        {"role": "user", "content": user_input},
                        {"role": "assistant", "content": response}
                    ]
                },
                timeout=10
            )
            print("RETAIN STATUS:", res.status_code)
            print("RETAIN RESPONSE:", res.text[:300])
        except Exception as e:
            print("Hindsight retain error:", e)