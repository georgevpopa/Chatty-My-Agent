"""Web UI for Chatty-My-Agent using Flask."""
import os
import json
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify, Response
from dotenv import load_dotenv

load_dotenv()

from llm import call_gemini, call_groq, call_gemini_stream, call_groq_stream
from tools import read_file, run_command, web_search

app = Flask(__name__)
messages = []
use_gemini = True

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Chatty-My-Agent</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #1a1a2e; color: #eee; height: 100vh; display: flex; flex-direction: column; }
        #header { padding: 12px 20px; background: #16213e; border-bottom: 1px solid #0f3460; }
        #header h1 { font-size: 1.2em; color: #4ecca3; }
        #chat { flex: 1; overflow-y: auto; padding: 20px; }
        .msg { margin-bottom: 16px; max-width: 80%; padding: 12px 16px; border-radius: 12px; line-height: 1.5; white-space: pre-wrap; }
        .msg code { background: #0f3460; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }
        .msg pre { background: #0f3460; padding: 12px; border-radius: 8px; overflow-x: auto; margin: 8px 0; }
        .user { background: #0f3460; margin-left: auto; border-bottom-right-radius: 4px; }
        .assistant { background: #1a1a2e; border: 1px solid #333; border-bottom-left-radius: 4px; }
        #input-area { padding: 16px 20px; background: #16213e; border-top: 1px solid #0f3460; display: flex; gap: 10px; }
        #input { flex: 1; padding: 12px 16px; border-radius: 8px; border: 1px solid #333; background: #1a1a2e; color: #eee; font-size: 1em; outline: none; }
        #input:focus { border-color: #4ecca3; }
        #send { padding: 12px 24px; background: #4ecca3; color: #1a1a2e; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; }
        #send:hover { background: #3dbb94; }
        .typing { color: #4ecca3; font-style: italic; }
    </style>
</head>
<body>
    <div id="header"><h1>🤖 Chatty-My-Agent</h1></div>
    <div id="chat"></div>
    <div id="input-area">
        <input id="input" placeholder="Ask anything... (or use /commands)" autofocus>
        <button id="send" onclick="send()">Send</button>
    </div>
    <script>
        const chat = document.getElementById('chat');
        const input = document.getElementById('input');

        input.addEventListener('keydown', e => { if (e.key === 'Enter') send(); });

        function addMsg(role, text) {
            const div = document.createElement('div');
            div.className = 'msg ' + role;
            div.textContent = text;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
            return div;
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


@app.route("/chat", methods=["POST"])
def chat():
    global messages, use_gemini
    data = request.json
    user_msg = data.get("message", "")

    # Handle commands
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
    elif user_msg == "/model":
        use_gemini = not use_gemini
        return jsonify({"response": f"Switched to {'Gemini' if use_gemini else 'Groq'}"})
    elif user_msg == "/clear":
        messages.clear()
        return jsonify({"response": "Conversation cleared."})
    else:
        messages.append({"role": "user", "content": user_msg})

    # Get response
    try:
        if use_gemini:
            response = call_gemini(messages)
        else:
            response = call_groq(messages)
    except Exception as e:
        try:
            response = call_groq(messages) if use_gemini else call_gemini(messages)
        except Exception as e2:
            response = f"Both providers failed: {e} / {e2}"

    messages.append({"role": "assistant", "content": response})
    return jsonify({"response": response})


if __name__ == "__main__":
    print("Starting Chatty-My-Agent Web UI at http://localhost:5000")
    app.run(debug=False, port=5000)
