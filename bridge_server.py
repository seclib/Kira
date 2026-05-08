#!/usr/bin/env python3
"""bridge_server.py — JSON-RPC stdio bridge between Electron and Kira Core.

Reads line-delimited JSON-RPC requests from stdin.
Writes line-delimited JSON-RPC responses and notifications to stdout.
All agent logs are intercepted and emitted as notifications.

Protocol (line-delimited JSON, newline-terminated):

→ Request:
  {"jsonrpc":"2.0","method":"run_mission","params":{"input":"..."},"id":1}
  {"jsonrpc":"2.0","method":"cancel","params":{},"id":2}
  {"jsonrpc":"2.0","method":"get_memory","params":{},"id":3}
  {"jsonrpc":"2.0","method":"get_facts","params":{},"id":4}
  {"jsonrpc":"2.0","method":"clear_memory","params":{},"id":5}
  {"jsonrpc":"2.0","method":"clear_all","params":{},"id":6}
  {"jsonrpc":"2.0","method":"ollama_status","params":{},"id":7}

← Notifications (no id):
  {"jsonrpc":"2.0","method":"log","params":{"text":"...","agent":"planner","level":"info"}}
  {"jsonrpc":"2.0","method":"step","params":{"agent":"planner","status":"running"}}

← Response (with id):
  {"jsonrpc":"2.0","result":{"response":"..."},"id":1}
  {"jsonrpc":"2.0","error":{"code":-32000,"message":"..."},"id":1}
"""

import sys
import json
import threading
import io
import re

# Ensure stdout is in line-buffered mode for real-time streaming
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

# Add parent dir to path so kira-core modules are importable
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests as _requests

_cancel_flag = threading.Event()

# ── JSON-RPC helpers ──────────────────────────────────────────────────────────

def _write(obj: dict) -> None:
    """Write a JSON-RPC message to stdout."""
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + '\n')

def _notify(method: str, params: dict) -> None:
    _write({"jsonrpc": "2.0", "method": method, "params": params})

def _respond(id_: int, result: dict) -> None:
    _write({"jsonrpc": "2.0", "result": result, "id": id_})

def _error(id_: int, code: int, message: str) -> None:
    _write({"jsonrpc": "2.0", "error": {"code": code, "message": message}, "id": id_})

# ── Log interceptor ───────────────────────────────────────────────────────────

_AGENT_PATTERNS = {
    "[INTENT]": "intent_parser",
    "[MISSION]": "goal_interpreter",
    "[PLAN]": "planner",
    "[RE-PLAN]": "planner",
    "[CONTROL]": "controller",
    "[THINK]": "reasoner",
    "[REFLECT]": "reflection",
    "[DONE]": "termination",
    "[FINAL]": "assembler",
    "[success]": "executor",
    "[failed]": "executor",
}

def _detect_agent(text: str) -> str:
    for pattern, agent in _AGENT_PATTERNS.items():
        if pattern.upper() in text.upper():
            return agent
    return "system"

class _LogCapture:
    """Redirect stdout from agent loop into JSON-RPC notifications."""
    def __init__(self, real_stdout):
        self.real_stdout = real_stdout

    def write(self, text: str):
        text = text.strip()
        if text:
            agent = _detect_agent(text)
            _notify("log", {"text": text, "agent": agent, "level": "info"})
        # Don't write to real stdout (that's reserved for JSON-RPC)

    def flush(self):
        pass

# ── Handlers ──────────────────────────────────────────────────────────────────

def handle_run_mission(params: dict, id_: int) -> None:
    user_input = params.get("input", "").strip()
    if not user_input:
        _error(id_, -32602, "Missing 'input' parameter")
        return

    _cancel_flag.clear()

    # Intercept prints from the agent loop
    real_stdout = sys.stdout
    sys.stdout = _LogCapture(real_stdout)  # type: ignore

    try:
        from core.loop import agent
        result = agent(user_input)
        _respond(id_, {"response": result})
    except Exception as e:
        _error(id_, -32000, str(e))
    finally:
        sys.stdout = real_stdout


def handle_get_memory(id_: int) -> None:
    try:
        from memory.memory import get_memory
        turns = get_memory()
        _respond(id_, {"turns": turns})
    except Exception as e:
        _error(id_, -32000, str(e))


def handle_get_facts(id_: int) -> None:
    try:
        from memory.memory import get_facts
        facts = get_facts(50)
        _respond(id_, {"facts": facts})
    except Exception as e:
        _error(id_, -32000, str(e))


def handle_clear_memory(id_: int) -> None:
    try:
        from memory.memory import clear_memory
        clear_memory()
        _respond(id_, {"ok": True})
    except Exception as e:
        _error(id_, -32000, str(e))


def handle_clear_all(id_: int) -> None:
    try:
        from memory.memory import clear_all
        clear_all()
        _respond(id_, {"ok": True})
    except Exception as e:
        _error(id_, -32000, str(e))


def handle_ollama_status(id_: int) -> None:
    try:
        from config import OLLAMA_HOST
        resp = _requests.get(f"{OLLAMA_HOST}/api/version", timeout=3)
        resp.raise_for_status()
        _respond(id_, {"status": "online", "version": resp.json().get("version", "")})
    except Exception:
        _respond(id_, {"status": "offline"})


# ── Main loop ─────────────────────────────────────────────────────────────────

DISPATCH = {
    "run_mission": lambda p, i: threading.Thread(
        target=handle_run_mission, args=(p, i), daemon=True
    ).start(),
    "cancel": lambda _p, i: (_cancel_flag.set(), _respond(i, {"ok": True})),
    "get_memory": lambda _p, i: handle_get_memory(i),
    "get_facts": lambda _p, i: handle_get_facts(i),
    "clear_memory": lambda _p, i: handle_clear_memory(i),
    "clear_all": lambda _p, i: handle_clear_all(i),
    "ollama_status": lambda _p, i: handle_ollama_status(i),
}


def main():
    _notify("log", {"text": "Kira bridge server ready", "agent": "system", "level": "info"})

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            _write({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None})
            continue

        method = msg.get("method", "")
        params = msg.get("params", {})
        id_ = msg.get("id")

        handler = DISPATCH.get(method)
        if handler is None:
            _error(id_, -32601, f"Method not found: {method}")
            continue

        try:
            handler(params, id_)
        except Exception as e:
            _error(id_, -32000, str(e))


if __name__ == "__main__":
    main()
