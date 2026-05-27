"""Autonomous agent mode for Chatty-My-Agent.

The AI decides what commands to run to accomplish a goal.
It can read files, run commands, search the web, and write files.
"""
import json
from tools import read_file, run_command, web_search
from pathlib import Path

AGENT_SYSTEM = """You are an autonomous AI agent. Given a goal, you decide what actions to take.

Available actions (respond with JSON):
{"action": "read", "path": "file_path"}
{"action": "run", "cmd": "shell_command"}
{"action": "search", "query": "search_query"}
{"action": "write", "path": "file_path", "content": "file_content"}
{"action": "think", "thought": "your reasoning"}
{"action": "done", "result": "final answer or summary"}

Rules:
- Take ONE action at a time
- After each action, you'll see the result and decide the next step
- Use "think" to reason about what to do next
- Use "done" when the goal is achieved
- Maximum 10 steps

Respond with ONLY valid JSON, no other text."""


def run_autonomous(goal: str, get_response, console, max_steps=10):
    """Run the agent autonomously to achieve a goal."""
    history = [
        {"role": "user", "content": f"{AGENT_SYSTEM}\n\nGoal: {goal}"}
    ]

    for step in range(max_steps):
        console.print(f"[dim]Step {step + 1}/{max_steps}...[/dim]")

        response = get_response(history)
        history.append({"role": "assistant", "content": response})

        # Parse action
        try:
            # Try to extract JSON from response
            text = response.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            action = json.loads(text)
        except json.JSONDecodeError:
            console.print(f"[yellow]Agent returned non-JSON, treating as done.[/yellow]")
            return response

        act = action.get("action", "done")

        if act == "done":
            result = action.get("result", "Task complete.")
            console.print(f"[green]✓ Done:[/green] {result}")
            return result

        elif act == "think":
            thought = action.get("thought", "")
            console.print(f"[dim]💭 {thought}[/dim]")
            history.append({"role": "user", "content": f"Thought noted. Continue with next action."})

        elif act == "read":
            path = action.get("path", "")
            content = read_file(path)
            console.print(f"[dim]📖 Reading {path}[/dim]")
            history.append({"role": "user", "content": f"File content of {path}:\n```\n{content[:3000]}\n```"})

        elif act == "run":
            cmd = action.get("cmd", "")
            console.print(f"[dim]$ {cmd}[/dim]")
            output = run_command(cmd)
            console.print(f"[dim]{output[:200]}[/dim]")
            history.append({"role": "user", "content": f"Command output:\n```\n{output[:3000]}\n```"})

        elif act == "search":
            query = action.get("query", "")
            console.print(f"[dim]🔍 Searching: {query}[/dim]")
            results = web_search(query)
            history.append({"role": "user", "content": f"Search results:\n{results[:3000]}"})

        elif act == "write":
            path = action.get("path", "")
            content = action.get("content", "")
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(content, encoding="utf-8")
            console.print(f"[green]📝 Wrote {path}[/green]")
            history.append({"role": "user", "content": f"File written to {path}. Continue."})

        else:
            history.append({"role": "user", "content": f"Unknown action '{act}'. Use: read, run, search, write, think, done."})

    return "Reached maximum steps. Here's what was accomplished so far."
