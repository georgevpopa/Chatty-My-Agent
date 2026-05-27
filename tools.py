import subprocess
from pathlib import Path


def read_file(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading file: {e}"


def run_command(cmd: str) -> str:
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        return output.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return "Command timed out (30s limit)"
    except Exception as e:
        return f"Error: {e}"


def web_search(query: str) -> str:
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        if not results:
            return "No results found."
        output = ""
        for r in results:
            output += f"**{r['title']}**\n{r['href']}\n{r['body']}\n\n"
        return output.strip()
    except Exception as e:
        return f"Search error: {e}"


def scan_project(path: str) -> str:
    p = Path(path)
    if not p.is_dir():
        return f"Error: {path} is not a directory"
    ignore = {".git", "__pycache__", "node_modules", ".venv", "venv", ".env", "dist", "build"}
    lines = []
    file_count = 0
    for item in sorted(p.rglob("*")):
        if any(part in ignore for part in item.parts):
            continue
        if item.is_file():
            rel = item.relative_to(p)
            size = item.stat().st_size
            lines.append(f"  {rel} ({size} bytes)")
            file_count += 1
            if file_count > 50:
                lines.append("  ... (truncated, too many files)")
                break
    return f"Project: {path}\nFiles ({file_count}):\n" + "\n".join(lines)


def clipboard_copy(text: str) -> bool:
    try:
        subprocess.run("clip", input=text.encode("utf-8"), check=True)
        return True
    except Exception:
        return False


def clipboard_paste() -> str:
    try:
        result = subprocess.run(
            ["powershell", "-command", "Get-Clipboard"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"
