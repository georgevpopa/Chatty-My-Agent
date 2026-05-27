# Chatty-My-Agent

A CLI-based AI assistant powered by Google Gemini and Groq (with automatic fallback).

## Features

- **Dual LLM support** — Gemini 2.0 Flash (primary) + Groq Llama 3.3 70B (fallback)
- **Streaming responses** — See text appear word by word in real-time
- **File analysis** — Read and analyze any file
- **Code generation** — Generate and save code to files
- **Web search** — DuckDuckGo search (free, no key needed)
- **Command execution** — Run shell commands and get AI analysis
- **Auto-fix** — Fix errors from failed commands automatically
- **Project overview** — Scan an entire folder and get a tech stack summary
- **File comparison** — Diff two files with AI explanation
- **Code explanation** — Get plain English explanations of any file
- **Clipboard integration** — Paste to analyze, copy responses
- **Task tracking** — Built-in todo list to track work
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

### All Commands

| Command | Description |
|---------|-------------|
| `/read <path>` | Read a file and analyze it |
| `/run <cmd>` | Run a command and analyze output |
| `/write <path>` | Generate content and save to file |
| `/search <query>` | Search the web (DuckDuckGo) |
| `/explain <path>` | Explain a file in plain English |
| `/project <path>` | Analyze an entire project folder |
| `/fix` | Auto-fix the last failed command |
| `/paste` | Analyze clipboard contents |
| `/copy` | Copy last AI response to clipboard |
| `/diff <f1> <f2>` | Compare two files |
| `/todo [text]` | Add a task or list all tasks |
| `/todo done <n>` | Mark task #n as done |
| `/history` | Show conversation summary |
| `/stream` | Toggle streaming mode (word by word) |
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

# Run a command and get explanation
You: /run ipconfig /all
You: /run git status
You: /run python -m pytest tests/

# Fix a failed command automatically
You: /run python app.py
You: /fix

# Generate a file
You: /write utils.py
→ What should the file contain? a function to parse CSV files

# Search the web
You: /search python asyncio best practices 2026
You: /search how to fix CORS error in FastAPI

# Explain code in plain English
You: /explain C:\dev\project\main.py

# Analyze a whole project
You: /project C:\dev\my-app

# Compare files
You: /diff config_old.yaml config_new.yaml

# Track tasks
You: /todo fix the login bug
You: /todo refactor database module
You: /todo              (shows all tasks)
You: /todo done 1       (marks first task done)

# Clipboard workflow
You: /paste       (analyzes what you copied)
You: /copy        (copies AI answer to clipboard)

# Toggle streaming (see response word by word)
You: /stream

# Conversation management
You: /save            (auto-named file)
You: /save notes.md   (custom name)
You: /clear           (fresh start)
You: /history         (summarize conversation)
You: /model           (switch Gemini ↔ Groq)
```

## How It Works

1. You type a question or command
2. The agent sends it to **Gemini** (fast, free, good at code)
3. If Gemini fails (rate limit, error), it automatically falls back to **Groq**
4. Response is displayed with markdown formatting (or streamed word by word)

## Requirements

- Python 3.10+
- Free API keys (Gemini + Groq)

## License

MIT
