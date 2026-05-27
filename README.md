# Chatty-My-Agent

A powerful CLI-based AI assistant powered by Google Gemini and Groq with automatic fallback.

## Features

### AI & Models
- **Dual LLM support** — Gemini 2.0 Flash (primary) + Groq Llama 3.3 70B (fallback)
- **Streaming responses** — See text appear word by word in real-time
- **Automatic fallback** — If one provider fails, seamlessly switches to the other
- **Token tracking** — Estimate how many tokens you've used per session

### Code & Files
- **File analysis** — Read and analyze any file
- **Code generation** — Generate and save code to files
- **Append to files** — Add AI-generated content to existing files
- **Refactoring** — AI rewrites your code with improvements (with undo support)
- **Test generation** — Auto-generate pytest unit tests for any file
- **Code explanation** — Get plain English explanations of any file
- **File summarization** — TL;DR of long files or logs
- **File comparison** — Diff two files with AI explanation
- **Project overview** — Scan an entire folder and get a tech stack summary
- **Translation** — Translate AI responses to any language

### Commands & System
- **Command execution** — Run shell commands and get AI analysis
- **Silent commands** — Run commands without AI analysis
- **Auto-fix** — Fix errors from failed commands automatically
- **Command chaining** — Pipe command output to AI with custom instructions
- **Git overview** — Quick branch, status, and recent commits view

### Productivity
- **Web search** — DuckDuckGo search (free, no key needed)
- **Clipboard integration** — Paste to analyze, copy responses
- **Multi-line input** — Paste code blocks or long text
- **Pinned context** — Keep files permanently in AI's context
- **Snippet library** — Save, list, and reuse useful AI responses
- **Task tracking** — Built-in todo list to track work
- **Aliases** — Create persistent custom shortcuts for commands
- **Undo** — Revert any file write, append, or refactor

### Session & Config
- **Persistent config** — Settings saved to disk (model, streaming, theme)
- **Session memory** — Save and reload conversation history across sessions
- **Themes** — Dark, light, and minimal color schemes
- **Session timer** — Track how long you've been working
- **Export** — Save conversations as markdown or JSON

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

### All Commands (37 total)

| Command | Description |
|---------|-------------|
| `/read <path>` | Read a file and analyze it |
| `/run <cmd>` | Run a command and analyze output |
| `/shell <cmd>` | Run a command silently (no AI) |
| `/write <path>` | Generate content and save to file |
| `/append <path>` | Append AI content to existing file |
| `/refactor <path>` | AI rewrites file with improvements |
| `/test <path>` | Generate pytest unit tests |
| `/search <query>` | Search the web (DuckDuckGo) |
| `/explain <path>` | Explain a file in plain English |
| `/summarize <path>` | TL;DR of a long file |
| `/translate <lang>` | Translate last response |
| `/project <path>` | Analyze an entire project folder |
| `/fix` | Auto-fix the last failed command |
| `/git` | Quick git status + recent commits |
| `/chain <c1> \| <c2>` | Run command, pipe to AI with instruction |
| `/paste` | Analyze clipboard contents |
| `/copy` | Copy last AI response to clipboard |
| `/multi` | Multi-line input mode (END to finish) |
| `/context <path>` | Pin a file as permanent context |
| `/context clear` | Remove all pinned context |
| `/diff <f1> <f2>` | Compare two files |
| `/snippet <name>` | Save last response as snippet |
| `/snippets` | List all saved snippets |
| `/load <name>` | Display a saved snippet |
| `/todo [text]` | Add a task or list all tasks |
| `/todo done <n>` | Mark task #n as done |
| `/alias <name> <cmd>` | Create a persistent shortcut |
| `/aliases` | List all aliases |
| `/undo` | Revert last file write/refactor |
| `/voice` | Voice input (speak instead of type) |
| `/speak` | Read last response aloud (TTS) |
| `/agent <goal>` | Autonomous mode (AI decides actions) |
| `/plugins` | List installed plugins |
| `/plugin <name> [args]` | Run a plugin |
| `/plugin-init` | Create example plugin |
| `/history` | Show conversation summary |
| `/stream` | Toggle streaming mode |
| `/timer` | Show session duration |
| `/cost` | Show estimated token usage |
| `/status` | Full dashboard |
| `/config <key> <val>` | Set persistent config value |
| `/theme <name>` | Switch theme (dark/light/minimal) |
| `/save [path]` | Save conversation to markdown |
| `/export json` | Export conversation as JSON |
| `/load-session` | Load last saved session |
| `/clear` | Clear conversation history |
| `/model` | Switch between Gemini and Groq |
| `/help` | Show help with examples |
| `/quit` | Exit (auto-saves session) |

