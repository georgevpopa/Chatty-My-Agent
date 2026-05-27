import os
import sys
import json
import time
import random
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.markdown import Markdown
from rich.theme import Theme

from llm import call_gemini, call_groq, call_gemini_stream, call_groq_stream
from tools import read_file, run_command, web_search, scan_project, clipboard_copy, clipboard_paste, fetch_url, check_port, docker_status, docker_logs
from storage import (load_config, save_config, load_aliases, save_aliases, save_history, load_history,
                     load_memory, add_memory, clear_memory, load_stats, update_stats, PERSONAS)
from help_text import show_help
from plugins import list_plugins, run_plugin, create_example_plugin
from autonomous import run_autonomous

TIPS = [
    "💡 Use /context to pin files the AI should always know about.",
    "💡 Use /agent to let the AI run commands autonomously.",
    "💡 Use /snippet to save useful responses for later.",
    "💡 Use /alias to create shortcuts for commands you use often.",
    "💡 Use /multi to paste multi-line code blocks.",
    "💡 Use /fix after a failed /run to get a fix suggestion.",
    "💡 Use /chain to run a command and give AI custom instructions.",
    "💡 Use /persona to switch AI personality (senior_dev, eli5, reviewer).",
    "💡 Use /learn to teach the AI facts it remembers across sessions.",
    "💡 Use /refactor to improve code quality automatically.",
]

THEMES = {
    "dark": Theme({"info": "dim cyan", "warning": "yellow", "error": "bold red"}),
    "light": Theme({"info": "blue", "warning": "dark_orange", "error": "red"}),
    "minimal": Theme({"info": "white", "warning": "white", "error": "white"}),
}

config = load_config()
console = Console(theme=THEMES.get(config.get("theme", "dark")))

# State
use_gemini = config.get("model", "gemini") == "gemini"
streaming = config.get("streaming", True)
persona = config.get("persona", "default")
todos = []
snippets = {}
bookmarks = []
aliases = load_aliases()
memory = load_memory()
pinned_context = []
undo_stack = []  # (path, original_content)
session_start = time.time()
token_estimate = 0


def estimate_tokens(text: str) -> int:
    return len(text) // 4


def get_response(messages: list[dict]) -> str:
    global use_gemini
    if use_gemini:
        try:
            return call_gemini(messages, persona, memory)
        except Exception as e:
            console.print(f"[warning]Gemini failed ({e}), falling back to Groq...[/warning]")
            try:
                return call_groq(messages, persona, memory)
            except Exception as e2:
                return f"Both providers failed.\nGemini: {e}\nGroq: {e2}"
    else:
        try:
            return call_groq(messages, persona, memory)
        except Exception as e:
            console.print(f"[warning]Groq failed ({e}), falling back to Gemini...[/warning]")
            try:
                return call_gemini(messages, persona, memory)
            except Exception as e2:
                return f"Both providers failed.\nGroq: {e}\nGemini: {e2}"


def get_response_stream(messages: list[dict]) -> str:
    global use_gemini
    full = ""
    try:
        stream = call_gemini_stream(messages, persona, memory) if use_gemini else call_groq_stream(messages, persona, memory)
        for chunk in stream:
            print(chunk, end="", flush=True)
            full += chunk
        print()
        return full
    except Exception as e:
        console.print(f"\n[warning]Stream failed ({e}), trying fallback...[/warning]")
        try:
            stream = call_groq_stream(messages, persona, memory) if use_gemini else call_gemini_stream(messages, persona, memory)
            for chunk in stream:
                print(chunk, end="", flush=True)
                full += chunk
            print()
            return full
        except Exception as e2:
            return f"Both providers failed.\n{e}\n{e2}"


