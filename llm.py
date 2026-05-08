"""llm.py — Ollama LLM interface for Kira."""

import requests
from config import OLLAMA_HOST, OLLAMA_MODEL, SYSTEM_PROMPT


def ask_llm(user_input: str, memory_context: str = "", system_override: str | None = None) -> str:
    """Send a prompt to Ollama and return the raw response string."""

    context_block = ""
    if memory_context.strip():
        context_block = f"\n\n# 🧠 MEMORY CONTEXT (recent interactions)\n{memory_context}\n"

    full_prompt = f"{context_block}\n# USER REQUEST\n{user_input}"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": full_prompt,
        "system": system_override or SYSTEM_PROMPT,
        "stream": False,
    }

    try:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        return "ERROR: Cannot connect to Ollama. Is it running? Run: ollama serve"
    except requests.exceptions.Timeout:
        return "ERROR: Ollama request timed out."
    except Exception as e:
        return f"ERROR: {e}"
