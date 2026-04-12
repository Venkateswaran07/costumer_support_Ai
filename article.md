# I built a support agent with Hindsight that stops repeating itself

Most support bots fail in the same way. They forget.

You ask a question, you get an answer. You come back with the same issue, and the system gives you the exact same response again. It doesn’t matter that the previous solution didn’t work. The system has no memory of it.

I wanted to fix that.

![BingoAI Dashboard](./dashboard.png)

---

## What the system does

I built a customer support agent that remembers past interactions and adjusts its responses based on what has already been tried.

At a high level, the system has three parts:

- A simple frontend for user interaction  
- A FastAPI backend that orchestrates logic  
- A memory layer powered by semantic retrieval  

The core loop is straightforward:

1. User sends a message  
2. System retrieves relevant past interactions  
3. LLM generates a response using both the query and memory  
4. Interaction is stored for future use  

The difference from most chatbot systems is in step two.

Instead of passing raw chat history, I retrieve only the most relevant past interactions. That decision ended up shaping the entire behavior of the system.

---

## Why memory was the real problem

At first, I tried the usual approach. Store conversation history and pass it into the model.

It didn’t work well.

If the history was too long, the model ignored it. If it was too short, it missed context. And if the user phrased the same issue differently, the system didn’t recognize it as the same problem.

What I needed wasn’t more history. I needed better retrieval.

I knew I needed [agent memory](https://vectorize.io/what-is-agent-memory) that could connect similar issues, not just identical text.

That’s when I came across [Hindsight agent memory](https://hindsight.vectorize.io/).

---

## Using Hindsight for memory

Instead of building a custom retrieval system, I decided to try [Hindsight](https://github.com/vectorize-io/hindsight).

The idea is simple. Store interactions as embeddings and retrieve the most relevant ones using semantic search.

In `memory.py`, I implemented two operations:

- Search for similar past interactions  
- Store new interactions after each response  

Here’s a simplified version of the retrieval logic:

```python
def get_memory(user_id, query):
    res = requests.post(f"{BASE_URL}/search", json={
        "query": query,
        "filters": {"user_id": user_id},
        "top_k": 5
    })
    return res.json()
```

This allows the system to retrieve interactions that are semantically similar, even if the wording is different.

For example:

- "My internet is slow"
- "WiFi is lagging"
- "Connection is unstable"

All of these map to similar past issues.

That was the first point where the system started behaving differently.

---

## The core design decision

The most important design choice was this:

**Do not pass full chat history. Retrieve only relevant memory.**

This changed everything.

Instead of overwhelming the model with context, I gave it only what mattered.

In `llm.py`, I build the prompt like this:

```python
history_text = ""
for convo in memory:
    history_text += f"- Issue: {convo['user']}\n"
    history_text += f"  Solution: {convo['assistant']}\n"
```

Then I include it in the prompt:

```python
prompt = f"""
You are a smart customer support assistant.

- Help the user solve the issue
- If issue repeats, suggest a different solution
- Be short and helpful

{history_text}

User: {user_input}
"""
```

Two things matter here:

1. The model sees what has already been tried
2. The prompt explicitly tells it not to repeat the same solution

That combination produces surprisingly good behavior without complex logic.

---

## Behavior in practice

Once memory and prompt design were in place, the system started showing a clear pattern.

**First interaction:**
> **User:** "My internet is slow"
> **Response:** Suggest restarting router

**Second interaction:**
> **User:** "Still slow"
> **Response:** Suggest changing DNS

**Third interaction:**
> **User:** "Same issue again today"
> **Response:** Suggest contacting ISP or upgrading plan

None of this is hardcoded.

The system infers that previous solutions didn’t work because they appear in memory.

This is where best agent memory actually matters. Without it, the system would repeat itself.

---

## Handling failure and fallback

One practical issue I ran into was reliability.

External services fail. If the memory system goes down, the entire application shouldn’t break.

So I added a fallback layer.

If Hindsight is unavailable, the system uses a simple in-memory store:

```python
local_memory = {}

def get_memory(user_id, query):
    return local_memory.get(user_id, [])[-5:]
```

This ensures the system always has at least some context.

It’s not as good as semantic search, but it keeps the system functional.

---

## What actually changed

The model didn’t change. The API didn’t change. What changed was how context was selected.

**Before:**
- Every request was independent
- Responses were repetitive

**After:**
- Requests were connected through memory
- Responses adapted over time

This is an important distinction.

The improvement came from system design, not model capability.

---

## Lessons learned

1. **Memory is about retrieval, not storage**
   Storing data is easy. Retrieving the right data at the right time is the hard part. Without retrieval, memory is useless.

2. **Less context is often better**
   Passing full chat history sounds useful, but it introduces noise. Retrieving only relevant interactions improves response quality.

3. **Prompt constraints matter**
   A simple rule like "do not repeat the same solution" has a strong impact when combined with memory.

4. **Semantic similarity is critical**
   Users don’t repeat problems the same way. Without semantic search, the system fails to connect related issues.

5. **Systems matter more than models**
   The biggest improvement came from architecture, not model changes. Designing how components interact is often more important than the model itself.

---

## Where this goes next

Right now, the system adapts based on past interactions.

The next step is to make it learn more explicitly:

- Track whether a solution worked
- Rank solutions based on outcomes
- Build long-term user profiles

That would move the system from memory-based adaptation to actual learning.

---

## Final thoughts

The biggest change was simple.

The system stopped forgetting.

Once it remembered what already happened, it stopped repeating itself.

That alone made it significantly more useful.
