import argparse
import sys
from qutato_core.engine.memory import memory_engine
from qutato_core.engine.quota import quota_manager
from qutato_core.engine.budget import budget_manager
from qutato_core.engine.loop_detector import loop_detector
from qutato_core.engine.updater import print_update_notification
from qutato_core.version import __version__

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
    budget_parser = subparsers.add_parser("budget", help="View or set daily token cap")
    budget_parser.add_argument("--set-tokens", type=int, help="Set daily limit in tokens (e.g. --set-tokens 500000)")
    budget_parser.add_argument("--reset", action="store_true", help="Reset today's token count")

    # Command: gstack
    gstack_parser = subparsers.add_parser("gstack", help="gstack compatibility bridge")
    gstack_parser.add_argument("--role", help="Engineering role (CEO, Architect, Security, QA)")
    gstack_parser.add_argument("--prompt", required=True, help="Prompt to vet")

    # Command: commands
    subparsers.add_parser("commands", help="List all available Qutato commands")

    args = parser.parse_args()

    if args.command == "status":
        count = len(memory_engine.memories)
        total_calls, total_tokens = quota_manager.get_total_savings()
        budget = budget_manager.get_status()
        loops = loop_detector.get_stats()

        print(f"--- Qutato Smart Core Status (v{__version__}) ---")
        print(f"Memory Health: Optimized")
        print(f"Known Facts:   {count}")
        print(f"Quota Saved:   {total_calls} requests (~{total_tokens} tokens)")
        print(f"Daily Budget:  {budget['tokens_today']:,} / {budget['daily_token_limit']:,} tokens ({budget['remaining_tokens']:,} left)")
        print(f"Requests Today:{budget['requests_today']}")
        print(f"Loops Killed:  {loops['total_loops_killed']}")
        print(f"DB Path:       {memory_engine.db_path}")
        
        # Check for updates (non-blocking)
        print_update_notification()

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
        if args.set_tokens is not None:
            budget_manager.set_token_limit(args.set_tokens)
        elif args.reset:
            budget_manager._data["tokens_today"] = 0
            budget_manager._data["requests_today"] = 0
            budget_manager._data["blocked_today"] = 0
            budget_manager._save()
            print("🔄 Today's token usage has been reset to 0.")
        else:
            b = budget_manager.get_status()
            print(f"--- Qutato Token Budget ---")
            print(f"Daily Limit:      {b['daily_token_limit']:,} tokens")
            print(f"Tokens Used:      {b['tokens_today']:,} tokens")
            print(f"Remaining:        {b['remaining_tokens']:,} tokens")
            print(f"Requests Today:   {b['requests_today']}")
            print(f"Blocked Today:    {b['blocked_today']}")

    elif args.command == "update":
        from qutato_core.engine.logo import print_logo
        import subprocess
        import os
        import qutato_core
        
        # Find where Qutato is installed from (the root git clone directory)
        install_dir = os.path.dirname(os.path.dirname(os.path.abspath(qutato_core.__file__)))
        
        print_logo()
        print(f"📥 Pulling latest updates from GitHub into: {install_dir}")
        try:
            result = subprocess.run(
                ["git", "pull", "origin", "main"], 
                cwd=install_dir, 
                capture_output=True, 
                text=True
            )
            if result.returncode == 0:
                print("✅ Update successful!")
                print(result.stdout)
            else:
                print("❌ Update failed. Are you sure you installed via git clone?")
                print(result.stderr)
        except Exception as e:
            print(f"❌ Error during update: {e}")

    elif args.command == "gstack":
        from qutato_core.gstack_bridge import GStackBridge
        bridge = GStackBridge()
        report = bridge.vet_prompt(args.prompt, role=args.role)
        
        import json
        print(json.dumps(report, indent=2))

    elif args.command == "commands":
        from qutato_core.engine.logo import print_logo
        print_logo()
        print("--- 🛡️ Qutato Command Reference ---\n")
        print("Usage: qutato <command> [options]\n")
        print("Commands:")
        print("  status    View real-time savings, budget, and memory health")
        print("  budget    View or manage your daily token cap")
        print("            - qutato budget --set-tokens 500000")
        print("            - qutato budget --reset")
        print("  learn     Store a new fact in the Qutato Brain")
        print("            - qutato learn \"The deadline is Friday\"")
        print("  recall    Search the Brain for context")
        print("            - qutato recall \"deadline\"")
        print("  forget    Wipe the entire memory brain")
        print("  gstack    Analyze a prompt through an engineering role lens")
        print("            - qutato gstack --role Architect --prompt \"use global vars\"")
        print("  update    Pull the latest Qutato updates from GitHub")
        print("  commands  Show this custom help menu\n")

    else:
        # Fallback to standard argparse help
        parser.print_help()

if __name__ == "__main__":
    main()
