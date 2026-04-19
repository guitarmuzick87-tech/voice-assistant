import json
import urllib.request
from config import (
    LLM_PROVIDER, LLM_MODEL, SYSTEM_PROMPT,
    OLLAMA_IP, OLLAMA_PORT,
    OPENAI_API_KEY, OPENAI_MODEL,
    ANTHROPIC_API_KEY, ANTHROPIC_MODEL
)


def query_llm(user_text: str) -> str:
    if LLM_PROVIDER == "ollama":
        return _query_ollama(user_text)
    elif LLM_PROVIDER == "openai":
        return _query_openai(user_text)
    elif LLM_PROVIDER == "anthropic":
        return _query_anthropic(user_text)
    return f"Unknown LLM provider: {LLM_PROVIDER}"


def _query_ollama(user_text: str) -> str:
    try:
        payload = json.dumps({
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            "stream": False
        }).encode()
        req = urllib.request.Request(
            f"http://{OLLAMA_IP}:{OLLAMA_PORT}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())["message"]["content"].strip()
    except Exception as e:
        print(f"[Ollama Error]: {e}")
        return "Sorry, I couldn't reach the language model."


def _query_openai(user_text: str) -> str:
    try:
        payload = json.dumps({
            "model": OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ]
        }).encode()
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[OpenAI Error]: {e}")
        return "Sorry, I couldn't reach OpenAI."


def _query_anthropic(user_text: str) -> str:
    try:
        payload = json.dumps({
            "model": ANTHROPIC_MODEL,
            "max_tokens": 1024,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_text}]
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())["content"][0]["text"].strip()
    except Exception as e:
        print(f"[Anthropic Error]: {e}")
        return "Sorry, I couldn't reach Anthropic."