def ask_ai(messages: list[dict]) -> str:
    global token_estimate
    # Add pinned context
    if pinned_context:
        ctx = "\n\n".join([f"[Pinned context - {p}]:\n{read_file(p)}" for p in pinned_context])
        augmented = [{"role": "user", "content": f"Context files:\n{ctx}"}] + messages
    else:
        augmented = messages

    for msg in augmented:
        token_estimate += estimate_tokens(msg["content"])

    if streaming:
        console.print()
        response = get_response_stream(augmented)
        console.print()
    else:
        with console.status("[bold green]Thinking...[/bold green]"):
            response = get_response(augmented)
        console.print()
        console.print(Markdown(response))
        console.print()

    token_estimate += estimate_tokens(response)
    return response


def get_multiline_input() -> str:
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


def save_conversation(messages: list[dict], path: str = None):
    if not path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"conversation_{timestamp}.md"
    with open(path, "w", encoding="utf-8") as f:
        for msg in messages:
            role = "You" if msg["role"] == "user" else "Agent"
            f.write(f"## {role}\n\n{msg['content']}\n\n---\n\n")
    return path


def main():
    global use_gemini, streaming, todos, snippets, aliases, pinned_context, undo_stack, token_estimate, config, persona, memory, bookmarks

    console.print("[bold green]Chatty-My-Agent[/bold green] — Tech assistant (Gemini + Groq)")
    console.print("Type [bold]/help[/bold] for commands, or just ask a question")
    console.print(f"[dim]{random.choice(TIPS)}[/dim]")
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
            save_history(messages)
            update_stats(len(messages), token_estimate)
            break

        # Check aliases
        first_word = user_input.split()[0].lower()
        if first_word in aliases:
            user_input = aliases[first_word]
            console.print(f"[dim]→ {user_input}[/dim]")

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
            config["model"] = "gemini" if use_gemini else "groq"
            save_config(config)
            console.print(f"[green]Switched primary model to {current}[/green]")
            continue

        # /stream
        if user_input.lower() == "/stream":
            streaming = not streaming
            config["streaming"] = streaming
            save_config(config)
            console.print(f"[green]Streaming mode: {'ON' if streaming else 'OFF'}[/green]")
            continue

        # /timer
        if user_input.lower() == "/timer":
            console.print(f"[bold]Session duration:[/bold] {format_duration(time.time() - session_start)}")
            continue

        # /cost
        if user_input.lower() == "/cost":
            console.print(f"[bold]Estimated tokens used:[/bold] ~{token_estimate:,}")
            console.print(f"[dim](Rough estimate: ~4 chars per token)[/dim]")
            continue

        # /status
        if user_input.lower() == "/status":
            current_model = "Gemini" if use_gemini else "Groq"
            console.print(f"""
[bold]Status:[/bold]
  Model:      {current_model}
  Streaming:  {'ON' if streaming else 'OFF'}
  Theme:      {config.get('theme', 'dark')}
  Messages:   {len(messages)}
  Tokens:     ~{token_estimate:,}
  Todos:      {len(todos)} ({sum(1 for t in todos if t['done'])} done)
  Snippets:   {len(snippets)}
  Aliases:    {len(aliases)}
  Context:    {len(pinned_context)} pinned files
  Session:    {format_duration(time.time() - session_start)}
""")
            continue

        # /config
        if user_input.lower().startswith("/config"):
            parts = user_input.split(maxsplit=2)
            if len(parts) < 3:
                console.print(f"[dim]Current config: {json.dumps(config, indent=2)}[/dim]")
            else:
                key, val = parts[1], parts[2]
                if val.lower() == "true":
                    val = True
                elif val.lower() == "false":
                    val = False
                config[key] = val
                save_config(config)
                console.print(f"[green]Set {key} = {val}[/green]")
            continue

        # /theme
        if user_input.lower().startswith("/theme"):
            parts = user_input.split(maxsplit=1)
            if len(parts) < 2:
                console.print(f"[dim]Available: dark, light, minimal. Current: {config.get('theme', 'dark')}[/dim]")
            else:
                theme = parts[1].strip().lower()
                if theme in THEMES:
                    config["theme"] = theme
                    save_config(config)
                    console.print(f"[green]Theme set to '{theme}'. Restart to apply fully.[/green]")
                else:
                    console.print("[red]Available themes: dark, light, minimal[/red]")
            continue

        # /save
        if user_input.lower().startswith("/save"):
            parts = user_input.split(maxsplit=1)
            path = parts[1] if len(parts) > 1 else None
            saved = save_conversation(messages, path)
            console.print(f"[green]Saved to {saved}[/green]")
            continue

        # /export
        if user_input.lower().startswith("/export"):
            parts = user_input.split(maxsplit=1)
            fmt = parts[1].strip().lower() if len(parts) > 1 else "json"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"conversation_{timestamp}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(messages, f, indent=2)
            console.print(f"[green]Exported to {path}[/green]")
            continue

        # /load-session
        if user_input.lower() == "/load-session":
            loaded = load_history()
            if loaded:
                messages = loaded
                console.print(f"[green]Loaded {len(messages)} messages from last session.[/green]")
            else:
                console.print("[yellow]No saved session found.[/yellow]")
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

        # /undo
        if user_input.lower() == "/undo":
            if not undo_stack:
                console.print("[yellow]Nothing to undo.[/yellow]")
            else:
                path, content = undo_stack.pop()
                Path(path).write_text(content, encoding="utf-8")
                console.print(f"[green]Reverted {path}[/green]")
            continue

        # /alias
        if user_input.lower().startswith("/alias"):
            parts = user_input.split(maxsplit=2)
            if len(parts) < 3:
                console.print("[red]Usage: /alias <name> <command>[/red]")
            else:
                name, cmd = parts[1].lower(), parts[2]
                aliases[name] = cmd
                save_aliases(aliases)
                console.print(f"[green]Alias '{name}' → '{cmd}'[/green]")
            continue

        # /aliases
        if user_input.lower() == "/aliases":
            if not aliases:
                console.print("[yellow]No aliases. Create with /alias <name> <command>[/yellow]")
            else:
                for name, cmd in aliases.items():
                    console.print(f"  [bold cyan]{name}[/bold cyan] → {cmd}")
            continue

        # /context
        if user_input.lower().startswith("/context"):
            args = user_input[8:].strip()
            if not args:
                if pinned_context:
                    for p in pinned_context:
                        console.print(f"  [bold cyan]{p}[/bold cyan]")
                else:
                    console.print("[yellow]No pinned context. Use /context <path>[/yellow]")
            elif args.lower() == "clear":
                pinned_context.clear()
                console.print("[green]Cleared all pinned context.[/green]")
            else:
                if Path(args).exists():
                    pinned_context.append(args)
                    console.print(f"[green]Pinned: {args}[/green]")
                else:
                    console.print(f"[red]File not found: {args}[/red]")
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
                console.print("[yellow]No snippets saved.[/yellow]")
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
                console.print(f"[red]Snippet '{name}' not found.[/red]")
            continue

        # /todo
        if user_input.lower().startswith("/todo"):
            args = user_input[5:].strip()
            if not args:
                if not todos:
                    console.print("[yellow]No tasks yet.[/yellow]")
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
                    console.print(f"[green]✓ Done: {todos[idx]['text']}[/green]")
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
            console.print(f"[dim]{len(messages)} messages[/dim]")
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
            branch = run_command("git branch --show-current")
            log = run_command("git log --oneline -5")
            status = run_command("git status --short")
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

        # /shell
        elif user_input.startswith("/shell "):
            cmd = user_input[7:].strip()
            output = run_command(cmd)
            console.print(f"[dim]$ {cmd}[/dim]")
            console.print(output)
            last_command = cmd
            last_command_output = output
            continue

        # /chain
        elif user_input.startswith("/chain "):
            parts = user_input[7:].split("|", 1)
            cmd = parts[0].strip()
            output = run_command(cmd)
            console.print(f"[dim]$ {cmd}[/dim]")
            console.print(f"[dim]{output[:300]}[/dim]")
            follow_up = parts[1].strip() if len(parts) > 1 else "Analyze this output."
            messages.append({"role": "user", "content": f"I ran `{cmd}` and got:\n```\n{output}\n```\n{follow_up}"})

        # /fix
        elif user_input.lower() == "/fix":
            if not last_command_output:
                console.print("[yellow]No previous command to fix.[/yellow]")
                continue
            messages.append({"role": "user", "content": f"The command `{last_command}` failed with:\n```\n{last_command_output}\n```\nWhat's wrong and how do I fix it?"})

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

        # /translate
        elif user_input.lower().startswith("/translate "):
            lang = user_input[11:].strip()
            if last_response:
                messages.append({"role": "user", "content": f"Translate the following to {lang}:\n\n{last_response}"})
            else:
                console.print("[yellow]No response to translate yet.[/yellow]")
                continue

        # /summarize
        elif user_input.startswith("/summarize "):
            path = user_input[11:].strip()
            content = read_file(path)
            console.print(f"[dim]Read {len(content)} chars from {path}[/dim]")
            messages.append({"role": "user", "content": f"Give me a brief TL;DR summary of this file:\n\nFile: `{path}`\n```\n{content}\n```"})

        # /project
        elif user_input.startswith("/project "):
            path = user_input[9:].strip()
            structure = scan_project(path)
            console.print(f"[dim]{structure[:300]}...[/dim]")
            messages.append({"role": "user", "content": f"Here's a project structure:\n```\n{structure}\n```\nGive me an overview: what is this project, what tech stack, how is it organized?"})

        # /explain
        elif user_input.startswith("/explain "):
            path = user_input[9:].strip()
            content = read_file(path)
            console.print(f"[dim]Read {len(content)} chars[/dim]")
            messages.append({"role": "user", "content": f"Explain this file in plain English:\n\nFile: `{path}`\n```\n{content}\n```"})

        # /refactor
        elif user_input.startswith("/refactor "):
            path = user_input[10:].strip()
            content = read_file(path)
            if content.startswith("Error"):
                console.print(f"[red]{content}[/red]")
                continue
            undo_stack.append((path, content))
            messages.append({"role": "user", "content": f"Refactor and improve this file. Fix code smells, improve naming, add comments, optimize. Keep same functionality.\n\nFile: `{path}`\n```\n{content}\n```\nRespond with ONLY the improved file content, no explanation or markdown fences."})
            with console.status("[bold green]Refactoring...[/bold green]"):
                response = get_response(messages)
            messages.append({"role": "assistant", "content": response})
            last_response = response
            token_estimate += estimate_tokens(content) + estimate_tokens(response)
            Path(path).write_text(response, encoding="utf-8")
            console.print(f"[green]Refactored {path} (use /undo to revert)[/green]")
            console.print(Markdown(f"```\n{response[:500]}\n```"))
            continue

        # /test
        elif user_input.startswith("/test "):
            path = user_input[6:].strip()
            content = read_file(path)
            if content.startswith("Error"):
                console.print(f"[red]{content}[/red]")
                continue
            test_path = Path(path).stem + "_test.py"
            messages.append({"role": "user", "content": f"Generate pytest unit tests for:\n\nFile: `{path}`\n```\n{content}\n```\nRespond with ONLY the test file content, no explanation or markdown fences."})
            with console.status("[bold green]Generating tests...[/bold green]"):
                response = get_response(messages)
            messages.append({"role": "assistant", "content": response})
            last_response = response
            token_estimate += estimate_tokens(content) + estimate_tokens(response)
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
            messages.append({"role": "user", "content": f"Compare:\n\n**{parts[0]}:**\n```\n{f1}\n```\n\n**{parts[1]}:**\n```\n{f2}\n```\nHighlight differences."})

        # /read
        elif user_input.startswith("/read "):
            path = user_input[6:].strip()
            content = read_file(path)
            console.print(f"[dim]Read {len(content)} chars from {path}[/dim]")
            messages.append({"role": "user", "content": f"Here's `{path}`:\n```\n{content}\n```\nAnalyze this."})

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
            if Path(path).exists():
                undo_stack.append((path, read_file(path)))
            messages.append({"role": "user", "content": f"Generate code/content for `{path}`. Requirements: {prompt}\nRespond with ONLY the file content, no explanation or markdown fences."})
            with console.status("[bold green]Generating...[/bold green]"):
                response = get_response(messages)
            messages.append({"role": "assistant", "content": response})
            last_response = response
            token_estimate += estimate_tokens(response)
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
            undo_stack.append((path, existing))
            prompt = console.input("[bold blue]What to add?[/bold blue] ").strip()
            messages.append({"role": "user", "content": f"`{path}` contains:\n```\n{existing}\n```\nAppend: {prompt}\nRespond with ONLY the new content to append, no markdown fences."})
            with console.status("[bold green]Generating...[/bold green]"):
                response = get_response(messages)
            messages.append({"role": "assistant", "content": response})
            last_response = response
            token_estimate += estimate_tokens(response)
            with open(path, "a", encoding="utf-8") as f:
                f.write("\n" + response)
            console.print(f"[green]Appended to {path}[/green]")
            console.print(Markdown(f"```\n{response[:500]}\n```"))
            continue

        # /retry
        elif user_input.lower() == "/retry":
            if messages and messages[-1]["role"] == "assistant":
                messages.pop()  # remove last response
                # re-run with same user message
            else:
                console.print("[yellow]Nothing to retry.[/yellow]")
                continue

        # /bookmark
        elif user_input.lower() == "/bookmark":
            if last_response:
                bookmarks.append({"time": datetime.now().strftime("%H:%M"), "content": last_response[:200]})
                console.print(f"[green]Bookmarked (#{len(bookmarks)})[/green]")
            else:
                console.print("[yellow]No response to bookmark.[/yellow]")
            continue

        # /bookmarks
        elif user_input.lower() == "/bookmarks":
            if not bookmarks:
                console.print("[yellow]No bookmarks yet.[/yellow]")
            else:
                for i, b in enumerate(bookmarks, 1):
                    console.print(f"  [bold cyan]#{i}[/bold cyan] [{b['time']}] {b['content'][:80]}...")
            continue

        # /persona
        elif user_input.lower().startswith("/persona"):
            args = user_input[8:].strip()
            if not args:
                console.print(f"[bold]Current:[/bold] {persona}")
                console.print(f"[dim]Available: {', '.join(PERSONAS.keys())}[/dim]")
            elif args in PERSONAS:
                persona = args
                config["persona"] = persona
                save_config(config)
                console.print(f"[green]Persona set to '{persona}'[/green]")
            else:
                console.print(f"[red]Unknown persona. Available: {', '.join(PERSONAS.keys())}[/red]")
            continue

        # /learn
        elif user_input.startswith("/learn "):
            fact = user_input[7:].strip()
            add_memory(fact)
            memory.append(fact)
            console.print(f"[green]Remembered: {fact}[/green]")
            continue

        # /memory
        elif user_input.lower() == "/memory":
            if not memory:
                console.print("[yellow]No memories. Use /learn <fact>[/yellow]")
            else:
                for i, m in enumerate(memory, 1):
                    console.print(f"  {i}. {m}")
            continue

        # /forget
        elif user_input.lower() == "/forget":
            clear_memory()
            memory.clear()
            console.print("[green]All memories cleared.[/green]")
            continue

        # /http
        elif user_input.startswith("/http "):
            url = user_input[6:].strip()
            console.print(f"[dim]Fetching: {url}[/dim]")
            content = fetch_url(url)
            console.print(f"[dim]Got {len(content)} chars[/dim]")
            messages.append({"role": "user", "content": f"I fetched {url} and got:\n```\n{content}\n```\nAnalyze this content."})

        # /port
        elif user_input.startswith("/port "):
            port = user_input[6:].strip()
            try:
                result = check_port(int(port))
                console.print(result)
            except ValueError:
                console.print("[red]Usage: /port <number>[/red]")
            continue

        # /docker
        elif user_input.lower() == "/docker":
            result = docker_status()
            console.print(result)
            continue

        # /docker-logs
        elif user_input.startswith("/docker-logs "):
            container = user_input[13:].strip()
            logs = docker_logs(container)
            console.print(f"[dim]{logs[:500]}[/dim]")
            messages.append({"role": "user", "content": f"Docker logs for '{container}':\n```\n{logs}\n```\nAnalyze these logs."})

        # /env
        elif user_input.lower() == "/env":
            safe_env = {k: ("***" if any(s in k.lower() for s in ["key", "secret", "token", "pass"]) else v)
                       for k, v in os.environ.items()}
            env_str = "\n".join(f"  {k}={v}" for k, v in sorted(safe_env.items())[:30])
            console.print(f"[dim]Environment (secrets masked):\n{env_str}[/dim]")
            continue

        # /stats
        elif user_input.lower() == "/stats":
            stats = load_stats()
            console.print(f"""
[bold]Lifetime Stats:[/bold]
  Sessions:    {stats.get('sessions', 0)}
  Messages:    {stats.get('messages', 0):,}
  Tokens:      ~{stats.get('tokens', 0):,}
  First use:   {stats.get('first_use', 'N/A')}
  Last use:    {stats.get('last_use', 'N/A')}
""")
            continue

        # /voice
        elif user_input.lower() == "/voice":
            try:
                from voice import speech_to_text
                text = speech_to_text()
                console.print(f"[dim]You said: {text}[/dim]")
                messages.append({"role": "user", "content": text})
            except ImportError:
                console.print("[red]Voice requires: pip install sounddevice numpy[/red]")
                continue
            except Exception as e:
                console.print(f"[red]Voice error: {e}[/red]")
                continue

        # /speak
        elif user_input.lower() == "/speak":
            if last_response:
                try:
                    from voice import text_to_speech
                    text_to_speech(last_response)
                except Exception as e:
                    console.print(f"[red]TTS error: {e}[/red]")
            else:
                console.print("[yellow]No response to speak.[/yellow]")
            continue

        # /agent
        elif user_input.startswith("/agent "):
            goal = user_input[7:].strip()
            console.print(f"[bold green]🤖 Autonomous mode: {goal}[/bold green]")
            result = run_autonomous(goal, get_response, console)
            last_response = result
            messages.append({"role": "user", "content": f"[Autonomous task: {goal}]"})
            messages.append({"role": "assistant", "content": result})
            continue

        # /plugins
        elif user_input.lower() == "/plugins":
            plugins = list_plugins()
            if not plugins:
                console.print("[yellow]No plugins. Dir: ~/.chatty-agent/plugins/[/yellow]")
                console.print("[dim]Use /plugin-init to create an example.[/dim]")
            else:
                for p in plugins:
                    console.print(f"  [bold cyan]{p['name']}[/bold cyan] — {p['description']}")
            continue

        # /plugin-init
        elif user_input.lower() == "/plugin-init":
            path = create_example_plugin()
            if path:
                console.print(f"[green]Created example plugin: {path}[/green]")
            else:
                console.print("[dim]Example plugin already exists.[/dim]")
            continue

        # /plugin <name> <args>
        elif user_input.startswith("/plugin "):
            parts = user_input[8:].split(maxsplit=1)
            name = parts[0]
            args = parts[1] if len(parts) > 1 else ""
            result = run_plugin(name, args, messages, get_response)
            console.print(result)
            last_response = result
            continue

        else:
            messages.append({"role": "user", "content": user_input})

        # Get AI response
        response = ask_ai(messages)
        messages.append({"role": "assistant", "content": response})
        last_response = response


if __name__ == "__main__":
    main()
