"""intent_parser.py — Agent 0: Intent classification front door.

Runs BEFORE the LLM reasoner. Classifies intent and complexity
so the pipeline can route efficiently.

Output is strict JSON:
{
  "intent":     "question | task | computation | research | multi_step",
  "needs_tools": true | false,
  "topics":     ["..."],
  "complexity": "low | medium | high"
}
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Literal

from llm import ask_llm


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

IntentType = Literal["question", "task", "computation", "research", "multi_step"]
Complexity = Literal["low", "medium", "high"]


@dataclass
class Intent:
    intent: IntentType = "question"
    needs_tools: bool = False
    topics: list[str] = field(default_factory=list)
    complexity: Complexity = "low"

    def is_simple(self) -> bool:
        """True when a direct LLM answer is sufficient — no tools, low complexity."""
        return not self.needs_tools and self.complexity == "low"

    def skip_synthesis(self) -> bool:
        """True when assembler synthesis can be skipped (saves one LLM call)."""
        return self.is_simple()


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

_INTENT_SYSTEM = """\
You are the INTENT PARSER of an AI agent system.

Your job:
- Understand the user request
- Classify the intent
- Detect complexity

OUTPUT FORMAT (strict JSON only, no markdown, no explanation):
{
  "intent": "question | task | computation | research | multi_step",
  "needs_tools": true | false,
  "topics": ["..."],
  "complexity": "low | medium | high"
}

RULES:
- Do NOT solve the task
- Do NOT call tools
- Only analyze intent
- Be precise and minimal
- Output ONLY valid JSON"""


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def parse_intent(user_input: str) -> Intent:
    """
    Classify the user's intent. Returns an Intent dataclass.
    Falls back to a safe default on parse failure.
    """
    raw = ask_llm(user_input, memory_context="", system_override=_INTENT_SYSTEM)

    # Extract JSON from the response (handles markdown fences)
    json_str = _extract_json(raw)

    try:
        data = json.loads(json_str)
        return Intent(
            intent=data.get("intent", "question"),
            needs_tools=bool(data.get("needs_tools", False)),
            topics=data.get("topics", []),
            complexity=data.get("complexity", "low"),
        )
    except (json.JSONDecodeError, KeyError):
        # Safe fallback — treat as a simple question
        return Intent(intent="question", needs_tools=False, topics=[], complexity="low")


def _extract_json(text: str) -> str:
    """Strip markdown fences and extract the first JSON object."""
    text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else text
