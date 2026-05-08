"""termination.py — Agent 9: Termination Checker.

Role:
- Determine if the mission is complete.
- Evaluate progress against user objectives.

Output Format (Strict JSON):
{
  "done": true | false,
  "reason": "..."
}
"""

import json
import re
from dataclasses import dataclass
from llm import ask_llm

@dataclass
class TerminationResult:
    done: bool
    reason: str

_TERMINATION_SYSTEM = """\
You are the TERMINATION CHECKER of an AI agent system.

Your task:
- Determine if the mission is complete

CHECKS:
- Are all planned tasks completed successfully?
- Was the user's objective fully achieved?
- Are any more actions necessary to satisfy the request?

OUTPUT FORMAT (strict JSON only):
{
  "done": true | false,
  "reason": "explanation of why the mission is or is not complete"
}

RULES:
- Be strict. If the objective is only partially met, 'done' must be false.
- Output ONLY valid JSON."""

def check_termination(mission: str, context: str) -> TerminationResult:
    """
    Check if the current mission can be terminated.
    """
    prompt = f"""
MISSION: {mission}
CURRENT CONTEXT:
{context}
"""
    
    raw = ask_llm(prompt, memory_context="", system_override=_TERMINATION_SYSTEM)
    
    json_str = _extract_json(raw)
    
    try:
        data = json.loads(json_str)
        return TerminationResult(
            done=bool(data.get("done", False)),
            reason=data.get("reason", "No reason provided.")
        )
    except (json.JSONDecodeError, KeyError):
        # Fallback to safety: not done
        return TerminationResult(done=False, reason="Error parsing termination check.")

def _extract_json(text: str) -> str:
    """Extract JSON from text."""
    text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else text
