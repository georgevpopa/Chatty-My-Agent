import os
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are a helpful technical assistant. You can:
- Write and explain code
- Analyze logs and errors
- Answer technical questions
- Suggest solutions to problems
- Search the web for current information

Be concise and direct. Use code blocks for code."""


def call_gemini(messages: list[dict]) -> str:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")
    history = []
    for msg in messages[:-1]:
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [msg["content"]]})
    chat = model.start_chat(history=history)
    response = chat.send_message(messages[-1]["content"])
    return response.text


def call_groq(messages: list[dict]) -> str:
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    groq_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    groq_messages.extend(messages)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=groq_messages,
    )
    return response.choices[0].message.content


def call_gemini_stream(messages: list[dict]):
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")
    history = []
    for msg in messages[:-1]:
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [msg["content"]]})
    chat = model.start_chat(history=history)
    response = chat.send_message(messages[-1]["content"], stream=True)
    for chunk in response:
        if chunk.text:
            yield chunk.text


def call_groq_stream(messages: list[dict]):
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    groq_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    groq_messages.extend(messages)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=groq_messages,
        stream=True,
    )
    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
