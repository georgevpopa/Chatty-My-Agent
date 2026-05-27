import os
import json
from pathlib import Path
from datetime import datetime

CONFIG_PATH = Path.home() / ".chatty-agent" / "config.json"
ALIASES_PATH = Path.home() / ".chatty-agent" / "aliases.json"
HISTORY_PATH = Path.home() / ".chatty-agent" / "history.json"
MEMORY_PATH = Path.home() / ".chatty-agent" / "memory.json"
STATS_PATH = Path.home() / ".chatty-agent" / "stats.json"

DEFAULT_CONFIG = {
    "model": "gemini",
    "streaming": True,
    "theme": "dark",
    "persona": "default",
}

PERSONAS = {
    "default": "You are a helpful technical assistant. Be concise and direct.",
    "senior_dev": "You are a senior software engineer with 15 years of experience. Give detailed, production-quality advice. Mention edge cases and best practices.",
    "eli5": "Explain everything like I'm 5 years old. Use simple words, analogies, and examples. No jargon.",
    "reviewer": "You are a strict code reviewer. Point out bugs, security issues, performance problems, and style violations. Be thorough but constructive.",
    "devops": "You are a DevOps engineer. Focus on infrastructure, CI/CD, containers, monitoring, and deployment.",
}


def ensure_dir():
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    ensure_dir()
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    ensure_dir()
    CONFIG_PATH.write_text(json.dumps(config, indent=2))


def load_aliases() -> dict:
    ensure_dir()
    if ALIASES_PATH.exists():
        return json.loads(ALIASES_PATH.read_text())
    return {}


def save_aliases(aliases: dict):
    ensure_dir()
    ALIASES_PATH.write_text(json.dumps(aliases, indent=2))


def save_history(messages: list[dict]):
    ensure_dir()
    HISTORY_PATH.write_text(json.dumps(messages, indent=2))


def load_history() -> list[dict]:
    ensure_dir()
    if HISTORY_PATH.exists():
        return json.loads(HISTORY_PATH.read_text())
    return []


# Persistent memory
def load_memory() -> list[str]:
    ensure_dir()
    if MEMORY_PATH.exists():
        return json.loads(MEMORY_PATH.read_text())
    return []


def save_memory(memory: list[str]):
    ensure_dir()
    MEMORY_PATH.write_text(json.dumps(memory, indent=2))


def add_memory(fact: str):
    mem = load_memory()
    mem.append(fact)
    save_memory(mem)


def clear_memory():
    save_memory([])


# Lifetime stats
def load_stats() -> dict:
    ensure_dir()
    if STATS_PATH.exists():
        return json.loads(STATS_PATH.read_text())
    return {"sessions": 0, "messages": 0, "tokens": 0, "first_use": None}


def save_stats(stats: dict):
    ensure_dir()
    STATS_PATH.write_text(json.dumps(stats, indent=2))


def update_stats(messages_count: int, tokens: int):
    stats = load_stats()
    stats["sessions"] += 1
    stats["messages"] += messages_count
    stats["tokens"] += tokens
    if not stats["first_use"]:
        stats["first_use"] = datetime.now().isoformat()
    stats["last_use"] = datetime.now().isoformat()
    save_stats(stats)