### Examples

```bash
# Ask any tech question
You: what is a REST API?
You: write me a Python web scraper

# Read and analyze files
You: /read C:\logs\app.log
You: /summarize C:\docs\spec.md
You: /explain C:\dev\project\main.py

# Run commands
You: /run ipconfig /all
You: /run python -m pytest
You: /shell pip install requests    (silent, no AI)

# Chain: run command + custom AI instruction
You: /chain dir /s | list only Python files

# Fix errors
You: /run python app.py
You: /fix

# Generate and modify files
You: /write utils.py
You: /append utils.py
You: /refactor messy_code.py
You: /undo                          (revert if needed)

# Generate tests
You: /test utils.py

# Translate
You: /translate spanish
You: /translate romanian

# Web search
You: /search python asyncio best practices

# Pin context (AI always sees these files)
You: /context C:\dev\project\config.yaml
You: /context C:\dev\project\schema.sql
You: /context clear

# Git overview
You: /git

# Compare files
You: /diff old.yaml new.yaml

# Multi-line input
You: /multi
→ paste code block, type END

# Snippets (save & reuse responses)
You: /snippet postgres_connect
You: /snippets
You: /load postgres_connect

# Tasks
You: /todo fix the login bug
You: /todo done 1

# Aliases (persistent shortcuts)
You: /alias deploy /shell git push
You: /alias logs /read C:\logs\app.log
You: deploy                         (runs the alias)
You: /aliases                       (list all)

# Clipboard
You: /paste    (analyze what you copied)
You: /copy     (copy AI answer)

# Session management
You: /stream        (toggle word-by-word)
You: /timer         (session duration)
You: /cost          (token estimate)
You: /status        (full dashboard)
You: /config model groq
You: /theme minimal
You: /save
You: /export json
You: /load-session  (resume last session)

# Voice
You: /voice         (speak instead of type)
You: /speak         (hear the response)

# Autonomous agent
You: /agent find all TODO comments in C:\dev\project
You: /agent create a hello world Flask app in C:\dev\test

# Plugins
You: /plugin-init
You: /plugins
You: /plugin wordcount C:\dev\file.py

# Web UI (separate process)
> python web_ui.py
→ opens at http://localhost:5000
```

## Project Structure

```
Chatty-My-Agent/
├── agent.py          ← Main CLI loop and command handling
├── llm.py            ← LLM provider calls (Gemini + Groq)
├── tools.py          ← Utility functions (file, clipboard, search)
├── storage.py        ← Persistent config, aliases, history
├── help_text.py      ← Help screen content
├── autonomous.py     ← Autonomous agent mode
├── plugins.py        ← Plugin system
├── voice.py          ← Voice input/output (STT + TTS)
├── web_ui.py         ← Web UI (Flask)
├── requirements.txt  ← Python dependencies
├── .env              ← Your API keys (not in git)
└── .gitignore
```

## How It Works

1. You type a question or command
2. The agent sends it to **Gemini** (fast, free, good at code)
3. If Gemini fails (rate limit, error), it automatically falls back to **Groq**
4. Response is streamed word by word (or displayed at once if streaming is off)
5. Pinned context files are included with every request
6. Session is auto-saved on exit and can be reloaded

## Stretch Features

### Web UI
Run `python web_ui.py` to start a browser-based interface at http://localhost:5000.
Supports chat, `/search`, `/read`, `/run`, `/model`, and `/clear`.

### Voice Input/Output
- `/voice` — Records 5 seconds from your microphone, transcribes with Groq Whisper
- `/speak` — Reads the last response aloud using Windows TTS
- Requires: `pip install sounddevice numpy`

### Autonomous Agent Mode
- `/agent <goal>` — The AI decides what to do: reads files, runs commands, searches the web, writes files
- Runs up to 10 steps autonomously
- Example: `/agent find all Python files with TODO comments in C:\dev\project`

### Plugin System
- Plugins are Python files in `~/.chatty-agent/plugins/`
- `/plugin-init` creates an example plugin
- `/plugins` lists available plugins
- `/plugin <name> <args>` runs a plugin
- Each plugin defines `name`, `description`, and a `run()` function

## Configuration

Settings are saved to `~/.chatty-agent/config.json`:

```json
{
  "model": "gemini",
  "streaming": true,
  "theme": "dark"
}
```

Aliases saved to `~/.chatty-agent/aliases.json`.
Session history saved to `~/.chatty-agent/history.json`.

## Requirements

- Python 3.10+
- Free API keys (Gemini + Groq)

## License

MIT
