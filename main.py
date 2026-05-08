"""main.py — CLI entry point for Kira agent."""

import sys
from core.loop import agent
from memory.memory import clear_memory, clear_all, get_facts


BANNER = """
╔══════════════════════════════════════════════════╗
║       🧠  KIRA  AGENT  v10.0             ║
║   11-agent ReAct · Controller · Self-Improving  ║
╚══════════════════════════════════════════════════╝
Commands:
  /clear   → wipe short-term memory (keep facts)
  /reset   → wipe ALL memory (short + long term)
  /facts   → show stored long-term facts
  /quit    → exit
"""


def main():
    print(BANNER)

    while True:
        try:
            user_input = input("You → ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Bye.")
            sys.exit(0)

        if not user_input:
            continue

        if user_input.lower() in ("/quit", "/exit", "quit", "exit"):
            print("👋 Bye.")
            sys.exit(0)

        if user_input.lower() == "/clear":
            clear_memory()
            print("🧹 Short-term memory cleared.\n")
            continue

        if user_input.lower() == "/reset":
            clear_all()
            print("🧹 All memory wiped (short + long term).\n")
            continue

        if user_input.lower() == "/facts":
            facts = get_facts()
            if facts:
                print("\n📚 Long-term facts:")
                for i, f in enumerate(facts, 1):
                    print(f"  {i}. {f}")
            else:
                print("  (no facts stored yet)")
            print()
            continue

        result = agent(user_input)
        print(f"Agent → {result}\n")


if __name__ == "__main__":
    main()
