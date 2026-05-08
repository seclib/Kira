"""python_exec.py — Agent Tool: Python Executor.

Role:
- Execute Python code safely in a subprocess.
- Capture and return stdout or descriptive errors.
"""

import subprocess
import sys
import textwrap

def run_python(code: str, timeout: int = 15) -> str:
    """
    Safely execute a Python snippet and return the resulting output or error.
    """
    # Clean and dedent code
    clean_code = textwrap.dedent(code).strip()

    # Security: Prevent obviously dangerous operations
    # This is a 'lite' safety measure; full sandboxing requires a container.
    danger_keywords = ["os.remove", "os.rmdir", "shutil.rmtree", "subprocess.run", "subprocess.Popen", "os.system"]
    for kw in danger_keywords:
        if kw in clean_code:
            return f"Security Error: Usage of '{kw}' is prohibited for safety reasons."

    try:
        # Run in a separate subprocess for safety
        process = subprocess.run(
            [sys.executable, "-c", clean_code],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        
        stdout = process.stdout.strip()
        stderr = process.stderr.strip()

        if process.returncode == 0:
            return stdout if stdout else "[Execution successful, no output]"
        else:
            return f"Runtime Error:\n{stderr}"

    except subprocess.TimeoutExpired:
        return f"Execution Error: Code timed out after {timeout} seconds."
    except Exception as e:
        return f"System Error: {str(e)}"
