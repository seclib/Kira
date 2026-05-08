"""router.py — Agent 2: Tool Router.

Deterministic module that decides where tasks go.
Destinations: WEB_TOOL, PYTHON_TOOL, FILE_TOOL, REASONING_NODE.

RULES:
- Deterministic routing.
- No execution.
- No reasoning.
"""

from enum import Enum
from core.planner import Task

class RouteTarget(Enum):
    WEB_TOOL = "WEB_TOOL"
    PYTHON_TOOL = "PYTHON_TOOL"
    FILE_TOOL = "FILE_TOOL"
    REASONING_NODE = "REASONING_NODE"

def route_task(task: Task, is_last: bool) -> RouteTarget:
    """
    Deterministically route a task to its destination.
    """
    t_type = task.type.lower()
    
    if t_type == "web":
        return RouteTarget.WEB_TOOL
    elif t_type == "python":
        return RouteTarget.PYTHON_TOOL
    elif t_type == "file":
        return RouteTarget.FILE_TOOL
    
    # Default and 'reasoning' tasks go to REASONING_NODE
    return RouteTarget.REASONING_NODE
