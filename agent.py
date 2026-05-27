import os
import sys
import json
import subprocess
import time
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
- Search the web for current information

Be concise and direct. Use code blocks for code."""

# State
use_gemini = True
streaming = True
todos = []
snippets = {}
session_start = time.time()


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


def get_response_stream(messages: list[dict]) -> str:
    global use_gemini
    full = ""
    try:
        stream = call_gemini_stream(messages) if use_gemini else call_groq_stream(messages)
        for chunk in stream:
            print(chunk, end="", flush=True)
            full += chunk
        print()
        return full
    except Exception as e:
        console.print(f"\n[yellow]Stream failed ({e}), trying fallback...[/yellow]")
        try:
            stream = call_groq_stream(messages) if use_gemini else call_gemini_stream(messages)
            for chunk in stream:
                print(chunk, end="", flush=True)
                full += chunk
            print()
            return full
        except Exception as e2:
            return f"Both providers failed.\n{e}\n{e2}"


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


def web_search(query: str) -> str:
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        if not results:
            return "No results found."
        output = ""
        for r in results:
            output += f"**{r['title']}**\n{r['href']}\n{r['body']}\n\n"
        return output.strip()
    except Exception as e:
        return f"Search error: {e}"


def scan_project(path: str) -> str:
    p = Path(path)
    if not p.is_dir():
        return f"Error: {path} is not a directory"
    ignore = {".git", "__pycache__", "node_modules", ".venv", "venv", ".env", "dist", "build"}
    lines = []
    file_count = 0
    for item in sorted(p.rglob("*")):
        if any(part in ignore for part in item.parts):
            continue
        if item.is_file():
            rel = item.relative_to(p)
            size = item.stat().st_size
            lines.append(f"  {rel} ({size} bytes)")
            file_count += 1
            if file_count > 50:
                lines.append("  ... (truncated, too many files)")
                break
    return f"Project: {path}\nFiles ({file_count}):\n" + "\n".join(lines)


def clipboard_copy(text: str):
    try:
        subprocess.run("clip", input=text.encode("utf-8"), check=True)
        return True
    except Exception:
        return False


def clipboard_paste() -> str:
    try:
        result = subprocess.run(
            ["powershell", "-command", "Get-Clipboard"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip()
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


def get_multiline_input() -> str:
    """Read multiple lines until user types END on its own line."""
    console.print("[dim]Enter text (type END on a new line to finish):[/dim]")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines)


def format_duration(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m}m"
    elif m:
        return f"{m}m {s}s"
    return f"{s}s"


def show_help():
    console.print("""
[bold green]━━━ Chatty-My-Agent Help ━━━[/bold green]

[bold]COMMANDS:[/bold]

  [bold cyan]/read <path>[/bold cyan]          Read a file and get AI analysis
  [bold cyan]/run <cmd>[/bold cyan]            Run a shell command and analyze output
  [bold cyan]/shell <cmd>[/bold cyan]          Run command silently (no AI analysis)
  [bold cyan]/write <path>[/bold cyan]         Generate code/content and save to file
  [bold cyan]/append <path>[/bold cyan]        Append AI-generated content to existing file
  [bold cyan]/refactor <path>[/bold cyan]      AI rewrites a file with improvements
  [bold cyan]/test <path>[/bold cyan]          Generate unit tests for a file
  [bold cyan]/search <query>[/bold cyan]       Search the web (DuckDuckGo, free)
  [bold cyan]/explain <path>[/bold cyan]       Explain a file in plain English
  [bold cyan]/project <path>[/bold cyan]       Analyze an entire project folder
  [bold cyan]/fix[/bold cyan]                  Auto-fix the last error from /run
  [bold cyan]/git[/bold cyan]                  Quick git status + recent commits
  [bold cyan]/paste[/bold cyan]                Analyze clipboard contents
  [bold cyan]/copy[/bold cyan]                 Copy last AI response to clipboard
  [bold cyan]/multi[/bold cyan]                Enter multi-line input mode
  [bold cyan]/diff <f1> <f2>[/bold cyan]       Compare two files
  [bold cyan]/snippet <name>[/bold cyan]       Save last response as a named snippet
  [bold cyan]/snippets[/bold cyan]             List all saved snippets
  [bold cyan]/load <name>[/bold cyan]          Load and display a snippet
  [bold cyan]/todo [text][/bold cyan]          Add a task, or list all tasks
  [bold cyan]/todo done <n>[/bold cyan]        Mark task #n as done
  [bold cyan]/history[/bold cyan]              Show conversation summary
  [bold cyan]/stream[/bold cyan]               Toggle streaming mode (word by word)
  [bold cyan]/timer[/bold cyan]                Show session duration
  [bold cyan]/status[/bold cyan]               Show current settings and stats
  [bold cyan]/save [path][/bold cyan]          Save conversation to markdown
  [bold cyan]/clear[/bold cyan]                Clear conversation history
  [bold cyan]/model[/bold cyan]                Switch between Gemini and Groq
  [bold cyan]/help[/bold cyan]                 Show this help
  [bold cyan]/quit[/bold cyan]                 Exit

