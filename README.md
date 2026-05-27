# Chatty-My-Agent

A powerful, extensible CLI-based AI assistant powered by Google Gemini and Groq with automatic fallback, autonomous mode, voice I/O, web UI, plugins, and 50+ commands.

---

## 🚀 Installation Tutorial (From Zero)

### Step 1: Install Python

1. Go to https://www.python.org/downloads/
2. Download Python 3.10 or newer
3. During install, **check "Add Python to PATH"**
4. Verify: open a terminal and run:
   ```cmd
   python --version
   ```

### Step 2: Install Git

1. Go to https://git-scm.com/downloads
2. Download and install Git for your OS
3. Verify:
   ```cmd
   git --version
   ```

### Step 3: Clone the Project

```cmd
git clone https://github.com/georgevpopa/Chatty-My-Agent.git
cd Chatty-My-Agent
```

### Step 4: Install Dependencies

```cmd
pip install -r requirements.txt
```

For optional voice support:
```cmd
pip install sounddevice numpy
```

### Step 5: Get Free API Keys

1. **Google Gemini** (primary AI):
   - Go to https://aistudio.google.com/apikey
   - Click "Create API Key"
   - Copy the key

2. **Groq** (fallback AI):
   - Go to https://console.groq.com/keys
   - Sign up and create an API key
   - Copy the key

### Step 6: Create .env File

In the `Chatty-My-Agent` folder, create a file called `.env`:

```
GEMINI_API_KEY=paste_your_gemini_key_here
GROQ_API_KEY=paste_your_groq_key_here
```

### Step 7: Run It!

```cmd
python agent.py
```

You should see:
```
Chatty-My-Agent — Tech assistant (Gemini + Groq)
Type /help for commands, or just ask a question
💡 Use /context to pin files the AI should always know about.
---
You:
```

Type a question and press Enter. That's it!

---

## Features

### AI & Models
- **Dual LLM** — Gemini 2.0 Flash + Groq Llama 3.3 70B with auto-fallback
- **Streaming** — Responses appear word by word
- **Personas** — Switch AI personality (senior dev, ELI5, code reviewer, DevOps)
- **Persistent memory** — Teach the AI facts it remembers across sessions
- **Autonomous agent** — AI decides what commands to run to achieve a goal
- **Token tracking** — Estimate usage per session + lifetime stats

### Code & Files
- Read, write, append, refactor, explain, summarize, diff files
- Auto-generate pytest unit tests
- Translate responses to any language
- Undo any file change

### Commands & DevOps
- Run commands with AI analysis or silently
- Auto-fix failed commands
- Chain commands with custom AI instructions
- Git overview, Docker status/logs, port checking
- Environment variable viewer (secrets masked)
- Fetch and analyze URLs

### Productivity
- Web search (DuckDuckGo, free)
- Clipboard integration (paste/copy)
- Multi-line input for code blocks
- Pin files as permanent context
- Snippet library + bookmarks
- Task tracking (todo list)
- Custom aliases (persistent shortcuts)

### Interfaces
- **CLI** — Full-featured terminal interface
- **Web UI** — Browser-based chat at localhost:5000
- **Voice** — Speech-to-text input + text-to-speech output

### Extensibility
- **Plugin system** — Drop Python files in `~/.chatty-agent/plugins/`
- **Persistent config** — Settings, aliases, memory saved to disk
- **Session memory** — Save/load conversations across sessions
- **Themes** — Dark, light, minimal

---

## All Commands (50+)

### File & Code
| Command | Description |
|---------|-------------|
| `/read <path>` | Read and analyze a file |
| `/write <path>` | Generate content and save to file |
| `/append <path>` | Append AI content to existing file |
| `/refactor <path>` | AI improves code (with undo) |
| `/test <path>` | Generate pytest unit tests |
| `/explain <path>` | Explain file in plain English |
| `/summarize <path>` | TL;DR of a long file |
| `/diff <f1> <f2>` | Compare two files |
| `/project <path>` | Analyze entire project folder |
| `/translate <lang>` | Translate last response |

### Commands & DevOps
| Command | Description |
|---------|-------------|
| `/run <cmd>` | Run command + AI analysis |
| `/shell <cmd>` | Run command silently |
| `/fix` | Auto-fix last failed command |
| `/git` | Git status + recent commits |
| `/chain <c1> \| <c2>` | Run + pipe to AI |
| `/docker` | List Docker containers |
| `/docker-logs <name>` | Analyze container logs |
| `/port <n>` | Check what's on a port |
| `/env` | Show env vars (secrets masked) |
| `/http <url>` | Fetch and analyze a URL |

