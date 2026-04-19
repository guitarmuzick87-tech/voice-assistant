import os

# ─────────────────────────────────────────────
# DEBUG FLAGS — set these to skip pipeline steps
# ─────────────────────────────────────────────
DEBUG_SKIP_WAKE_WORD = False      # skip wake word, jump straight to recording
DEBUG_SKIP_RECORDING = False      # skip mic recording, use DEBUG_FAKE_TRANSCRIPT
DEBUG_SKIP_LLM = False            # skip LLM, use DEBUG_FAKE_RESPONSE
DEBUG_SKIP_TTS = False            # skip Piper, just print response
DEBUG_FAKE_TRANSCRIPT = "what is the capital of France"
DEBUG_FAKE_RESPONSE = "The capital of France is Paris."


DEBUG_FAKE_TRANSCRIPT = "what is the capital of France"
# ─────────────────────────────────────────────
# PERSONALITY
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """You are Jarvis, a helpful and concise voice assistant running on a Raspberry Pi.
You respond in clear, natural spoken English — no markdown, no bullet points, no code blocks.
Keep responses brief and conversational since they will be spoken aloud.
If you don't know something, say so simply."""

# ─────────────────────────────────────────────
# LLM
# ─────────────────────────────────────────────
LLM_PROVIDER = "ollama"           # "ollama" | "openai" | "anthropic"
LLM_MODEL = "gemma3:4b"
OLLAMA_IP = "127.0.0.1"
OLLAMA_PORT = 11434
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4o-mini"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = "claude-sonnet-4-5"

# ─────────────────────────────────────────────
# SERVICES
# ─────────────────────────────────────────────
VOSK_IP = "127.0.0.1"
VOSK_PORT = 10300
WAKE_IP = "127.0.0.1"
WAKE_PORT = 10400
PIPER_IP = "127.0.0.1"
PIPER_PORT = 10200

# ─────────────────────────────────────────────
# AUDIO HARDWARE
# ─────────────────────────────────────────────
SAMPLE_RATE = 44100

WIDTH = 2
CHUNK_BYTES = 3200
MIC_DEVICE_INDEX = 0 #Change these per device
MIC_CHANNELS = 1 #Change these per device
SPEAKER_DEVICE_INDEX = 1 #Change these per dvice
SPEAKER_CHANNELS = 2 #Change these per device
SPEAKER_RATE = 44100
SILENCE_TIMEOUT = 5.0
SILENCE_THRESHOLD = 500
MAX_COMMAND_SECONDS = 15
BEEP_FILE = "beep.wav"
WAKE_WORD = "hey_jarvis"