"""
Qutato Budget Manager — Daily Token Cap

Prevents runaway agents by tracking token volume and blocking
requests when the daily token budget is exceeded.

Usage:
    qutato budget                 # Show remaining token budget
    qutato budget --set 500000    # Set daily limit to 500k tokens
    qutato budget --reset         # Reset today's token count
"""

import json
import os
import time
from datetime import datetime


class BudgetManager:
    """Track and enforce daily token spending limits."""

    def __init__(self, budget_path: str = None):
        if budget_path is None:
            home = os.path.expanduser("~")
            qutato_dir = os.path.join(home, ".qutato")
            os.makedirs(qutato_dir, exist_ok=True)
            budget_path = os.path.join(qutato_dir, "qutato_budget.json")

        self.budget_path = budget_path
        self._data = {
            "daily_token_limit": 500000,
            "today": datetime.now().strftime("%Y-%m-%d"),
            "tokens_today": 0,
            "requests_today": 0,
            "blocked_today": 0,
        }
        self._load()

    def _load(self):
        if os.path.exists(self.budget_path):
            try:
                with open(self.budget_path, "r") as f:
                    self._data = json.load(f)
            except:
                pass
        
        # Ensure daily_token_limit exists for older config migrations
        if "daily_token_limit" not in self._data:
            self._data["daily_token_limit"] = 500000

        # Auto-reset if it's a new day
        today = datetime.now().strftime("%Y-%m-%d")
        if self._data.get("today") != today:
            self._data["today"] = today
            self._data["tokens_today"] = 0
            self._data["requests_today"] = 0
            self._data["blocked_today"] = 0
            self._save()

    def _save(self):
        with open(self.budget_path, "w") as f:
            json.dump(self._data, f, indent=2)

    def set_token_limit(self, limit: int):
        """Set the daily token cap."""
        self._data["daily_token_limit"] = limit
        self._save()
        print(f"💰 [Qutato Budget] Daily token limit set to {limit:,}")

    def can_spend(self, estimated_tokens: int = 500) -> bool:
        """Check if the request fits within today's token budget."""
        self._load()  # Refresh in case another process updated
        limit = self._data.get("daily_token_limit", 500000)
        remaining = limit - self._data["tokens_today"]

        if remaining <= 0 or estimated_tokens > remaining:
            self._data["blocked_today"] += 1
            self._save()
            print(f"🚫 [Qutato Budget] BLOCKED! Daily limit of {limit:,} tokens reached. Used: {self._data['tokens_today']:,}")
            return False
        return True

    def log_spend(self, tokens_used: int):
        """Record a completed request's token usage."""
        self._data["tokens_today"] += tokens_used
        self._data["requests_today"] += 1
        self._save()

    def get_status(self) -> dict:
        """Get current budget status."""
        self._load()
        limit = self._data.get("daily_token_limit", 500000)
        remaining = limit - self._data["tokens_today"]
        return {
            "daily_token_limit": limit,
            "tokens_today": self._data["tokens_today"],
            "remaining_tokens": max(0, remaining),
            "requests_today": self._data["requests_today"],
            "blocked_today": self._data["blocked_today"],
            "date": self._data["today"],
        }


budget_manager = BudgetManager()