### Search & Input
| Command | Description |
|---------|-------------|
| `/search <query>` | Web search (DuckDuckGo) |
| `/paste` | Analyze clipboard |
| `/copy` | Copy response to clipboard |
| `/multi` | Multi-line input mode |
| `/context <path>` | Pin file as permanent context |
| `/context clear` | Remove pinned context |

### AI & Intelligence
| Command | Description |
|---------|-------------|
| `/persona [name]` | Switch AI personality |
| `/learn <fact>` | Teach AI (persists forever) |
| `/memory` | Show learned facts |
| `/forget` | Clear all memories |
| `/retry` | Re-run last prompt |
| `/agent <goal>` | Autonomous mode |
| `/voice` | Voice input (STT) |
| `/speak` | Read response aloud (TTS) |

### Snippets & Tasks
| Command | Description |
|---------|-------------|
| `/snippet <name>` | Save response as snippet |
| `/snippets` | List snippets |
| `/load <name>` | Display a snippet |
| `/bookmark` | Bookmark last response |
| `/bookmarks` | List bookmarks |
| `/todo [text]` | Add/list tasks |
| `/todo done <n>` | Complete a task |

### Plugins
| Command | Description |
|---------|-------------|
| `/plugins` | List installed plugins |
| `/plugin <name> [args]` | Run a plugin |
| `/plugin-init` | Create example plugin |

### Session & Config
| Command | Description |
|---------|-------------|
| `/alias <name> <cmd>` | Create persistent shortcut |
| `/aliases` | List aliases |
| `/undo` | Revert last file change |
| `/history` | Conversation summary |
| `/stream` | Toggle streaming |
| `/timer` | Session duration |
| `/cost` | Token estimate |
| `/stats` | Lifetime statistics |
| `/status` | Full dashboard |
| `/config <key> <val>` | Set persistent config |
| `/theme <name>` | Switch theme |
| `/save [path]` | Save as markdown |
| `/export json` | Export as JSON |
| `/load-session` | Resume last session |
| `/clear` | Clear history |
| `/model` | Switch Gemini/Groq |
| `/help` | Show help |
| `/quit` | Exit (auto-saves) |

---

## Personas

| Name | Description |
|------|-------------|
| `default` | Helpful technical assistant |
| `senior_dev` | Senior engineer, production-quality advice |
| `eli5` | Explains like you're 5 years old |
| `reviewer` | Strict code reviewer |
| `devops` | DevOps/infrastructure focus |

Usage: `/persona senior_dev`

---

## Web UI

Run separately:
```cmd
python web_ui.py
```
Opens at http://localhost:5000. Supports chat, search, file reading, and commands.

---

## Plugin Development

Plugins live in `~/.chatty-agent/plugins/`. Each is a Python file:

```python
"""My custom plugin."""
name = "myplugin"
description = "Does something cool"

def run(args: str, messages: list, get_response) -> str:
    # args = everything after the plugin name
    # messages = conversation history
    # get_response = function to call the AI
    return "Plugin result here"
```

Use `/plugin-init` to generate an example.

---

## Project Structure

```
Chatty-My-Agent/
├── agent.py          ← Main CLI loop (50+ commands)
├── llm.py            ← LLM calls (Gemini + Groq + streaming)
├── tools.py          ← Utilities (file, web, clipboard, docker, ports)
├── storage.py        ← Config, aliases, memory, stats (persistent)
├── help_text.py      ← Help screen
├── autonomous.py     ← Autonomous agent mode
├── plugins.py        ← Plugin system
├── voice.py          ← Voice I/O (STT + TTS)
├── web_ui.py         ← Web UI (Flask)
├── requirements.txt  ← Dependencies
├── .env              ← API keys (not in git)
└── .gitignore
```

## Data Storage

All persistent data is in `~/.chatty-agent/`:
```
~/.chatty-agent/
├── config.json       ← Settings (model, theme, streaming, persona)
├── aliases.json      ← Custom command shortcuts
├── memory.json       ← Learned facts
├── history.json      ← Last session (auto-saved on quit)
├── stats.json        ← Lifetime usage statistics
└── plugins/          ← Custom plugins
```

---

## Requirements

- Python 3.10+
- Free API keys (Gemini + Groq)
- Optional: `sounddevice` + `numpy` for voice
- Optional: `flask` for web UI
- Optional: Docker for `/docker` commands

## License

MIT
