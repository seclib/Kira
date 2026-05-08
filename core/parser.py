"""parser.py — Parse LLM output and extract tool dispatch instructions."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ActionType(Enum):
    DIRECT = "direct"
    WEB = "web"
    PYTHON = "python"
    FILE = "file"


@dataclass
class ParsedAction:
    action: ActionType
    payload: Optional[str] = None  # query or code
    raw: str = ""


def parse_response(response: str) -> ParsedAction:
    """
    Parse the LLM response string and return a structured ParsedAction.

    Supported patterns:
      - Starts with or contains 'WEB: <query>'
      - Starts with or contains 'PY: <code>'
      - Starts with or contains 'FILE: <json_op>'
      - Anything else → DIRECT answer
    """
    text = response.strip()

    # Check for WEB: tag
    if "WEB:" in text:
        parts = text.split("WEB:", 1)
        query = parts[1].strip().splitlines()[0].strip()  # first line only
        return ParsedAction(action=ActionType.WEB, payload=query, raw=text)

    # Check for PY: tag
    if "PY:" in text:
        parts = text.split("PY:", 1)
        code = parts[1].strip()
        # Strip markdown code fences if present
        if code.startswith("```"):
            lines = code.splitlines()
            code = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
        return ParsedAction(action=ActionType.PYTHON, payload=code.strip(), raw=text)

    # Check for FILE: tag
    if "FILE:" in text:
        parts = text.split("FILE:", 1)
        payload = parts[1].strip()
        # Strip markdown code fences if present
        if payload.startswith("```"):
            lines = payload.splitlines()
            payload = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
        return ParsedAction(action=ActionType.FILE, payload=payload.strip(), raw=text)

    # Default: direct answer
    return ParsedAction(action=ActionType.DIRECT, payload=text, raw=text)
