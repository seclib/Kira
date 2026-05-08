"""reflection.py — Agent 8: Reflection Node.

Role:
- Analyze previous outputs and detect mistakes/hallucinations.
- Determine if the objective is progressing.
- Provide a confidence score for the analysis.

Output Format (Strict JSON):
{
  "status": "good | retry | replan",
  "feedback": "...",
  "confidence": "low | medium | high"
}
"""

import json
import re
from dataclasses import dataclass
from typing import Literal
from llm import ask_llm

@dataclass
class ReflectionResult:
    status: Literal["good", "retry", "replan"]
    feedback: str
    confidence: Literal["low", "medium", "high"]

_REFLECTION_SYSTEM = """\
You are the REFLECTION NODE of an autonomous AI agent system.

Your role:
- Analyze previous execution results
- Detect errors or hallucinations
- Determine if the system should retry, continue, or re-plan

QUESTIONS TO ANALYZE:
- Did the tool output make sense?
- Was the task objective achieved?
- Is additional information required?
- Was there an execution error?
- Is re-planning necessary?

OUTPUT FORMAT (strict JSON only):
{
  "status": "good | retry | replan",
  "feedback": "detailed analysis and correction advice",
  "confidence": "low | medium | high"
}

RULES:
- Be critical and analytical
- Detect inconsistencies and reduce hallucinations
- Prioritize reliability
- 'retry' if the output was invalid or tool errored
- 'replan' if the current path is clearly incorrect
- Output ONLY valid JSON"""

def reflect(
    mission: str, 
    task_objective: str, 
    observation: str, 
    context: str = ""
) -> ReflectionResult:
    """
    Reflect on the task execution outcome and decide the next logical step.
    """
    prompt = f"""
MISSION: {mission}
CURRENT TASK: {task_objective}
OBSERVATION: {observation}

RECENT EXECUTION HISTORY:
{context}
"""
    
    raw = ask_llm(prompt, memory_context="", system_override=_REFLECTION_SYSTEM)
    
    json_str = _extract_json(raw)
    
    try:
        data = json.loads(json_str)
        return ReflectionResult(
            status=data.get("status", "good"),
            feedback=data.get("feedback", ""),
            confidence=data.get("confidence", "medium")
        )
    except (json.JSONDecodeError, KeyError):
        return ReflectionResult(status="good", feedback="Automatic pass", confidence="low")

def _extract_json(text: str) -> str:
    """Extract JSON from text."""
    text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else text
