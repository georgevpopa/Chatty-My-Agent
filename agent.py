import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

load_dotenv()
console = Console()

SYSTEM_PROMPT = """You are a helpful technical assistant. You can:
- Write and explain code
- Analyze logs and errors
- Answer technical questions
- Suggest solutions to problems

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


# State
use_gemini = True


def get_response(messages: list[dict]) -> str:
    global use_gemini
    if use_gemini:
        try:
            return call_gemini(messages)
        except Exception as e:
            console.print(f"[yellow]Gemini failed ({e}), falling back to Groq...[/yellow]")
            try:
                return call_groq(messages)
            except Exception as e2:
                return f"Both providers failed.\nGemini: {e}\nGroq: {e2}"
    else:
        try:
            return call_groq(messages)
        except Exception as e:
            console.print(f"[yellow]Groq failed ({e}), falling back to Gemini...[/yellow]")
            try:
                return call_gemini(messages)
            except Exception as e2:
                return f"Both providers failed.\nGroq: {e}\nGemini: {e2}"


def read_file(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading file: {e}"


def run_command(cmd: str) -> str:
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        return output.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return "Command timed out (30s limit)"
    except Exception as e:
        return f"Error: {e}"


def save_conversation(messages: list[dict], path: str = None):
    if not path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"conversation_{timestamp}.md"
    with open(path, "w", encoding="utf-8") as f:
        for msg in messages:
            role = "You" if msg["role"] == "user" else "Agent"
            f.write(f"## {role}\n\n{msg['content']}\n\n---\n\n")
    return path


def show_help():
    console.print("""
[bold]Commands:[/bold]
  /read <path>    Read a file and analyze it
  /run <cmd>      Run a command and analyze output
  /write <path>   Ask AI to generate code, then save to file
  /save [path]    Save conversation to a file
  /clear          Clear conversation history
  /model          Switch between Gemini and Groq
  /help           Show this help
  /quit           Exit
""")


def main():
    global use_gemini
    console.print("[bold green]My-Agent[/bold green] — Tech assistant (Gemini + Groq)")
    console.print("Type [bold]/help[/bold] for commands")
    console.print("---")

    messages = []

    while True:
        try:
            user_input = console.input("[bold blue]You:[/bold blue] ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue
        if user_input.lower() in ("/quit", "/exit", "quit", "exit"):
            break

        # /help
        if user_input.lower() == "/help":
            show_help()
            continue

        # /clear
        if user_input.lower() == "/clear":
            messages.clear()
            console.print("[green]Conversation cleared.[/green]")
            continue

        # /model
        if user_input.lower() == "/model":
            use_gemini = not use_gemini
            current = "Gemini" if use_gemini else "Groq"
            console.print(f"[green]Switched primary model to {current}[/green]")
            continue

        # /save
        if user_input.lower().startswith("/save"):
            parts = user_input.split(maxsplit=1)
            path = parts[1] if len(parts) > 1 else None
            saved = save_conversation(messages, path)
            console.print(f"[green]Saved to {saved}[/green]")
            continue

        # /read
        if user_input.startswith("/read "):
            path = user_input[6:].strip()
            content = read_file(path)
            console.print(f"[dim]Read {len(content)} chars from {path}[/dim]")
            messages.append({"role": "user", "content": f"Here's the content of `{path}`:\n```\n{content}\n```\nAnalyze this."})

        # /run
        elif user_input.startswith("/run "):
            cmd = user_input[5:].strip()
            output = run_command(cmd)
            console.print(f"[dim]$ {cmd}[/dim]")
            console.print(f"[dim]{output[:500]}[/dim]")
            messages.append({"role": "user", "content": f"I ran `{cmd}` and got:\n```\n{output}\n```\nAnalyze this output."})

        # /write
        elif user_input.startswith("/write "):
            path = user_input[7:].strip()
            prompt = console.input("[bold blue]What should the file contain?[/bold blue] ").strip()
            messages.append({"role": "user", "content": f"Generate the code/content for a file called `{path}`. Requirements: {prompt}\nRespond with ONLY the file content, no explanation or markdown fences."})
            with console.status("[bold green]Generating...[/bold green]"):
                response = get_response(messages)
            messages.append({"role": "assistant", "content": response})
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(response, encoding="utf-8")
            console.print(f"[green]Written to {path}[/green]")
            console.print(Markdown(f"```\n{response[:500]}\n```"))
            continue

        else:
            messages.append({"role": "user", "content": user_input})

        # Get AI response
        with console.status("[bold green]Thinking...[/bold green]"):
            response = get_response(messages)

        messages.append({"role": "assistant", "content": response})
        console.print()
        console.print(Markdown(response))
        console.print()


if __name__ == "__main__":
    main()
