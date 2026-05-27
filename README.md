# Chatty-My-Agent

A CLI-based AI assistant powered by Google Gemini and Groq (with automatic fallback).

## Features

- **Dual LLM support** — Gemini 2.0 Flash (primary) + Groq Llama 3.3 70B (fallback)
- **File analysis** — Read and analyze any file
- **Code generation** — Generate and save code to files
- **Web search** — DuckDuckGo search (free, no key needed)
- **Command execution** — Run shell commands and get AI analysis
- **Auto-fix** — Fix errors from failed commands
- **File comparison** — Diff two files with AI explanation
- **Clipboard integration** — Paste to analyze, copy responses
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

### Commands

| Command | Description |
|---------|-------------|
| `/read <path>` | Read a file and analyze it |
| `/run <cmd>` | Run a command and analyze output |
| `/write <path>` | Generate content and save to file |
| `/search <query>` | Search the web (DuckDuckGo) |
| `/explain <path>` | Explain a file in plain English |
| `/fix` | Auto-fix the last failed command |
| `/paste` | Analyze clipboard contents |
| `/copy` | Copy last AI response to clipboard |
| `/diff <f1> <f2>` | Compare two files |
| `/history` | Show conversation summary |
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

# Fix a failed command
You: /run python app.py
You: /fix

# Generate a file
You: /write utils.py
→ What should the file contain? a function to parse CSV files

# Search the web
You: /search python asyncio best practices 2026

# Explain code
You: /explain C:\dev\project\main.py

# Compare files
You: /diff config_old.yaml config_new.yaml

# Clipboard workflow
You: /paste       (analyzes what you copied)
You: /copy        (copies AI answer to clipboard)
```

## Requirements

- Python 3.10+
- Free API keys (Gemini + Groq)
