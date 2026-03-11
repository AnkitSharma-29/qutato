"""
Qutato Budget Manager — Daily Spending Cap for Solo Builders

Prevents surprise LLM bills by tracking estimated token costs
and blocking requests when the daily budget is exceeded.

Usage:
    qutato budget                 # Show remaining budget
    qutato budget --set 5.00     # Set daily limit to $5
    qutato budget --reset        # Reset today's spending
"""

import json
import os
import time
from datetime import datetime


class BudgetManager:
    """Track and enforce daily token spending limits."""

    # Approximate costs per 1K tokens (input + output average)
    COST_PER_1K_TOKENS = {
        "gpt-4o": 0.005,
        "gpt-4": 0.03,
        "gpt-3.5-turbo": 0.001,
        "claude-3-opus": 0.015,
        "claude-3-sonnet": 0.003,
        "claude-3-haiku": 0.00025,
        "gemini-pro": 0.00025,
        "gemini-1.5-pro": 0.00125,
        "ollama/*": 0.0,  # Local models are free
        "default": 0.002,
    }

    def __init__(self, budget_path: str = None):
        if budget_path is None:
            home = os.path.expanduser("~")
            qutato_dir = os.path.join(home, ".qutato")
            os.makedirs(qutato_dir, exist_ok=True)
            budget_path = os.path.join(qutato_dir, "qutato_budget.json")

        self.budget_path = budget_path
        self._data = {
            "daily_limit_usd": 5.00,
            "today": datetime.now().strftime("%Y-%m-%d"),
            "spent_today_usd": 0.0,
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
        # Auto-reset if it's a new day
        today = datetime.now().strftime("%Y-%m-%d")
        if self._data.get("today") != today:
            self._data["today"] = today
            self._data["spent_today_usd"] = 0.0
            self._data["tokens_today"] = 0
            self._data["requests_today"] = 0
            self._data["blocked_today"] = 0
            self._save()

    def _save(self):
        with open(self.budget_path, "w") as f:
            json.dump(self._data, f, indent=2)

    def set_daily_limit(self, amount_usd: float):
        """Set the daily spending cap."""
        self._data["daily_limit_usd"] = amount_usd
        self._save()
        print(f"💰 [Qutato Budget] Daily limit set to ${amount_usd:.2f}")

    def estimate_cost(self, model: str, estimated_tokens: int) -> float:
        """Estimate the cost of a request."""
        # Check for exact match or wildcard
        cost_rate = self.COST_PER_1K_TOKENS.get("default", 0.002)
        for key, rate in self.COST_PER_1K_TOKENS.items():
            if key.endswith("/*") and model.startswith(key[:-2]):
                cost_rate = rate
                break
            elif model.startswith(key):
                cost_rate = rate
                break
        return (estimated_tokens / 1000) * cost_rate

    def can_spend(self, model: str = "default", estimated_tokens: int = 500) -> bool:
        """Check if the request fits within today's budget."""
        self._load()  # Refresh in case another process updated
        estimated_cost = self.estimate_cost(model, estimated_tokens)
        remaining = self._data["daily_limit_usd"] - self._data["spent_today_usd"]

        if remaining <= 0 or estimated_cost > remaining:
            self._data["blocked_today"] += 1
            self._save()
            print(f"🚫 [Qutato Budget] BLOCKED! Daily limit ${self._data['daily_limit_usd']:.2f} reached. Spent: ${self._data['spent_today_usd']:.2f}")
            return False
        return True

    def log_spend(self, model: str, tokens_used: int):
        """Record a completed request's cost."""
        cost = self.estimate_cost(model, tokens_used)
        self._data["spent_today_usd"] += cost
        self._data["tokens_today"] += tokens_used
        self._data["requests_today"] += 1
        self._save()

    def get_status(self) -> dict:
        """Get current budget status."""
        self._load()
        remaining = self._data["daily_limit_usd"] - self._data["spent_today_usd"]
        return {
            "daily_limit": f"${self._data['daily_limit_usd']:.2f}",
            "spent_today": f"${self._data['spent_today_usd']:.4f}",
            "remaining": f"${max(0, remaining):.4f}",
            "tokens_today": self._data["tokens_today"],
            "requests_today": self._data["requests_today"],
            "blocked_today": self._data["blocked_today"],
            "date": self._data["today"],
        }


budget_manager = BudgetManager()
