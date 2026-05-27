import os
import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".chatty-agent" / "config.json"
ALIASES_PATH = Path.home() / ".chatty-agent" / "aliases.json"
HISTORY_PATH = Path.home() / ".chatty-agent" / "history.json"

DEFAULT_CONFIG = {
    "model": "gemini",
    "streaming": True,
    "theme": "dark",
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
