"""Web UI for Chatty-My-Agent using Flask."""
import os
import sys
import json
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify
from dotenv import load_dotenv

sys.path.insert(0, r"C:\dev\torch_pkg")
load_dotenv()

from llm import call_model, MODELS
from tools import read_file, run_command, web_search
from rag import index_file, index_folder, get_context_for_query, list_indexed, clear_index

app = Flask(__name__)
messages = []
current_model = "gemini"
fallback_model = "groq"
knowledge_mode = "general"

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Chatty-My-Agent</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #1a1a2e; color: #eee; height: 100vh; display: flex; flex-direction: column; }
        #header { padding: 12px 20px; background: #16213e; border-bottom: 1px solid #0f3460; display: flex; align-items: center; justify-content: space-between; }
        #mascot { color: #4ecca3; font-family: 'Courier New', monospace; font-size: 10px; line-height: 1.2; white-space: pre; text-align: left; }
        .controls { display: flex; gap: 8px; align-items: center; }
        select { padding: 6px 10px; background: #1a1a2e; color: #4ecca3; border: 1px solid #4ecca3; border-radius: 6px; font-size: 0.85em; cursor: pointer; outline: none; }
        select option { background: #1a1a2e; color: #eee; }
        .label { font-size: 0.7em; color: #888; text-transform: uppercase; }
        #chat { flex: 1; overflow-y: auto; padding: 20px; }
        .msg { margin-bottom: 16px; max-width: 80%; padding: 12px 16px; border-radius: 12px; line-height: 1.5; white-space: pre-wrap; word-wrap: break-word; }
        .user { background: #0f3460; margin-left: auto; border-bottom-right-radius: 4px; }
        .assistant { background: #1a1a2e; border: 1px solid #333; border-bottom-left-radius: 4px; }
        #input-area { padding: 16px 20px; background: #16213e; border-top: 1px solid #0f3460; display: flex; gap: 10px; }
        #input { flex: 1; padding: 12px 16px; border-radius: 8px; border: 1px solid #333; background: #1a1a2e; color: #eee; font-size: 1em; outline: none; }
        #input:focus { border-color: #4ecca3; }
        #send { padding: 12px 24px; background: #4ecca3; color: #1a1a2e; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; }
        #send:hover { background: #3dbb94; }
        .typing { color: #4ecca3; font-style: italic; }
        .system-msg { color: #4ecca3; font-style: italic; text-align: center; margin: 8px 0; font-size: 0.9em; }
    </style>
</head>
<body>
    <div id="header">
        <pre id="mascot">╔═══╗
║■ ■║ Chatty
║ ▽ ║ Your Friendly Assistant
╚╦═╦╝/</pre>
        <div class="controls">
            <div>
                <div class="label">Model</div>
                <select id="model-select" onchange="switchModel(this.value)"></select>
            </div>
            <div>
                <div class="label">Knowledge</div>
                <select id="knowledge-select" onchange="switchKnowledge(this.value)">
                    <option value="general">General</option>
                    <option value="local">Local Only</option>
                    <option value="hybrid">Hybrid</option>
                </select>
            </div>
        </div>
    </div>
    <div id="chat"></div>
    <div id="input-area">
        <input id="input" placeholder="Ask anything... (/index path to add files, /search, /read, /run)" autofocus>
        <button id="send" onclick="send()">Send</button>
    </div>
    <script>
        const chat = document.getElementById('chat');
        const input = document.getElementById('input');
        const modelSelect = document.getElementById('model-select');
        const knowledgeSelect = document.getElementById('knowledge-select');

        fetch('/models').then(r => r.json()).then(data => {
            modelSelect.innerHTML = '';
            data.models.forEach(m => {
                const opt = document.createElement('option');
                opt.value = m.key;
                opt.textContent = m.name;
                if (m.active) opt.selected = true;
                modelSelect.appendChild(opt);
            });
        });

        fetch('/knowledge-mode').then(r => r.json()).then(data => {
            knowledgeSelect.value = data.mode;
        });

        input.addEventListener('keydown', e => { if (e.key === 'Enter') send(); });

        function addMsg(role, text) {
            const div = document.createElement('div');
            div.className = 'msg ' + role;
            div.textContent = text;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
            return div;
        }

        function addSystem(text) {
            const div = document.createElement('div');
            div.className = 'system-msg';
            div.textContent = text;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }

        function switchModel(key) {
            fetch('/switch-model', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({model: key})
            }).then(r => r.json()).then(data => {
                addSystem('Model: ' + data.name);
            });
        }

        function switchKnowledge(mode) {
            fetch('/switch-knowledge', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({mode: mode})
            }).then(r => r.json()).then(data => {
                addSystem('Knowledge: ' + data.mode);
            });
        }

        async function send() {
            const text = input.value.trim();
            if (!text) return;
            input.value = '';
            addMsg('user', text);

            const div = addMsg('assistant', '');
            div.classList.add('typing');
            div.textContent = 'Thinking...';

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text})
                });
                const data = await res.json();
                div.classList.remove('typing');
                div.textContent = data.response;
            } catch(e) {
                div.classList.remove('typing');
                div.textContent = 'Error: ' + e.message;
            }
        }
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/models")
def get_models():
    model_list = [{"key": k, "name": v["name"], "active": k == current_model} for k, v in MODELS.items()]
    return jsonify({"models": model_list})


