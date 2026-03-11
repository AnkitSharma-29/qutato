import argparse
import sys
from qutato_core.engine.memory import memory_engine
from qutato_core.engine.quota import quota_manager
from qutato_core.engine.budget import budget_manager
from qutato_core.engine.loop_detector import loop_detector

def main():
    parser = argparse.ArgumentParser(description="Qutato — The Smart Core Trust Platform")
    subparsers = parser.add_subparsers(dest="command")

    # Command: status
    subparsers.add_parser("status", help="Show Qutato Smart Core status")

    # Command: learn
    learn_parser = subparsers.add_parser("learn", help="Memorize a new fact")
    learn_parser.add_argument("text", help="The fact to memorize")

    # Command: recall
    recall_parser = subparsers.add_parser("recall", help="Search the Qutato Brain")
    recall_parser.add_argument("query", help="What to search for")

    # Command: forget
    subparsers.add_parser("forget", help="Wipe the Qutato Memory")

    # Command: budget
    budget_parser = subparsers.add_parser("budget", help="View or set daily spending cap")
    budget_parser.add_argument("--set", type=float, help="Set daily limit in USD (e.g. --set 5.00)")
    budget_parser.add_argument("--reset", action="store_true", help="Reset today's spending")

    args = parser.parse_args()

    if args.command == "status":
        count = len(memory_engine.memories)
        saved_calls, saved_tokens = quota_manager.get_savings("default_user")
        budget = budget_manager.get_status()
        loops = loop_detector.get_stats()

        print(f"--- Qutato Smart Core Status ---")
        print(f"Memory Health: Optimized")
        print(f"Known Facts:   {count}")
        print(f"Quota Saved:   {saved_calls} requests (~{saved_tokens} tokens)")
        print(f"Daily Budget:  {budget['spent_today']} / {budget['daily_limit']} ({budget['remaining']} left)")
        print(f"Requests Today:{budget['requests_today']}")
        print(f"Loops Killed:  {loops['total_loops_killed']}")
        print(f"DB Path:       {memory_engine.db_path}")

    elif args.command == "learn":
        memory_engine.store(args.text)
        print("✅ Qutato has memorized this. It is now part of the Trust Layer.")

    elif args.command == "recall":
        results = memory_engine.retrieve(args.query)
        if not results:
            print("❌ No matching context found in the brain.")
        else:
            print(f"--- Qutato Recall Results ---")
            for i, r in enumerate(results, 1):
                print(f"{i}. {r}")

    elif args.command == "forget":
        memory_engine.clear()
        print("🧹 Brain wiped. Qutato is now a blank slate.")

    elif args.command == "budget":
        if args.set is not None:
            budget_manager.set_daily_limit(args.set)
        elif args.reset:
            budget_manager._data["spent_today_usd"] = 0.0
            budget_manager._data["tokens_today"] = 0
            budget_manager._data["requests_today"] = 0
            budget_manager._data["blocked_today"] = 0
            budget_manager._save()
            print("🔄 Today's spending has been reset to $0.00")
        else:
            b = budget_manager.get_status()
            print(f"--- Qutato Budget ---")
            print(f"Daily Limit:    {b['daily_limit']}")
            print(f"Spent Today:    {b['spent_today']}")
            print(f"Remaining:      {b['remaining']}")
            print(f"Tokens Today:   {b['tokens_today']}")
            print(f"Requests Today: {b['requests_today']}")
            print(f"Blocked Today:  {b['blocked_today']}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
