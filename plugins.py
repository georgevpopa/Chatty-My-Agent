"""Plugin system for Chatty-My-Agent.

Plugins are Python files in ~/.chatty-agent/plugins/
Each plugin must define:
  - name: str
  - description: str  
  - run(args: str, messages: list, get_response: callable) -> str
"""
import importlib.util
from pathlib import Path

PLUGIN_DIR = Path.home() / ".chatty-agent" / "plugins"


def ensure_plugin_dir():
    PLUGIN_DIR.mkdir(parents=True, exist_ok=True)


def list_plugins() -> list[dict]:
    ensure_plugin_dir()
    plugins = []
    for f in PLUGIN_DIR.glob("*.py"):
        try:
            spec = importlib.util.spec_from_file_location(f.stem, f)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            plugins.append({
                "name": getattr(mod, "name", f.stem),
                "description": getattr(mod, "description", "No description"),
                "path": str(f),
                "module": mod,
            })
        except Exception as e:
            plugins.append({"name": f.stem, "description": f"Error: {e}", "path": str(f), "module": None})
    return plugins


def run_plugin(plugin_name: str, args: str, messages: list, get_response) -> str:
    plugins = list_plugins()
    for p in plugins:
        if p["name"].lower() == plugin_name.lower() and p["module"]:
            return p["module"].run(args, messages, get_response)
    return f"Plugin '{plugin_name}' not found. Use /plugins to list available."


# Example plugin template
EXAMPLE_PLUGIN = '''"""Example plugin: word counter."""
name = "wordcount"
description = "Count words in a file"


def run(args: str, messages: list, get_response) -> str:
    from pathlib import Path
    try:
        text = Path(args.strip()).read_text()
        words = len(text.split())
        lines = text.count("\\n") + 1
        return f"📊 {args}: {words} words, {lines} lines, {len(text)} chars"
    except Exception as e:
        return f"Error: {e}"
'''


def create_example_plugin():
    ensure_plugin_dir()
    example_path = PLUGIN_DIR / "wordcount.py"
    if not example_path.exists():
        example_path.write_text(EXAMPLE_PLUGIN)
        return str(example_path)
    return None
