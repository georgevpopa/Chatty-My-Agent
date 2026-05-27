# Chatty-My-Agent

A CLI-based AI assistant powered by Google Gemini and Groq (with automatic fallback).

## Features

- **Dual LLM support** — Gemini 2.0 Flash (primary) + Groq Llama 3.3 70B (fallback)
- **Streaming responses** — See text appear word by word in real-time
- **File analysis** — Read and analyze any file
- **Code generation** — Generate and save code to files
- **Append to files** — Add AI-generated content to existing files
- **Refactoring** — AI rewrites your code with improvements (keeps a backup)
- **Test generation** — Auto-generate pytest unit tests for any file
- **Web search** — DuckDuckGo search (free, no key needed)
- **Command execution** — Run shell commands and get AI analysis
- **Silent commands** — Run commands without AI analysis
- **Auto-fix** — Fix errors from failed commands automatically
- **Git overview** — Quick branch, status, and recent commits view
- **Project overview** — Scan an entire folder and get a tech stack summary
- **File comparison** — Diff two files with AI explanation
- **Code explanation** — Get plain English explanations of any file
- **Multi-line input** — Paste code blocks or long text
- **Clipboard integration** — Paste to analyze, copy responses
- **Snippet library** — Save, list, and reuse useful AI responses
- **Task tracking** — Built-in todo list to track work
- **Session timer** — Track how long you've been working
- **Status dashboard** — See current settings and session stats
- **Conversation management** — Save, clear, summarize history

## Setup

```bash
git clone https://github.com/georgevpopa/Chatty-My-Agent.git
cd Chatty-My-Agent
pip install -r requirements.txt
```

Create a `.env` file with your API keys:

```
GEMINI_API_KEY=your_gemini_key_here
GROQ_API_KEY=your_groq_key_here
```

Get free keys from:
- Gemini: https://aistudio.google.com/apikey
- Groq: https://console.groq.com/keys

## Usage

```bash
python agent.py
```

### All Commands (27 total)

| Command | Description |
|---------|-------------|
| `/read <path>` | Read a file and analyze it |
| `/run <cmd>` | Run a command and analyze output |
| `/shell <cmd>` | Run a command silently (no AI analysis) |
| `/write <path>` | Generate content and save to file |
| `/append <path>` | Append AI-generated content to existing file |
| `/refactor <path>` | AI rewrites file with improvements (saves .bak backup) |
| `/test <path>` | Generate pytest unit tests for a file |
| `/search <query>` | Search the web (DuckDuckGo) |
| `/explain <path>` | Explain a file in plain English |
| `/project <path>` | Analyze an entire project folder |
| `/fix` | Auto-fix the last failed command |
| `/git` | Quick git status, branch, and recent commits |
| `/paste` | Analyze clipboard contents |
| `/copy` | Copy last AI response to clipboard |
| `/multi` | Enter multi-line input mode (type END to finish) |
| `/diff <f1> <f2>` | Compare two files |
| `/snippet <name>` | Save last response as a named snippet |
| `/snippets` | List all saved snippets |
| `/load <name>` | Load and display a saved snippet |
| `/todo [text]` | Add a task or list all tasks |
| `/todo done <n>` | Mark task #n as done |
| `/history` | Show conversation summary |
| `/stream` | Toggle streaming mode (word by word) |
| `/timer` | Show how long you've been in this session |
| `/status` | Show current settings and session stats |
| `/save [path]` | Save conversation to markdown |
| `/clear` | Clear conversation history |
| `/model` | Switch between Gemini and Groq |
| `/help` | Show help with examples |
| `/quit` | Exit |

### Examples

```bash
# Ask any tech question
You: what is a REST API?
You: write a Python function to sort a list of dicts by key

# Read and analyze a log file
You: /read C:\logs\app.log

# Run a command and get AI explanation
You: /run ipconfig /all
You: /run git status
You: /run python -m pytest tests/

# Run a command silently (just execute, no AI)
You: /shell mkdir new_folder
You: /shell pip install requests

# Fix a failed command automatically
You: /run python app.py
You: /fix

# Generate a new file
You: /write utils.py
→ What should the file contain? a function to parse CSV files

# Add to an existing file
You: /append utils.py
→ What to add? a function to validate email addresses

# Refactor messy code (saves backup as .bak)
You: /refactor C:\dev\project\messy_code.py

# Generate unit tests
You: /test C:\dev\project\utils.py

# Search the web
You: /search python asyncio best practices 2026
You: /search how to fix CORS error in FastAPI

# Explain code in plain English
You: /explain C:\dev\project\main.py

# Analyze a whole project
You: /project C:\dev\my-app

# Quick git overview
You: /git

# Compare files
You: /diff config_old.yaml config_new.yaml

# Multi-line input (paste code blocks)
You: /multi
→ (type or paste multiple lines, then type END)

# Save and reuse code snippets
You: how do I connect to PostgreSQL in Python?
You: /snippet postgres_connect    (saves the response)
You: /snippets                    (list all saved)
You: /load postgres_connect       (show it again)

# Track tasks
You: /todo fix the login bug
You: /todo refactor database module
You: /todo              (shows all tasks)
You: /todo done 1       (marks first task done)

# Clipboard workflow
You: /paste       (analyzes what you copied)
You: /copy        (copies AI answer to clipboard)

# Session info
You: /stream      (toggle streaming on/off)
You: /timer       (how long you've been here)
You: /status      (full dashboard)
You: /model       (switch Gemini ↔ Groq)

# Conversation management
You: /save            (auto-named file)
You: /save notes.md   (custom name)
You: /clear           (fresh start)
You: /history         (summarize conversation)
```

## How It Works

1. You type a question or command
2. The agent sends it to **Gemini** (fast, free, good at code)
3. If Gemini fails (rate limit, error), it automatically falls back to **Groq**
4. Response is streamed word by word (or displayed at once if streaming is off)

## Requirements

- Python 3.10+
- Free API keys (Gemini + Groq)

## License

MIT
