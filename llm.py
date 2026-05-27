import os
from dotenv import load_dotenv
from storage import PERSONAS

load_dotenv()

MODELS = {
    "gemini": {"name": "Google Gemini 2.0 Flash", "provider": "gemini"},
    "groq": {"name": "Groq Llama 3.3 70B", "provider": "groq"},
    "cohere": {"name": "Cohere Command R+", "provider": "cohere"},
    "mistral": {"name": "Mistral Small 3.1", "provider": "mistral"},
    "openrouter": {"name": "OpenRouter (Meta Llama 3.3 70B)", "provider": "openrouter"},
    "together": {"name": "Together AI (Llama 3.3 70B)", "provider": "together"},
    "huggingface": {"name": "HuggingFace (Qwen 2.5 72B)", "provider": "huggingface"},
}


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


def call_cohere(messages: list[dict], persona: str = "default", memory: list[str] = None) -> str:
    import cohere
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    system = get_system_prompt(persona, memory)
    chat_history = []
    for msg in messages[:-1]:
        role = "USER" if msg["role"] == "user" else "CHATBOT"
        chat_history.append({"role": role, "message": msg["content"]})
    response = client.chat(
        model="command-r-plus",
        message=messages[-1]["content"],
        chat_history=chat_history,
        preamble=system,
    )
    return response.text


def call_mistral(messages: list[dict], persona: str = "default", memory: list[str] = None) -> str:
    from mistralai import Mistral
    client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
    system = get_system_prompt(persona, memory)
    mistral_messages = [{"role": "system", "content": system}]
    mistral_messages.extend(messages)
    response = client.chat.complete(
        model="mistral-small-latest",
        messages=mistral_messages,
    )
    return response.choices[0].message.content


def call_openrouter(messages: list[dict], persona: str = "default", memory: list[str] = None) -> str:
    import httpx
    system = get_system_prompt(persona, memory)
    all_messages = [{"role": "system", "content": system}] + messages
    response = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"},
        json={"model": "meta-llama/llama-3.3-70b-instruct:free", "messages": all_messages},
        timeout=30,
    )
    return response.json()["choices"][0]["message"]["content"]


def call_together(messages: list[dict], persona: str = "default", memory: list[str] = None) -> str:
    import httpx
    system = get_system_prompt(persona, memory)
    all_messages = [{"role": "system", "content": system}] + messages
    response = httpx.post(
        "https://api.together.xyz/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.getenv('TOGETHER_API_KEY')}"},
        json={"model": "meta-llama/Llama-3.3-70B-Instruct-Turbo", "messages": all_messages},
        timeout=30,
    )
    return response.json()["choices"][0]["message"]["content"]


def call_huggingface(messages: list[dict], persona: str = "default", memory: list[str] = None) -> str:
    import httpx
    system = get_system_prompt(persona, memory)
    all_messages = [{"role": "system", "content": system}] + messages
    response = httpx.post(
        "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-72B-Instruct/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"},
        json={"model": "Qwen/Qwen2.5-72B-Instruct", "messages": all_messages, "max_tokens": 2048},
        timeout=30,
    )
    return response.json()["choices"][0]["message"]["content"]


# Streaming variants for Gemini and Groq
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


def call_mistral_stream(messages: list[dict], persona: str = "default", memory: list[str] = None):
    from mistralai import Mistral
    client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
    system = get_system_prompt(persona, memory)
    mistral_messages = [{"role": "system", "content": system}]
    mistral_messages.extend(messages)
    response = client.chat.stream(
        model="mistral-small-latest",
        messages=mistral_messages,
    )
    for event in response:
        if event.data.choices[0].delta.content:
            yield event.data.choices[0].delta.content


# Dispatch
CALL_MAP = {
    "gemini": call_gemini,
    "groq": call_groq,
    "cohere": call_cohere,
    "mistral": call_mistral,
    "openrouter": call_openrouter,
    "together": call_together,
    "huggingface": call_huggingface,
}

STREAM_MAP = {
    "gemini": call_gemini_stream,
    "groq": call_groq_stream,
    "mistral": call_mistral_stream,
}


def call_model(model_key: str, messages: list[dict], persona: str = "default", memory: list[str] = None) -> str:
    fn = CALL_MAP.get(model_key)
    if fn:
        return fn(messages, persona, memory)
    raise ValueError(f"Unknown model: {model_key}")


def stream_model(model_key: str, messages: list[dict], persona: str = "default", memory: list[str] = None):
    fn = STREAM_MAP.get(model_key)
    if fn:
        yield from fn(messages, persona, memory)
    else:
        # Fallback: call non-streaming and yield whole response
        yield call_model(model_key, messages, persona, memory)
