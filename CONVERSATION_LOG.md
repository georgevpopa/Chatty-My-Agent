# Chatty-My-Agent - Development Conversation Log
## Date: 2026-05-27

This file contains the development conversation that built Chatty-My-Agent from scratch.
Use this as reference to continue development from where we left off.

---

## Summary of What Was Built

### Architecture
- Python CLI agent with modular architecture
- 7 LLM providers with auto-fallback
- Web UI (Flask) with model selector dropdown
- Voice I/O (speech-to-text + text-to-speech)
- Autonomous agent mode
- Plugin system
- Persistent config, memory, aliases, stats

### Files
- agent.py — Main CLI loop (50+ commands)
- llm.py — LLM calls (7 providers + streaming)
- tools.py — Utilities (file, web, clipboard, docker, ports)
- storage.py — Persistent config, aliases, memory, stats
- help_text.py — Help screen
- autonomous.py — Autonomous agent mode
- plugins.py — Plugin system
- voice.py — Voice I/O (STT + TTS)
- web_ui.py — Web UI (Flask) with model selector
- requirements.txt — Dependencies
- .env.example — Template for API keys
- .gitignore

### Models Available
1. Google Gemini 2.0 Flash (gemini)
2. Groq Llama 3.3 70B (groq)
3. Cohere Command R+ (cohere)
4. Mistral Small 3.1 (mistral)
5. OpenRouter Llama 3.3 70B free (openrouter)
6. Together AI Llama 3.3 70B Turbo (together)
7. HuggingFace Qwen 2.5 72B (huggingface)

### Commands (50+)
File & Code: /read, /write, /append, /refactor, /test, /explain, /summarize, /diff, /project, /translate
Commands: /run, /shell, /fix, /git, /chain, /docker, /docker-logs, /port, /env, /http
Search & Input: /search, /paste, /copy, /multi, /context, /context clear
AI: /persona, /learn, /memory, /forget, /retry, /agent, /voice, /speak
Snippets & Tasks: /snippet, /snippets, /load, /bookmark, /bookmarks, /todo, /todo done
Plugins: /plugins, /plugin, /plugin-init
Session: /alias, /aliases, /undo, /history, /stream, /timer, /cost, /stats, /status, /config, /theme, /save, /export, /load-session, /clear, /model, /models, /help, /quit

### Key Decisions Made
- Python chosen for ecosystem and library support
- Gemini as primary (best free tier), Groq as fallback (fastest)
- DuckDuckGo for web search (no API key needed)
- Rich library for CLI formatting
- Flask for web UI (lightweight)
- Groq Whisper for speech-to-text
- Windows SAPI for text-to-speech
- Plugin system uses ~/.chatty-agent/plugins/ directory
- All persistent data in ~/.chatty-agent/

### Known Issues / Notes
- API keys were exposed in chat — user needs to regenerate them
- Gemini free tier can hit rate limits (quota 0 error seen)
- Groq SDK was upgraded from 0.12.0 to 1.2.0 to fix httpx compatibility
- Web UI mascot needed monospace font fix
- Voice requires optional deps: sounddevice, numpy
- Cohere API may differ slightly between SDK versions

### What Could Be Added Next
- Tab autocomplete for commands in CLI
- RAG (index local docs for better answers)
- Email integration (/email)
- SQL database queries (/sql)
- Notification sounds for long tasks
- More themes
- Mobile-friendly web UI
- WebSocket streaming in web UI
- Multi-user support in web UI
- Rate limit handling with automatic retry/wait

### GitHub Repo
https://github.com/georgevpopa/Chatty-My-Agent

### Tech Stack
- Python 3.13
- google-generativeai, groq, cohere, mistralai, httpx
- rich (CLI formatting)
- flask (web UI)
- duckduckgo-search (web search)
- python-dotenv (env management)
- sounddevice + numpy (voice, optional)
