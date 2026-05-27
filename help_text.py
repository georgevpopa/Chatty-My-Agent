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
  [bold cyan]/chain <c1> | <c2>[/bold cyan]    Pipe: run c1, feed output to AI, then c2

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
  [bold cyan]/todo [text][/bold cyan]          Add a task, or list all tasks
  [bold cyan]/todo done <n>[/bold cyan]        Mark task #n as done

[bold]SESSION & CONFIG:[/bold]
  [bold cyan]/alias <n> <cmd>[/bold cyan]      Create a shortcut (saved to disk)
  [bold cyan]/aliases[/bold cyan]              List all aliases
  [bold cyan]/undo[/bold cyan]                 Revert last file write/refactor
  [bold cyan]/history[/bold cyan]              Show conversation summary
  [bold cyan]/stream[/bold cyan]               Toggle streaming mode
  [bold cyan]/timer[/bold cyan]                Show session duration
  [bold cyan]/cost[/bold cyan]                 Show estimated token usage
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

  [dim]# Read and analyze a log file[/dim]
  You: /read C:\\logs\\app.log

  [dim]# Run a command and get AI explanation[/dim]
  You: /run ipconfig /all

  [dim]# Run silently[/dim]
  You: /shell pip install requests

  [dim]# Fix the last failed command[/dim]
  You: /run python app.py
  You: /fix

  [dim]# Generate a file[/dim]
  You: /write utils.py
  → What should the file contain? a CSV parser

  [dim]# Refactor (saves backup)[/dim]
  You: /refactor messy_code.py
  You: /undo    (reverts if you don't like it)

  [dim]# Generate tests[/dim]
  You: /test utils.py

  [dim]# Summarize a long file[/dim]
  You: /summarize C:\\logs\\huge.log

  [dim]# Translate last response[/dim]
  You: /translate spanish
  You: /translate romanian

  [dim]# Search the web[/dim]
  You: /search python asyncio best practices

  [dim]# Pin context (AI always sees this file)[/dim]
  You: /context C:\\dev\\project\\config.yaml
  You: /context clear

  [dim]# Chain commands[/dim]
  You: /chain dir /s | summarize what files are here

  [dim]# Aliases (persistent shortcuts)[/dim]
  You: /alias deploy /shell git push
  You: /alias status /git
  You: deploy    (runs the alias)

  [dim]# Multi-line input[/dim]
  You: /multi
  → paste code, type END

  [dim]# Snippets[/dim]
  You: /snippet postgres_connect
  You: /snippets
  You: /load postgres_connect

  [dim]# Tasks[/dim]
  You: /todo fix login bug
  You: /todo done 1

  [dim]# Session[/dim]
  You: /stream   /timer   /status   /cost
  You: /config model groq
  You: /theme minimal
  You: /save   /export json   /load-session
""")
