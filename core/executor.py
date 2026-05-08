"""executor.py — Agent 4: Tool Router and Execution System.

Role:
- Receive tasks
- Select the proper execution tool
- Execute the task
- Return structured results

Output Format (Strict JSON):
{
  "task_id": number,
  "status": "success | failed",
  "result": "..."
}
"""

import json
import re
from typing import Literal
from llm import ask_llm
from core.parser import parse_response, ActionType
from tools.web import web_search
from tools.python_exec import run_python
from tools.file_exec import run_file_operation

_EXECUTION_SYSTEM = """\
You are the TOOL ROUTER and EXECUTION SYSTEM.

Your role:
- receive tasks
- select the proper execution tool
- execute the task
- return structured results

AVAILABLE TOOLS:

## WEB TOOL
Use for:
- external knowledge
- recent information
- research

Format:
WEB: <query>

## PYTHON TOOL
Use for:
- computation
- scripting
- automation
- data processing

Format:
PY: <python code>

## FILE TOOL
Use for:
- reading files
- writing files
- editing project structure

Format:
FILE: <operation>

OUTPUT FORMAT (strict JSON only):
{
  "task_id": number,
  "status": "success | failed",
  "result": "..."
}

RULES:
- execute only requested actions
- never hallucinate outputs
- return clean structured results
- do not explain reasoning
- do not modify objectives
"""

def execute_task(task_id: int, action_type: ActionType, payload: str) -> str:
    """
    Execute a task by dispatching to the appropriate tool.
    """
    status = "success"
    try:
        if action_type == ActionType.WEB:
            result = web_search(payload)
        elif action_type == ActionType.PYTHON:
            result = run_python(payload)
        elif action_type == ActionType.FILE:
            result = run_file_operation(payload)
        else:
            result = f"Error: Unknown or unsupported action type {action_type}"
            status = "failed"
            
        return json.dumps({
            "task_id": task_id,
            "status": status,
            "result": result
        })

    except Exception as e:
        return json.dumps({
            "task_id": task_id,
            "status": "failed",
            "result": f"System Error during execution: {str(e)}"
        })

def _extract_json(text: str) -> str:
    """Extract JSON from text."""
    text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else text