[bold]EXAMPLES:[/bold]

  [dim]# Ask any tech question[/dim]
  You: what is a REST API?
  You: write a Python function to sort a list of dicts by key

  [dim]# Read and analyze a log file[/dim]
  You: /read C:\\logs\\app.log

  [dim]# Run a command and get AI explanation[/dim]
  You: /run ipconfig /all
  You: /run git status
  You: /run python -m pytest tests/

  [dim]# Run a command silently (just execute, no AI)[/dim]
  You: /shell mkdir new_folder
  You: /shell pip install requests

  [dim]# Fix the last failed command[/dim]
  You: /run python app.py
  You: /fix

  [dim]# Generate a new file[/dim]
  You: /write utils.py
  → What should the file contain? a function to parse CSV files

  [dim]# Add to an existing file[/dim]
  You: /append utils.py
  → What to add? a function to validate email addresses

  [dim]# Refactor a file (AI improves it)[/dim]
  You: /refactor C:\\dev\\project\\messy_code.py

  [dim]# Generate tests for a file[/dim]
  You: /test C:\\dev\\project\\utils.py

  [dim]# Search the web[/dim]
  You: /search python asyncio best practices 2026

  [dim]# Explain code in plain English[/dim]
  You: /explain C:\\dev\\project\\main.py

  [dim]# Analyze a whole project[/dim]
  You: /project C:\\dev\\my-app

  [dim]# Quick git overview[/dim]
  You: /git

  [dim]# Compare files[/dim]
  You: /diff config_old.yaml config_new.yaml

  [dim]# Multi-line input (paste code blocks)[/dim]
  You: /multi
  → (type or paste multiple lines, then type END)

  [dim]# Save and reuse code snippets[/dim]
  You: how do I connect to PostgreSQL in Python?
  You: /snippet postgres_connect
  You: /snippets
  You: /load postgres_connect

  [dim]# Track tasks[/dim]
  You: /todo fix the login bug
  You: /todo done 1

  [dim]# Clipboard workflow[/dim]
  You: /paste          (analyzes what you copied)
  You: /copy           (copies AI answer to clipboard)

  [dim]# Session info[/dim]
  You: /stream         (toggle streaming)
  You: /timer          (how long you've been here)
  You: /status         (full dashboard)
  You: /model          (switch Gemini ↔ Groq)

  [dim]# Conversation management[/dim]
  You: /save
  You: /clear
  You: /history
""")


def main():
    global use_gemini, streaming, todos, snippets
    console.print("[bold green]Chatty-My-Agent[/bold green] — Tech assistant (Gemini + Groq)")
    console.print("Type [bold]/help[/bold] for commands, or just ask a question")
    console.print("---")

    messages = []
    last_response = ""
    last_command = ""
    last_command_output = ""

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

        # /stream
        if user_input.lower() == "/stream":
            streaming = not streaming
            state = "ON" if streaming else "OFF"
            console.print(f"[green]Streaming mode: {state}[/green]")
            continue

        # /timer
        if user_input.lower() == "/timer":
            elapsed = time.time() - session_start
            console.print(f"[bold]Session duration:[/bold] {format_duration(elapsed)}")
            continue

        # /status
        if user_input.lower() == "/status":
            current_model = "Gemini" if use_gemini else "Groq"
            stream_state = "ON" if streaming else "OFF"
            elapsed = format_duration(time.time() - session_start)
            console.print(f"""
[bold]Status:[/bold]
  Model:      {current_model} (primary)
  Streaming:  {stream_state}
  Messages:   {len(messages)}
  Todos:      {len(todos)} ({sum(1 for t in todos if t['done'])} done)
  Snippets:   {len(snippets)}
  Session:    {elapsed}
""")
            continue

        # /save
        if user_input.lower().startswith("/save"):
            parts = user_input.split(maxsplit=1)
            path = parts[1] if len(parts) > 1 else None
            saved = save_conversation(messages, path)
            console.print(f"[green]Saved to {saved}[/green]")
            continue

        # /copy
        if user_input.lower() == "/copy":
            if last_response:
                if clipboard_copy(last_response):
                    console.print("[green]Copied last response to clipboard.[/green]")
                else:
                    console.print("[red]Failed to copy.[/red]")
            else:
                console.print("[yellow]No response to copy yet.[/yellow]")
            continue

        # /snippet
        if user_input.lower().startswith("/snippet "):
            name = user_input[9:].strip()
            if last_response:
                snippets[name] = last_response
                console.print(f"[green]Saved snippet '{name}'[/green]")
            else:
                console.print("[yellow]No response to save yet.[/yellow]")
            continue

        # /snippets
        if user_input.lower() == "/snippets":
            if not snippets:
                console.print("[yellow]No snippets saved. Use /snippet <name> after a response.[/yellow]")
            else:
                for name in snippets:
                    preview = snippets[name][:60].replace("\n", " ")
                    console.print(f"  [bold cyan]{name}[/bold cyan] — {preview}...")
            continue

        # /load
        if user_input.lower().startswith("/load "):
            name = user_input[6:].strip()
            if name in snippets:
                console.print()
                console.print(Markdown(snippets[name]))
                console.print()
            else:
                console.print(f"[red]Snippet '{name}' not found. Use /snippets to list.[/red]")
            continue

        # /todo
        if user_input.lower().startswith("/todo"):
            args = user_input[5:].strip()
            if not args:
                if not todos:
                    console.print("[yellow]No tasks yet. Add one with /todo <text>[/yellow]")
                else:
                    for i, t in enumerate(todos, 1):
                        status = "✓" if t["done"] else "○"
                        style = "strike dim" if t["done"] else ""
                        console.print(f"  [{style}]{status} {i}. {t['text']}[/{style}]")
                continue
            if args.startswith("done "):
                try:
                    idx = int(args[5:]) - 1
                    todos[idx]["done"] = True
                    console.print(f"[green]✓ Marked done: {todos[idx]['text']}[/green]")
                except (ValueError, IndexError):
                    console.print("[red]Invalid task number.[/red]")
                continue
            todos.append({"text": args, "done": False})
            console.print(f"[green]Added task #{len(todos)}: {args}[/green]")
            continue

        # /history
        if user_input.lower() == "/history":
            if not messages:
                console.print("[yellow]No conversation yet.[/yellow]")
                continue
            console.print(f"[dim]{len(messages)} messages in history[/dim]")
            messages.append({"role": "user", "content": "Summarize our conversation so far in bullet points. Be brief."})
            with console.status("[bold green]Summarizing...[/bold green]"):
                response = get_response(messages)
            messages.pop()
            console.print()
            console.print(Markdown(response))
            console.print()
            continue

        # /git
        if user_input.lower() == "/git":
            status = run_command("git status --short")
            log = run_command("git log --oneline -5")
            branch = run_command("git branch --show-current")
            console.print(f"[bold]Branch:[/bold] {branch}")
            console.print(f"[bold]Recent commits:[/bold]\n{log}")
            console.print(f"[bold]Changes:[/bold]\n{status or '(clean)'}")
            continue

        # /multi
        if user_input.lower() == "/multi":
            content = get_multiline_input()
            if content:
                messages.append({"role": "user", "content": content})
            else:
                console.print("[yellow]Empty input.[/yellow]")
                continue

        # /shell (run without AI analysis)
        elif user_input.startswith("/shell "):
            cmd = user_input[7:].strip()
            output = run_command(cmd)
            console.print(f"[dim]$ {cmd}[/dim]")
            console.print(output)
            last_command = cmd
            last_command_output = output
            continue

        # /fix
        elif user_input.lower() == "/fix":
            if not last_command_output:
                console.print("[yellow]No previous command to fix. Run /run first.[/yellow]")
                continue
            messages.append({"role": "user", "content": f"The command `{last_command}` failed with:\n```\n{last_command_output}\n```\nWhat's wrong and how do I fix it? Give me the corrected command or code."})

        # /paste
        elif user_input.lower() == "/paste":
            content = clipboard_paste()
            if content:
                console.print(f"[dim]Clipboard: {content[:100]}...[/dim]")
                messages.append({"role": "user", "content": f"Analyze this from my clipboard:\n```\n{content}\n```"})
            else:
                console.print("[yellow]Clipboard is empty.[/yellow]")
                continue

        # /search
        elif user_input.startswith("/search "):
            query = user_input[8:].strip()
            console.print(f"[dim]Searching: {query}[/dim]")
            with console.status("[bold green]Searching...[/bold green]"):
                results = web_search(query)
            console.print(Markdown(results))
            messages.append({"role": "user", "content": f"I searched for '{query}' and got:\n{results}\nSummarize the key findings."})

        # /project
        elif user_input.startswith("/project "):
            path = user_input[9:].strip()
            console.print(f"[dim]Scanning project: {path}[/dim]")
            structure = scan_project(path)
            console.print(f"[dim]{structure[:300]}...[/dim]")
            messages.append({"role": "user", "content": f"Here's a project structure:\n```\n{structure}\n```\nGive me an overview: what is this project, what tech stack does it use, and how is it organized?"})

        # /explain
        elif user_input.startswith("/explain "):
            path = user_input[9:].strip()
            content = read_file(path)
            console.print(f"[dim]Read {len(content)} chars from {path}[/dim]")
            messages.append({"role": "user", "content": f"Explain this file in plain English. What does it do, how is it structured, and what are the key parts?\n\nFile: `{path}`\n```\n{content}\n```"})

        # /refactor
        elif user_input.startswith("/refactor "):
            path = user_input[10:].strip()
            content = read_file(path)
            if content.startswith("Error"):
                console.print(f"[red]{content}[/red]")
                continue
            console.print(f"[dim]Read {len(content)} chars from {path}[/dim]")
            messages.append({"role": "user", "content": f"Refactor and improve this file. Fix code smells, improve naming, add comments, optimize where possible. Keep the same functionality.\n\nFile: `{path}`\n```\n{content}\n```\nRespond with ONLY the improved file content, no explanation or markdown fences."})
            with console.status("[bold green]Refactoring...[/bold green]"):
                response = get_response(messages)
            messages.append({"role": "assistant", "content": response})
            last_response = response
            # Save backup
            backup = path + ".bak"
            Path(backup).write_text(content, encoding="utf-8")
            Path(path).write_text(response, encoding="utf-8")
            console.print(f"[green]Refactored {path} (backup: {backup})[/green]")
            console.print(Markdown(f"```\n{response[:500]}\n```"))
            continue

        # /test
        elif user_input.startswith("/test "):
            path = user_input[6:].strip()
            content = read_file(path)
            if content.startswith("Error"):
                console.print(f"[red]{content}[/red]")
                continue
            console.print(f"[dim]Read {len(content)} chars from {path}[/dim]")
            test_path = Path(path).stem + "_test.py"
            messages.append({"role": "user", "content": f"Generate unit tests (using pytest) for this file:\n\nFile: `{path}`\n```\n{content}\n```\nRespond with ONLY the test file content, no explanation or markdown fences."})
            with console.status("[bold green]Generating tests...[/bold green]"):
                response = get_response(messages)
            messages.append({"role": "assistant", "content": response})
            last_response = response
            Path(test_path).write_text(response, encoding="utf-8")
            console.print(f"[green]Tests written to {test_path}[/green]")
            console.print(Markdown(f"```\n{response[:500]}\n```"))
            continue

        # /diff
        elif user_input.startswith("/diff "):
            parts = user_input[6:].strip().split()
            if len(parts) < 2:
                console.print("[red]Usage: /diff <file1> <file2>[/red]")
                continue
            f1, f2 = read_file(parts[0]), read_file(parts[1])
            messages.append({"role": "user", "content": f"Compare these two files:\n\n**{parts[0]}:**\n```\n{f1}\n```\n\n**{parts[1]}:**\n```\n{f2}\n```\nHighlight the differences and explain them."})

        # /read
        elif user_input.startswith("/read "):
            path = user_input[6:].strip()
            content = read_file(path)
            console.print(f"[dim]Read {len(content)} chars from {path}[/dim]")
            messages.append({"role": "user", "content": f"Here's the content of `{path}`:\n```\n{content}\n```\nAnalyze this."})

        # /run
        elif user_input.startswith("/run "):
            cmd = user_input[5:].strip()
            output = run_command(cmd)
            last_command = cmd
            last_command_output = output
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
            last_response = response
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(response, encoding="utf-8")
            console.print(f"[green]Written to {path}[/green]")
            console.print(Markdown(f"```\n{response[:500]}\n```"))
            continue

        # /append
        elif user_input.startswith("/append "):
            path = user_input[8:].strip()
            if not Path(path).exists():
                console.print(f"[red]File not found: {path}[/red]")
                continue
            existing = read_file(path)
            prompt = console.input("[bold blue]What to add?[/bold blue] ").strip()
            messages.append({"role": "user", "content": f"The file `{path}` currently contains:\n```\n{existing}\n```\nAppend the following to it: {prompt}\nRespond with ONLY the new content to append (not the whole file), no markdown fences."})
            with console.status("[bold green]Generating...[/bold green]"):
                response = get_response(messages)
            messages.append({"role": "assistant", "content": response})
            last_response = response
            with open(path, "a", encoding="utf-8") as f:
                f.write("\n" + response)
            console.print(f"[green]Appended to {path}[/green]")
            console.print(Markdown(f"```\n{response[:500]}\n```"))
            continue

        else:
            messages.append({"role": "user", "content": user_input})

        # Get AI response
        if streaming:
            console.print()
            response = get_response_stream(messages)
            console.print()
        else:
            with console.status("[bold green]Thinking...[/bold green]"):
                response = get_response(messages)
            console.print()
            console.print(Markdown(response))
            console.print()

        messages.append({"role": "assistant", "content": response})
        last_response = response


if __name__ == "__main__":
    main()
