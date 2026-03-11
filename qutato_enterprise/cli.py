import argparse
import sys
from qutato_core.engine.memory import memory_engine

def main():
    parser = argparse.ArgumentParser(description="Qutato Management CLI")
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

    args = parser.parse_args()

    if args.command == "status":
        count = len(memory_engine.memories)
        saved_calls, saved_tokens = quota_manager.get_savings("default_user")
        
        print(f"--- Qutato Smart Core Status ---")
        print(f"Memory Health: Optimized")
        print(f"Known Facts:   {count}")
        print(f"Quota Saved:   {saved_calls} requests (~{saved_tokens} tokens)")
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

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
