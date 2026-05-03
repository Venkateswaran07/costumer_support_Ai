import requests
import certifi
import os
import vertexai
from vertexai.generative_models import GenerativeModel
from config import GROQ_API_KEY, MODEL_NAME

# Fix broken PostgreSQL TLS cert path that can hijack requests on some systems
os.environ.pop("REQUESTS_CA_BUNDLE", None)
os.environ.pop("SSL_CERT_FILE", None)

try:
    # Initialize Vertex AI. This uses Google Cloud Default Credentials.
    # When deployed to Cloud Run, it automatically picks up the service account.
    vertexai.init()
    vertex_model = GenerativeModel("gemini-1.5-flash")
    VERTEX_AVAILABLE = True
except Exception as e:
    print(f"Vertex AI initialization failed: {e}. Falling back to Groq.")
    VERTEX_AVAILABLE = False


def generate_response(user_input, memory):
    history_text = ""

    if memory:
        history_text += "Previous interactions:\n"
        for convo in memory:
            history_text += f"- User: {convo['user']}\n"
            history_text += f"  Assistant: {convo['assistant']}\n"

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

    try:
        if VERTEX_AVAILABLE:
            # Use Google Cloud Vertex AI
            response = vertex_model.generate_content(prompt)
            return response.text
        else:
            # Fallback to Groq API if Vertex is unavailable (e.g. running locally without gcloud auth)
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}]
            }
            response = requests.post(url, headers=headers, json=data, verify=certifi.where())
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

    except Exception as e:
        print("LLM Error:", e)
        return "Sorry, something went wrong while connecting to the AI. Please try again."
