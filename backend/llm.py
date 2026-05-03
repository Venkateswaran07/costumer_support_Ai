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
You are an interactive Election Process Assistant. Your goal is to help users understand voting timelines, registration steps, and election procedures in an easy-to-follow, step-by-step manner.

- Be encouraging and informative.
- Use bullet points for steps.
- Use Markdown tables for timelines and key dates to make them easy to follow.
- Highlight important deadlines.
- If the user asks about a specific location, provide general guidance on how they can find their local election office details.
- Stay neutral and focus on the 'how-to' of voting.
- Be short and helpful.

{history_text}

User query:
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
