import os
from dotenv import load_dotenv
from storage import PERSONAS

load_dotenv()


def get_system_prompt(persona: str = "default", memory: list[str] = None) -> str:
    base = PERSONAS.get(persona, PERSONAS["default"])
    if memory:
        facts = "\n".join(f"- {m}" for m in memory)
        base += f"\n\nThings you remember about the user:\n{facts}"
    return base


def call_gemini(messages: list[dict], persona: str = "default", memory: list[str] = None) -> str:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    system = get_system_prompt(persona, memory)
    model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=system)
    history = []
    for msg in messages[:-1]:
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [msg["content"]]})
    chat = model.start_chat(history=history)
    response = chat.send_message(messages[-1]["content"])
    return response.text


def call_groq(messages: list[dict], persona: str = "default", memory: list[str] = None) -> str:
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    system = get_system_prompt(persona, memory)
    groq_messages = [{"role": "system", "content": system}]
    groq_messages.extend(messages)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=groq_messages,
    )
    return response.choices[0].message.content


def call_gemini_stream(messages: list[dict], persona: str = "default", memory: list[str] = None):
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    system = get_system_prompt(persona, memory)
    model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=system)
    history = []
    for msg in messages[:-1]:
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [msg["content"]]})
    chat = model.start_chat(history=history)
    response = chat.send_message(messages[-1]["content"], stream=True)
    for chunk in response:
        if chunk.text:
            yield chunk.text


def call_groq_stream(messages: list[dict], persona: str = "default", memory: list[str] = None):
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    system = get_system_prompt(persona, memory)
    groq_messages = [{"role": "system", "content": system}]
    groq_messages.extend(messages)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=groq_messages,
        stream=True,
    )
    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
