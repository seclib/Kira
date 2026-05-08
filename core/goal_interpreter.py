"""goal_interpreter.py — Agent 7: Goal Interpreter Node.

Responsibility:
- Understand the user's real objective.
- Transform vague requests into precise executable goals.
- Determine if autonomous looping is necessary.

Output Format (Strict JSON):
{
  "goal": "...",
  "difficulty": "low | medium | high",
  "requires_autonomy": true | false,
  "estimated_steps": number
}
"""

import json
import re
from dataclasses import dataclass
from llm import ask_llm

@dataclass
class Mission:
    goal: str
    difficulty: str
    requires_autonomy: bool
    estimated_steps: int

_GOAL_SYSTEM = """\
You are the GOAL INTERPRETER node of an autonomous AI system.

Your responsibility:
- Understand the user's real objective
- Transform vague requests into precise executable goals
- Determine if autonomous looping is necessary

OUTPUT FORMAT (strict JSON only):
{
  "goal": "precise executable mission statement",
  "difficulty": "low | medium | high",
  "requires_autonomy": true | false,
  "estimated_steps": 5
}

RULES:
- Do NOT solve the problem
- Do NOT use tools
- Only clarify the mission
- Infer hidden objectives if obvious
- Be concise and structured
- Output ONLY valid JSON

EXAMPLE:
User: "Create me a Python scraper"
Output:
{
  "goal": "Build a Python web scraper capable of extracting structured data from websites",
  "difficulty": "medium",
  "requires_autonomy": true,
  "estimated_steps": 6
}"""

def interpret_goal(user_input: str) -> Mission:
    """
    Interpret the user input into a precise mission statement.
    """
    raw = ask_llm(user_input, memory_context="", system_override=_GOAL_SYSTEM)
    
    json_str = _extract_json(raw)
    
    try:
        data = json.loads(json_str)
        return Mission(
            goal=data.get("goal", user_input),
            difficulty=data.get("difficulty", "medium"),
            requires_autonomy=bool(data.get("requires_autonomy", False)),
            estimated_steps=int(data.get("estimated_steps", 5))
        )
    except (json.JSONDecodeError, KeyError, ValueError):
        # Fallback to defaults
        return Mission(
            goal=user_input, 
            difficulty="medium", 
            requires_autonomy=False, 
            estimated_steps=3
        )

def _extract_json(text: str) -> str:
    """Extract JSON from text."""
    text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else text
