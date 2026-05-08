"""loop.py — Eleven-agent Autonomous Execution Loop Orchestrator.

Pipeline:
  Agent 0 — Intent Parser      (core/intent_parser.py)      CLASSIFY
  Agent 7 — Goal Interpreter  (core/goal_interpreter.py)   MISSION
  Agent 6 — Memory Manager    (core/memory_manager.py)     MEMORY
  Agent 1 — Task Planner       (core/planner.py)            PLAN
  Agent 10 — Loop Controller   (core/controller.py)         DECIDE
  Agent 2 — Tool Router        (core/router.py)             ROUTE
  Agent 3 — LLM Reasoner       (llm.py + core/parser.py)    THINK
  Agent 4 — Execution System   (core/executor.py)           ACT
  Agent 8 — Reflection Node    (core/reflection.py)         REFLECT
  Agent 9 — Termination Check  (core/termination.py)        VERIFY
  Agent 5 — Final Gen          (core/assembler.py)          FINISH
"""

import json
from llm import ask_llm
from memory.memory import get_full_context, save_memory, save_fact
from core.intent_parser import parse_intent
from core.goal_interpreter import interpret_goal
from core.planner import create_plan, Task
from core.router import route_task, RouteTarget
from core.parser import parse_response, ActionType
from core.executor import execute_task
from core.assembler import assemble
from core.memory_manager import process_memory
from core.reflection import reflect
from core.termination import check_termination
from core.controller import decide_next_action


def agent(user_input: str, max_turns: int = 15) -> str:
    """
    Autonomous Execution Loop Orchestrator.
    """

    # ── Initialization ───────────────────────────────────────────────────
    save_memory(user_input, role="user")
    
    # 1. Classify
    intent = parse_intent(user_input)
    print(f"\n🎯 [INTENT] {intent.intent} ({intent.complexity})")

    # 2. Define Mission
    mission = interpret_goal(user_input)
    print(f"🚀 [MISSION] {mission.goal} (Est. Steps: {mission.estimated_steps})")

    # 3. Initial Planning
    plan = create_plan(mission.goal, memory_context=get_full_context())
    tasks = plan.tasks
    completed_task_ids = []
    print(f"📋 [PLAN] {len(tasks)} tasks queued.")

    turn = 0
    last_observation = ""
    history_log = []

    # ── AUTONOMOUS LOOP ──────────────────────────────────────────────────
    while turn < max_turns:
        turn += 1
        history_str = "\n".join(history_log[-5:]) 
        
        # 4. DECIDE NEXT ACTION (Agent 10)
        decision = decide_next_action(mission.goal, tasks, completed_task_ids, history=history_str)
        print(f"\n🎮 [CONTROL] Turn {turn} | {decision.action.upper()} | Task: {decision.next_task_id}")
        
        if decision.action == "finalize":
            term = check_termination(mission.goal, get_full_context())
            if term.done:
                print(f"🏁 [DONE] {term.reason}")
                break
            else:
                decision.action = "replan"

        if decision.action == "replan":
            plan = create_plan(mission.goal, memory_context=get_full_context())
            tasks = plan.tasks
            print(f"📋 [RE-PLAN] {len(tasks)} new tasks queued.")
            continue

        # Find current task
        current_task = next((t for t in tasks if t.id == decision.next_task_id), None)
        if not current_task:
            unfinished = [t for t in tasks if t.id not in completed_task_ids]
            if unfinished: current_task = unfinished[0]
            else: break

        # 5. Route (Initial check)
        target = route_task(current_task, False)
        
        # 6. Think (Reasoner)
        reasoner_context = get_full_context()
        step_query = f"Mission: {mission.goal}\nTask: {current_task.objective}"
        
        raw_response = ask_llm(step_query, memory_context=reasoner_context)
        print(f"🤖 [THINK] {raw_response}")
        action = parse_response(raw_response)

        # 7. Act (Execution System - Agent 4)
        if target != RouteTarget.REASONING_NODE:
            # Map Reasoner action to Router expectation if needed
            if target == RouteTarget.WEB_TOOL: action.action = ActionType.WEB
            elif target == RouteTarget.PYTHON_TOOL: action.action = ActionType.PYTHON
            elif target == RouteTarget.FILE_TOOL: action.action = ActionType.FILE
            
            # Agent 4: Execute & Route
            result_json = execute_task(current_task.id, action.action, action.payload or "")
            try:
                data = json.loads(result_json)
                observation = data.get("result", "").strip()
                status = data.get("status", "success")
            except json.JSONDecodeError:
                observation = result_json.strip()
                status = "failed"
            
            print(f"⚙️ [{status.upper()}] {observation[:100]}...")
            last_observation = observation
            
            # 8. REFLECT
            reflection = reflect(mission.goal, current_task.objective, observation, context=get_full_context())
            print(f"🔍 [REFLECT] {reflection.status.upper()} (Conf: {reflection.confidence}) | Feedback: {reflection.feedback}")
            
            history_log.append(f"Task {current_task.id} result: {observation[:200]}. Status: {status}")
            
            if reflection.status == "good" and status == "success":
                completed_task_ids.append(current_task.id)
                save_memory(f"Task {current_task.id} Success: {observation}", role="agent")
            else:
                save_memory(f"Task {current_task.id} Issue: {reflection.feedback}", role="agent")
        else:
            observation = action.payload
            last_observation = observation
            completed_task_ids.append(current_task.id)
            history_log.append(f"Task {current_task.id} reasoning complete.")

        # 9. MEMORY (Store)
        mem_data = process_memory(mission.goal, tool_output=last_observation)
        if mem_data.get("memory_update"):
            save_fact(mem_data["memory_update"])

    # ── Finalization ───────────────────────────────────────────────────
    final_action = parse_response(last_observation) if last_observation else parse_response("Mission complete.")
    final_result = assemble(user_input, final_action, last_observation)
    print(f"\n✅ [FINAL] {final_result}\n")

    return final_result