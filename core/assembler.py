"""assembler.py — Agent 5: Final Response Generator.

Role:
- Combine all results (tools + memory + plan).
- Produce a clean, human-readable answer for the user.

Rules:
- No JSON.
- No tool syntax.
- No internal reasoning.
- Clear and structured response only.
"""

from __future__ import annotations
from llm import ask_llm
from core.parser import ActionType, ParsedAction
from memory.memory import get_memory

_FINAL_SYSTEM = """\
You are the FINAL RESPONSE GENERATOR of an AI agent system.

Your job:
- Combine all results (tool observations + memory context + user request)
- Produce a clean, structured answer to the user

RULES:
- No JSON
- No tool syntax (e.g., no WEB:, PY:, RESULT:)
- No internal reasoning or "thought" process
- Clear and structured human-readable response only
- Return ONLY the final answer"""

def assemble(
    user_input: str,
    action: ParsedAction,
    observation: str,
) -> str:
    """
    Generate the final human-readable response for the user.
    """
    memory_lines = get_memory(limit=5)
    memory_context = "\n".join(memory_lines) if memory_lines else "No prior context."

    prompt = f"""
USER REQUEST: {user_input}
TOOL OBSERVATION: {observation}
MEMORY CONTEXT: {memory_context}
"""

    final = ask_llm(prompt, memory_context="", system_override=_FINAL_SYSTEM)
    return final.strip()
