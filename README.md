# Chatty-My-Agent

A CLI-based AI assistant powered by Google Gemini and Groq (with automatic fallback).

## Features

- **Dual LLM support** — Gemini 2.0 Flash (primary) + Groq Llama 3.3 70B (fallback)
- **File analysis** — Read and analyze any file
- **Command execution** — Run shell commands and get AI analysis of output
- **Code generation** — Generate and save code to files
- **Conversation saving** — Export chats to markdown

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
| `/save [path]` | Save conversation to markdown |
| `/clear` | Clear conversation history |
| `/model` | Switch between Gemini and Groq |
| `/help` | Show all commands |
| `/quit` | Exit |

### Examples

```
You: explain what a decorator is in Python
You: /read C:\logs\app.log
You: /run netstat -an
You: /write utils.py
```

## Requirements

- Python 3.10+
- Free API keys (Gemini + Groq)
