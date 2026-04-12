import requests
import certifi
import os
from config import GROQ_API_KEY, MODEL_NAME

# Fix broken PostgreSQL TLS cert path that can hijack requests on some systems
os.environ.pop("REQUESTS_CA_BUNDLE", None)
os.environ.pop("SSL_CERT_FILE", None)


def generate_response(user_input, memory):
    history_text = ""

    if memory:
        history_text += "Previous issues and solutions:\n"
        for convo in memory:
            history_text += f"- Issue: {convo['user']}\n"
            history_text += f"  Solution: {convo['assistant']}\n"

    prompt = f"""
You are a smart customer support assistant.

- Help the user solve the issue
- If issue repeats, suggest a different solution
- Be short and helpful

{history_text}

User issue:
{user_input}
"""

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        # Use certifi's CA bundle to avoid broken system cert paths
        response = requests.post(url, headers=headers, json=data, verify=certifi.where())

        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text[:300])

        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]["content"]

    except Exception as e:
        print("LLM Error:", e)
        return "Sorry, something went wrong. Please try again."