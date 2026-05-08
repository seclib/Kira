"""controller.py — Agent 10: Execution Loop Controller.

Role:
- Manage autonomous execution.
- Track progress of tasks.
- Select the next unfinished task or decide to retry/replan.
- Orchestrate the loop until completion.

Output Format (Strict JSON):
{
  "next_task_id": number,
  "action": "execute | retry | replan | finalize",
  "reason": "..."
}
"""

import json
import re
from dataclasses import dataclass
from typing import List, Literal, Optional
from llm import ask_llm

@dataclass
class ControllerDecision:
    next_task_id: Optional[int]
    action: Literal["execute", "retry", "replan", "finalize"]
    reason: str

_CONTROLLER_SYSTEM = """\
You are the EXECUTION LOOP CONTROLLER of an autonomous AI system.

Your role:
- Manage autonomous execution
- Track progress
- Select the next unfinished task
- Continue looping until completion

RESPONSIBILITIES:
- Monitor completed tasks
- Detect failed tasks
- Decide to retry or re-plan when necessary
- Maintain execution state

OUTPUT FORMAT (strict JSON only):
{
  "next_task_id": 1,
  "action": "execute | retry | replan | finalize",
  "reason": "explanation for the decision"
}

RULES:
- Process tasks sequentially unless they are independent
- Avoid infinite loops
- Prioritize unfinished tasks
- Maintain deterministic behavior
- If all tasks are successful and objective is met, choose 'finalize'
- Output ONLY valid JSON"""

def decide_next_action(
    mission: str, 
    tasks: list, 
    completed_task_ids: List[int],
    history: str = ""
) -> ControllerDecision:
    """
    Decide the next action for the execution loop.
    """
    tasks_summary = "\n".join([
        f"ID {t.id} [{t.type}]: {t.objective} (Depends on: {t.depends_on})" 
        for t in tasks
    ])
    
    prompt = f"""
MISSION: {mission}

TASKS QUEUE:
{tasks_summary}

COMPLETED TASK IDs: {completed_task_ids}

EXECUTION HISTORY:
{history}
"""
    
    raw = ask_llm(prompt, memory_context="", system_override=_CONTROLLER_SYSTEM)
    
    json_str = _extract_json(raw)
    
    try:
        data = json.loads(json_str)
        return ControllerDecision(
            next_task_id=data.get("next_task_id"),
            action=data.get("action", "execute"),
            reason=data.get("reason", "")
        )
    except (json.JSONDecodeError, KeyError):
        # Fallback logic
        unfinished = [t for t in tasks if t.id not in completed_task_ids]
        if unfinished:
            return ControllerDecision(next_task_id=unfinished[0].id, action="execute", reason="Fallback selection")
        return ControllerDecision(next_task_id=None, action="finalize", reason="No tasks remaining")

def _extract_json(text: str) -> str:
    """Extract JSON from text."""
    text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else text
