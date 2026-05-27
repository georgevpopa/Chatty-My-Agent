from rich.console import Console

console = Console()


def show_help():
    console.print("""
[bold green]━━━ Chatty-My-Agent Help ━━━[/bold green]

[bold]FILE & CODE:[/bold]
  [bold cyan]/read <path>[/bold cyan]          Read a file and get AI analysis
  [bold cyan]/write <path>[/bold cyan]         Generate code/content and save to file
  [bold cyan]/append <path>[/bold cyan]        Append AI-generated content to existing file
  [bold cyan]/refactor <path>[/bold cyan]      AI rewrites file with improvements (saves .bak)
  [bold cyan]/test <path>[/bold cyan]          Generate pytest unit tests for a file
  [bold cyan]/explain <path>[/bold cyan]       Explain a file in plain English
  [bold cyan]/summarize <path>[/bold cyan]     Get a TL;DR of a long file
  [bold cyan]/diff <f1> <f2>[/bold cyan]       Compare two files
  [bold cyan]/project <path>[/bold cyan]       Analyze an entire project folder
  [bold cyan]/translate <lang>[/bold cyan]     Translate last response to a language

[bold]COMMANDS & SYSTEM:[/bold]
  [bold cyan]/run <cmd>[/bold cyan]            Run a shell command and analyze output
  [bold cyan]/shell <cmd>[/bold cyan]          Run command silently (no AI analysis)
  [bold cyan]/fix[/bold cyan]                  Auto-fix the last error from /run
  [bold cyan]/git[/bold cyan]                  Quick git status, branch, recent commits
  [bold cyan]/chain <c1> | <c2>[/bold cyan]    Pipe: run c1, feed output to AI with instruction
  [bold cyan]/docker[/bold cyan]               List running Docker containers
  [bold cyan]/docker-logs <name>[/bold cyan]   Get and analyze container logs
  [bold cyan]/port <n>[/bold cyan]             Check what's running on a port
  [bold cyan]/env[/bold cyan]                  Show environment variables (secrets masked)
  [bold cyan]/http <url>[/bold cyan]           Fetch a URL and analyze content

[bold]SEARCH & INPUT:[/bold]
  [bold cyan]/search <query>[/bold cyan]       Search the web (DuckDuckGo, free)
  [bold cyan]/paste[/bold cyan]                Analyze clipboard contents
  [bold cyan]/copy[/bold cyan]                 Copy last AI response to clipboard
  [bold cyan]/multi[/bold cyan]                Enter multi-line input mode (END to finish)
  [bold cyan]/context <path>[/bold cyan]       Pin a file as permanent context
  [bold cyan]/context clear[/bold cyan]        Remove all pinned context

[bold]SNIPPETS & TASKS:[/bold]
  [bold cyan]/snippet <name>[/bold cyan]       Save last response as a named snippet
  [bold cyan]/snippets[/bold cyan]             List all saved snippets
  [bold cyan]/load <name>[/bold cyan]          Load and display a snippet
  [bold cyan]/bookmark[/bold cyan]             Bookmark last response
  [bold cyan]/bookmarks[/bold cyan]            List all bookmarks
  [bold cyan]/todo [text][/bold cyan]          Add a task, or list all tasks
  [bold cyan]/todo done <n>[/bold cyan]        Mark task #n as done

[bold]AI & INTELLIGENCE:[/bold]
  [bold cyan]/persona [name][/bold cyan]       Switch AI personality
  [bold cyan]/learn <fact>[/bold cyan]         Teach AI something (persists across sessions)
  [bold cyan]/memory[/bold cyan]               Show all learned facts
  [bold cyan]/forget[/bold cyan]               Clear all memories
  [bold cyan]/retry[/bold cyan]                Re-run the last prompt
  [bold cyan]/agent <goal>[/bold cyan]         Autonomous mode (AI decides actions)
  [bold cyan]/voice[/bold cyan]                Voice input (speak instead of type)
  [bold cyan]/speak[/bold cyan]                Read last response aloud (TTS)

[bold]PLUGINS:[/bold]
  [bold cyan]/plugins[/bold cyan]              List installed plugins
  [bold cyan]/plugin <n> [args][/bold cyan]    Run a plugin
  [bold cyan]/plugin-init[/bold cyan]          Create example plugin

[bold]SESSION & CONFIG:[/bold]
  [bold cyan]/alias <n> <cmd>[/bold cyan]      Create a shortcut (saved to disk)
  [bold cyan]/aliases[/bold cyan]              List all aliases
  [bold cyan]/undo[/bold cyan]                 Revert last file write/refactor
  [bold cyan]/history[/bold cyan]              Show conversation summary
  [bold cyan]/stream[/bold cyan]               Toggle streaming mode
  [bold cyan]/timer[/bold cyan]                Show session duration
  [bold cyan]/cost[/bold cyan]                 Show estimated token usage
  [bold cyan]/stats[/bold cyan]                Lifetime usage statistics
  [bold cyan]/status[/bold cyan]               Show current settings and stats
  [bold cyan]/config <k> <v>[/bold cyan]       Set a persistent config value
  [bold cyan]/theme <name>[/bold cyan]         Switch theme (dark/light/minimal)
  [bold cyan]/save [path][/bold cyan]          Save conversation to markdown
  [bold cyan]/export json[/bold cyan]          Export conversation as JSON
  [bold cyan]/load-session[/bold cyan]         Load last saved session from disk
  [bold cyan]/clear[/bold cyan]                Clear conversation history
  [bold cyan]/model[/bold cyan]                Switch between Gemini and Groq
  [bold cyan]/help[/bold cyan]                 Show this help
  [bold cyan]/quit[/bold cyan]                 Exit

[bold]EXAMPLES:[/bold]

  [dim]# Ask any tech question[/dim]
  You: what is a REST API?

  [dim]# File operations[/dim]
  You: /read C:\\logs\\app.log
  You: /write utils.py
  You: /refactor messy_code.py
  You: /test utils.py
  You: /undo

  [dim]# Commands[/dim]
  You: /run ipconfig /all
  You: /shell pip install requests
  You: /fix
  You: /chain dir /s | list only Python files

  [dim]# DevOps[/dim]
  You: /docker
  You: /docker-logs my-container
  You: /port 8080
  You: /env
  You: /git

  [dim]# Web[/dim]
  You: /search python asyncio best practices
  You: /http https://api.github.com/repos/python/cpython

  [dim]# AI personality[/dim]
  You: /persona senior_dev
  You: /persona eli5
  You: /persona reviewer

  [dim]# Memory (persists across sessions)[/dim]
  You: /learn I prefer TypeScript over JavaScript
  You: /learn My project uses PostgreSQL
  You: /memory
  You: /forget

  [dim]# Autonomous agent[/dim]
  You: /agent find all TODO comments in C:\\dev\\project
  You: /agent create a Flask hello world app

  [dim]# Voice[/dim]
  You: /voice    (speak instead of type)
  You: /speak    (hear the response)

  [dim]# Plugins[/dim]
  You: /plugin-init
  You: /plugins
  You: /plugin wordcount C:\\dev\\file.py

  [dim]# Snippets & bookmarks[/dim]
  You: /snippet postgres_connect
  You: /bookmark
  You: /bookmarks

  [dim]# Session[/dim]
  You: /stream   /timer   /cost   /stats   /status
  You: /retry
  You: /save   /export json   /load-session

  [dim]# Web UI (separate process)[/dim]
  Run: python web_ui.py → http://localhost:5000
""")
