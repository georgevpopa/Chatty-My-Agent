"""Voice input/output for Chatty-My-Agent."""
import os
import subprocess
from dotenv import load_dotenv

load_dotenv()


def speech_to_text() -> str:
    """Record from microphone and transcribe using Groq Whisper."""
    import sounddevice as sd
    import numpy as np
    import tempfile
    import wave

    print("🎤 Listening... (speak now, 5 seconds)")
    duration = 5
    sample_rate = 16000
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
    sd.wait()
    print("✓ Got it.")

    # Save to temp wav
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    with wave.open(tmp.name, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())

    # Transcribe with Groq Whisper
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    with open(tmp.name, "rb") as f:
        transcription = client.audio.transcriptions.create(
            file=(tmp.name, f.read()),
            model="whisper-large-v3",
        )
    os.unlink(tmp.name)
    return transcription.text


def text_to_speech(text: str):
    """Speak text using Windows built-in TTS."""
    # Use PowerShell SAPI
    escaped = text.replace("'", "''").replace('"', '`"')[:500]
    cmd = f'powershell -command "Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Speak(\'{escaped}\')"'
    subprocess.run(cmd, shell=True, capture_output=True)
