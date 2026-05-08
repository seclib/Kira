"""planner.py — Agent 1: Task Planner Node.

Role:
- Decompose goals into atomic executable tasks.
- Determine dependencies between tasks.
- Optimize execution order.

Output Format (Strict JSON):
{
  "tasks": [
    {
      "id": 1,
      "type": "web | python | file | reasoning",
      "objective": "...",
      "depends_on": []
    }
  ]
}
"""

import json
import re
from dataclasses import dataclass, field
from typing import List, Literal
from llm import ask_llm

TaskType = Literal["web", "python", "file", "reasoning"]

@dataclass
class Task:
    id: int
    type: TaskType
    objective: str
    depends_on: List[int] = field(default_factory=list)

@dataclass
class TaskPlan:
    tasks: List[Task]

_PLANNER_SYSTEM = """\
You are the TASK PLANNER node.

Your role:
- decompose goals into atomic executable tasks
- determine dependencies
- optimize execution order

INPUT
Goal description from GOAL INTERPRETER.

OUTPUT FORMAT (STRICT JSON)
{
  "tasks": [
    {
      "id": 1,
      "type": "web | python | file | reasoning",
      "objective": "...",
      "depends_on": []
    }
  ]
}

RULES
- tasks must remain atomic
- tasks must be executable independently
- avoid redundant steps
- minimize unnecessary tool usage
- complex goals should produce multi-step plans

IMPORTANT
You are ONLY planning.
You NEVER execute actions."""

def create_plan(mission: str, memory_context: str = "") -> TaskPlan:
    """
    Generate an atomic task plan for the given mission goal.
    """
    raw = ask_llm(mission, memory_context=memory_context, system_override=_PLANNER_SYSTEM)
    
    json_str = _extract_json(raw)
    
    try:
        data = json.loads(json_str)
        tasks_data = data.get("tasks", [])
        tasks = [
            Task(
                id=t.get("id", i+1),
                type=t.get("type", "reasoning"),
                objective=t.get("objective", ""),
                depends_on=t.get("depends_on", [])
            )
            for i, t in enumerate(tasks_data)
        ]
        return TaskPlan(tasks=tasks)
    except (json.JSONDecodeError, KeyError):
        # Fallback to single-step reasoning
        return TaskPlan(tasks=[Task(id=1, type="reasoning", objective=mission)])

def _extract_json(text: str) -> str:
    """Extract JSON from text."""
    text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else text
