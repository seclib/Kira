# 🧠 Kira v10.0

A high-intelligence, 11-agent autonomous AI system powered by **Ollama**.

## 🏗️ 11-Agent Architecture

Kira v10.0 features an LLM-driven orchestration layer for dynamic loop control:

1.  **Agent 0: Intent Parser** (`core/intent_parser.py`)
    - Classifies the request and detects complexity.
2.  **Agent 7: Goal Interpreter** (`core/goal_interpreter.py`)
    - **Mission Layer**: Redefines the request into a precise mission with autonomy detection.
3.  **Agent 6: Memory Manager (Retrieve)** (`core/memory_manager.py`)
    - Finds relevant past context and project durable knowledge.
4.  **Agent 1: Task Planner** (`core/planner.py`)
    - Breaks the mission into atomic tasks with explicit dependencies.
5.  **Agent 10: Execution Loop Controller** (`core/controller.py`)
    - **Orchestration Layer**: Dynamically decides the next action (execute, retry, replan, finalize).
6.  **Agent 2: Tool Router** (`core/router.py`)
    - **Deterministic Layer**: Routes each task to `WEB_TOOL`, `PYTHON_TOOL`, `FILE_TOOL`, or `REASONING_NODE`.
7.  **Agent 3: Reasoner** (`llm.py` + `core/parser.py`)
    - Generates specific tool calls or logic per task.
8.  **Agent 4: Executor** (`core/executor.py`)
    - Executes tools and returns strict JSON observations.
9.  **Agent 8: Reflection Node** (`core/reflection.py`)
    - **Self-Correction Layer**: Analyzes outputs to detect mistakes/hallucinations.
    - Provides critical feedback and confidence scores for each evaluation.
10. **Agent 9: Termination Checker** (`core/termination.py`)
    - **Validation Layer**: Strictly determines if the mission objective is achieved.
11. **Agent 5: Final Response Generator** (`core/assembler.py`)
    - Synthesizes the final human-readable answer.

## 🧠 Dual-Layer Memory

- **Short-term Memory:** Rolling conversation context (50 turns).
- **Long-term Facts:** Durable knowledge managed by the Memory Manager.

## 🚀 Setup

```bash
# 1. Create virtualenv
python3 -m venv env
source env/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start Ollama
ollama serve
ollama pull mistral

# 4. Run the agent
python main.py
```

## 🛠️ Commands

| Command | Effect |
|---|---|
| `/clear` | Wipe short-term memory (keep facts) |
| `/reset` | Wipe ALL memory (short + long term) |
| `/facts` | List all stored long-term knowledge |
| `/quit` | Exit the agent |

## 📂 File Structure

```
kira/
├── config.py              # Central config
├── llm.py                 # Ollama API client
├── main.py                # CLI Entry Point
├── core/
│   ├── loop.py            # Orchestrator
│   ├── intent_parser.py   # Agent 0
│   ├── goal_interpreter.py # Agent 7
│   ├── planner.py         # Agent 1
│   ├── controller.py      # Agent 10
│   ├── router.py          # Agent 2
│   ├── parser.py          # Agent 3
│   ├── executor.py        # Agent 4
│   ├── reflection.py      # Agent 8
│   ├── termination.py     # Agent 9
│   ├── assembler.py       # Agent 5
│   └── memory_manager.py  # Agent 6
├── tools/
│   ├── web.py             # Web Executor
│   ├── python_exec.py     # Python Executor
│   └── file_exec.py       # File Executor
├── memory/
│   └── memory.py          # SQLite logic
└── data/
    └── memory.db          # Database
```
