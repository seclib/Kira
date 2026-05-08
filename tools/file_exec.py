"""file_exec.py — Agent Tool: File Executor.

Role:
- Read, write, and update files safely.
- Organize and manage project directory structure.
"""

import os
import json
import shutil

def run_file_operation(payload: str) -> str:
    """
    Execute a file operation based on a JSON payload.
    Expected payload format:
    {
      "op": "read | write | list | delete",
      "path": "path/to/file",
      "content": "..." (for write)
    }
    """
    try:
        data = json.loads(payload)
        op = data.get("op", "").lower()
        path = data.get("path", "")
        
        # Security: Prevent escaping the workspace
        # Resolve symlinks and normalize paths for strict validation
        abs_path = os.path.realpath(path)
        workspace_root = os.path.realpath(os.getcwd())
        
        if not abs_path.startswith(workspace_root):
            return f"Security Error: Path '{path}' resolves to '{abs_path}', which is outside the workspace."

        if op == "read":
            if not os.path.exists(path):
                return f"Error: File '{path}' not found."
            with open(path, 'r') as f:
                return f.read()

        elif op == "write":
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(data.get("content", ""))
            return f"Success: File '{path}' written."

        elif op == "list":
            dir_to_list = path if path else "."
            if not os.path.isdir(dir_to_list):
                return f"Error: '{dir_to_list}' is not a directory."
            items = os.listdir(dir_to_list)
            return "\n".join(items)

        elif op == "delete":
            if not os.path.exists(path):
                return f"Error: '{path}' does not exist."
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            return f"Success: '{path}' deleted."

        else:
            return f"Error: Unknown operation '{op}'."

    except json.JSONDecodeError:
        # If payload is not JSON, try to treat it as a path for listing (fallback)
        if os.path.exists(payload):
            return run_file_operation(json.dumps({"op": "list", "path": payload}))
        return "Error: Invalid file operation payload (expected JSON)."
    except Exception as e:
        return f"File System Error: {str(e)}"
