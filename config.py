import os
from dotenv import load_dotenv

load_dotenv()  # loads .env file if present, silently ignores if missing

# ─────────────────────────────────────────────
# DEBUG FLAGS
# ─────────────────────────────────────────────
DEBUG_SKIP_WAKE_WORD  = os.environ.get("DEBUG_SKIP_WAKE_WORD",  "false").lower() == "true"
DEBUG_SKIP_RECORDING  = os.environ.get("DEBUG_SKIP_RECORDING",  "false").lower() == "true"
DEBUG_SKIP_LLM        = os.environ.get("DEBUG_SKIP_LLM",        "false").lower() == "true"
DEBUG_SKIP_TTS        = os.environ.get("DEBUG_SKIP_TTS",        "false").lower() == "true"
DEBUG_FAKE_TRANSCRIPT = os.environ.get("DEBUG_FAKE_TRANSCRIPT", "what is the capital of France")
DEBUG_FAKE_RESPONSE   = os.environ.get("DEBUG_FAKE_RESPONSE",   "The capital of France is Paris.")

# ─────────────────────────────────────────────
# PERSONALITY
# ─────────────────────────────────────────────
WAKE_RESPONSE      = os.environ.get("WAKE_RESPONSE",      "Yes, I'm listening.")
INTERRUPT_RESPONSE = os.environ.get("INTERRUPT_RESPONSE", "Okay, stopping.")
SYSTEM_PROMPT      = os.environ.get("SYSTEM_PROMPT", (
    "You are Jarvis, a helpful and concise voice assistant running on a Raspberry Pi. "
    "You respond in clear, natural spoken English — no markdown, no bullet points, no code blocks. "
    "Keep responses brief and conversational since they will be spoken aloud. "
    "If you don't know something, say so simply."
))

# ─────────────────────────────────────────────
# LLM
# ─────────────────────────────────────────────
LLM_PROVIDER     = os.environ.get("LLM_PROVIDER",     "ollama")   # ollama | openai | anthropic
LLM_MODEL        = os.environ.get("LLM_MODEL",        "gemma3:4b:cloud")
OLLAMA_IP        = os.environ.get("OLLAMA_IP",        "127.0.0.1")
OLLAMA_PORT      = int(os.environ.get("OLLAMA_PORT",  "11434"))
OPENAI_API_KEY   = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL     = os.environ.get("OPENAI_MODEL",     "gpt-4o-mini")
ANTHROPIC_API_KEY  = os.environ.get("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL    = os.environ.get("ANTHROPIC_MODEL",    "claude-sonnet-4-5")

# ─────────────────────────────────────────────
# SERVICES
# ─────────────────────────────────────────────
VOSK_IP    = os.environ.get("VOSK_IP",    "127.0.0.1")
VOSK_PORT  = int(os.environ.get("VOSK_PORT",  "10300"))
WAKE_IP    = os.environ.get("WAKE_IP",    "127.0.0.1")
WAKE_PORT  = int(os.environ.get("WAKE_PORT",  "10400"))
PIPER_IP   = os.environ.get("PIPER_IP",   "127.0.0.1")
PIPER_PORT = int(os.environ.get("PIPER_PORT", "10200"))

# ─────────────────────────────────────────────
# AUDIO HARDWARE
# ─────────────────────────────────────────────
MIC_DEVICE_INDEX    = int(os.environ.get("MIC_DEVICE_INDEX",    "0"))
MIC_CHANNELS        = int(os.environ.get("MIC_CHANNELS",        "1"))
SAMPLE_RATE         = int(os.environ.get("SAMPLE_RATE",         "48000"))
SPEAKER_DEVICE_INDEX = int(os.environ.get("SPEAKER_DEVICE_INDEX", "1"))
SPEAKER_CHANNELS    = int(os.environ.get("SPEAKER_CHANNELS",    "2"))
SPEAKER_RATE        = int(os.environ.get("SPEAKER_RATE",        "44100"))
WIDTH               = 2   # always 16-bit, not worth overriding
CHUNK_BYTES         = int(os.environ.get("CHUNK_BYTES",         "3200"))
SILENCE_TIMEOUT     = float(os.environ.get("SILENCE_TIMEOUT",   "2.0"))
SILENCE_THRESHOLD   = int(os.environ.get("SILENCE_THRESHOLD",   "500"))
MAX_COMMAND_SECONDS = int(os.environ.get("MAX_COMMAND_SECONDS", "15"))
BEEP_FILE           = os.environ.get("BEEP_FILE", "beep.wav")
WAKE_WORD           = os.environ.get("WAKE_WORD", "hey_jarvis")

# ─────────────────────────────────────────────
# INTERRUPT
# ─────────────────────────────────────────────
INTERRUPT_ENABLED      = os.environ.get("INTERRUPT_ENABLED",      "true").lower() == "true"
INTERRUPT_WORD         = os.environ.get("INTERRUPT_WORD",         "stop")
INTERRUPT_LISTEN_DELAY = float(os.environ.get("INTERRUPT_LISTEN_DELAY", "2.0"))