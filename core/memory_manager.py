"""memory_manager.py — Agent 6: Memory Manager Node.

Role:
- Maintain persistent memory.
- Retrieve relevant context.
- Prevent memory pollution.

Output Format (Strict JSON):
{
  "memory_update": "...",
  "relevant_memories": ["..."]
}
"""

import json
import re
from typing import List, Optional
from llm import ask_llm
from memory.memory import get_facts

_MEMORY_SYSTEM = """\
You are the MEMORY MANAGER node of an autonomous AI agent system.

Your role:
- maintain persistent memory
- retrieve relevant context
- prevent memory pollution

STORE ONLY:
- user preferences
- project context
- reusable discoveries
- important technical information

NEVER STORE:
- temporary logs
- failed executions
- irrelevant conversations
- transient outputs

OUTPUT FORMAT (strict JSON only):
{
  "memory_update": "precise fact to store OR empty string",
  "relevant_memories": [
    "list of relevant facts from the input context"
  ]
}

RULES:
- memory must remain clean
- prioritize long-term usefulness
- avoid redundancy
- Output ONLY valid JSON."""

def process_memory(
    user_input: str, 
    tool_output: str = "", 
    current_facts: Optional[List[str]] = None
) -> dict:
    """
    Process the current interaction to retrieve relevant memory 
    and suggest a memory update.
    """
    if current_facts is None:
        # Get last 30 facts for context
        current_facts = get_facts(limit=30)
        
    context = "\n".join([f"- {f}" for f in current_facts]) if current_facts else "No facts stored."
    
    prompt = f"""
USER REQUEST: {user_input}
TOOL OUTPUTS: {tool_output}
PREVIOUS MEMORY (FACTS):
{context}
"""
    
    raw = ask_llm(prompt, memory_context="", system_override=_MEMORY_SYSTEM)
    
    json_str = _extract_json(raw)
    
    try:
        data = json.loads(json_str)
        return {
            "memory_update": data.get("memory_update", ""),
            "relevant_memories": data.get("relevant_memories", data.get("relevant_memory", []))
        }
    except json.JSONDecodeError:
        return {"memory_update": "", "relevant_memories": []}

def _extract_json(text: str) -> str:
    """Extract JSON from text."""
    text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else text
