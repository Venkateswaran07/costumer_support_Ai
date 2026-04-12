import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")
BASE_URL = os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io")
BANK_ID = os.getenv("HINDSIGHT_BANK_ID", "customer-support-agent")

# Local fallback memory store
local_memory = {}
_hindsight_client = None
_hindsight_bank_ready = False


def _get_hindsight_client():
    """Create and cache a Hindsight client only when API key is configured."""
    global _hindsight_client

    if not HINDSIGHT_API_KEY:
        return None

    if _hindsight_client is not None:
        return _hindsight_client

    _hindsight_client = Hindsight(
        base_url=BASE_URL,
        api_key=HINDSIGHT_API_KEY,
        timeout=10.0,
    )
    return _hindsight_client


def _ensure_hindsight_bank(client):
    global _hindsight_bank_ready

    if _hindsight_bank_ready:
        return

    try:
        client.create_bank(
            bank_id=BANK_ID,
            name="Customer Support Agent",
        )
    except Exception:
        # Bank may already exist or the API may reject duplicate creation.
        pass

    _hindsight_bank_ready = True


def get_memory(user_id, query):
    # Try Hindsight API first
    client = _get_hindsight_client()
    if client is not None:
        try:
            _ensure_hindsight_bank(client)

            # Prefix query with user_id so memories are naturally scoped.
            recall_response = client.recall(
                bank_id=BANK_ID,
                query=f"User ({user_id}) context: {query}",
            )

            results = getattr(recall_response, "results", [])
            parsed_memories = []
            for item in results:
                text = getattr(item, "text", "")
                if text:
                    parsed_memories.append({"user": text, "assistant": ""})

            if parsed_memories:
                return parsed_memories
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
    client = _get_hindsight_client()
    if client is not None:
        try:
            _ensure_hindsight_bank(client)

            content = f"User ({user_id}) asked: {user_input}\nAssistant replied: {response}"

            client.retain(
                bank_id=BANK_ID,
                content=content,
                metadata={"user_id": user_id},
            )
        except Exception as e:
            print("Hindsight retain error:", e)