@app.route("/knowledge-mode")
def get_knowledge_mode():
    return jsonify({"mode": knowledge_mode})


@app.route("/switch-model", methods=["POST"])
def switch_model():
    global current_model
    data = request.json
    key = data.get("model")
    if key in MODELS:
        current_model = key
        return jsonify({"name": MODELS[key]["name"]})
    return jsonify({"error": "Unknown model"}), 400


@app.route("/switch-knowledge", methods=["POST"])
def switch_knowledge():
    global knowledge_mode
    data = request.json
    mode = data.get("mode")
    if mode in ("general", "local", "hybrid"):
        knowledge_mode = mode
        return jsonify({"mode": mode})
    return jsonify({"error": "Unknown mode"}), 400


@app.route("/chat", methods=["POST"])
def chat_endpoint():
    global messages, current_model, fallback_model, knowledge_mode
    data = request.json
    user_msg = data.get("message", "")

    # Handle /index command
    if user_msg.startswith("/index "):
        path = user_msg[7:].strip()
        if path == "list":
            try:
                info = list_indexed()
                return jsonify({"response": f"Indexed: {info['count']} chunks from {len(info['sources'])} files"})
            except Exception as e:
                return jsonify({"response": f"Error: {e}"})
        elif path == "clear":
            try:
                clear_index()
                return jsonify({"response": "Index cleared."})
            except Exception as e:
                return jsonify({"response": f"Error: {e}"})
        else:
            try:
                p = Path(path)
                if p.is_dir():
                    stats = index_folder(path)
                    return jsonify({"response": f"Indexed {stats['files']} files ({stats['chunks']} chunks)"})
                elif p.is_file():
                    n = index_file(path)
                    return jsonify({"response": f"Indexed {p.name} ({n} chunks)"})
                else:
                    return jsonify({"response": f"Path not found: {path}"})
            except Exception as e:
                return jsonify({"response": f"Error: {e}"})

    # Handle other commands
    if user_msg.startswith("/search "):
        query = user_msg[8:]
        results = web_search(query)
        messages.append({"role": "user", "content": f"Search results for '{query}':\n{results}\nSummarize."})
    elif user_msg.startswith("/read "):
        path = user_msg[6:]
        content = read_file(path)
        messages.append({"role": "user", "content": f"File `{path}`:\n```\n{content}\n```\nAnalyze."})
    elif user_msg.startswith("/run "):
        cmd = user_msg[5:]
        output = run_command(cmd)
        messages.append({"role": "user", "content": f"Command `{cmd}` output:\n```\n{output}\n```\nAnalyze."})
    elif user_msg == "/clear":
        messages.clear()
        return jsonify({"response": "Conversation cleared."})
    else:
        messages.append({"role": "user", "content": user_msg})

    # Add RAG context if in local/hybrid mode
    augmented = messages.copy()
    if knowledge_mode in ("local", "hybrid") and messages:
        last_msg = messages[-1]["content"]
        rag_context = get_context_for_query(last_msg)
        if rag_context:
            prefix = "[Local Knowledge"
            if knowledge_mode == "local":
                prefix += " - answer ONLY from this data"
            prefix += "]:\n\n"
            augmented = [{"role": "user", "content": prefix + rag_context}] + augmented

    # Get response with fallback
    try:
        response = call_model(current_model, augmented)
    except Exception as e:
        try:
            response = call_model(fallback_model, augmented)
        except Exception as e2:
            response = f"Both providers failed:\n{current_model}: {e}\n{fallback_model}: {e2}"

    messages.append({"role": "assistant", "content": response})
    return jsonify({"response": response})


if __name__ == "__main__":
    print("Starting Chatty-My-Agent Web UI at http://localhost:5000")
    app.run(debug=False, port=5000)
