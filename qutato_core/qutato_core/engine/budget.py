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


from typing import Dict, Any, Optional

class BudgetManager:
    """Track and enforce daily token spending limits."""

    def __init__(self, budget_path: Optional[str] = None):
        if budget_path is None:
            home = os.path.expanduser("~")
            qutato_dir = os.path.join(home, ".qutato")
            os.makedirs(qutato_dir, exist_ok=True)
            budget_path = os.path.join(qutato_dir, "qutato_budget.json")

        self.budget_path = budget_path
        # Default data structure with explicit types
        self._data: Dict[str, Any] = {
            "daily_token_limit": 500000,
            "today": datetime.now().strftime("%Y-%m-%d"),
            "tokens_today": 0,
            "requests_today": 0,
            "blocked_today": 0,
        }
        self._load()

    def _load(self):
        """Load budget from disk with robust error handling."""
        if not os.path.exists(self.budget_path):
            self._save()
            return

        try:
            with open(self.budget_path, "r") as f:
                loaded_data = json.load(f)
                if isinstance(loaded_data, dict):
                    # Merge and ensure numeric types
                    for key in ["daily_token_limit", "tokens_today", "requests_today", "blocked_today"]:
                        if key in loaded_data:
                            try:
                                loaded_data[key] = int(loaded_data[key])
                            except (ValueError, TypeError):
                                loaded_data[key] = self._data[key]
                    self._data.update(loaded_data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️ [Qutato Budget] Warning: Could not read budget file ({str(e)}). Using defaults.")
        
        # Auto-reset if it's a new day
        today = datetime.now().strftime("%Y-%m-%d")
        if self._data.get("today") != today:
            self._data.update({
                "today": today,
                "tokens_today": 0,
                "requests_today": 0,
                "blocked_today": 0,
            })
            self._save()

    def _save(self):
        """Atomic save to avoid corruption during concurrent writes."""
        temp_path = self.budget_path + ".tmp"
        try:
            with open(temp_path, "w") as f:
                json.dump(self._data, f, indent=2)
            # Atomic swap
            os.replace(temp_path, self.budget_path)
        except IOError as e:
            print(f"❌ [Qutato Budget] Critical Error: Failed to save budget! {str(e)}")
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass

    def set_token_limit(self, limit: int):
        """Set the daily token cap."""
        self._data["daily_token_limit"] = int(limit)
        self._save()
        print(f"💰 [Qutato Budget] Daily token limit set to {limit:,}")

    def can_spend(self, estimated_tokens: int = 500) -> bool:
        """Check if the request fits within today's token budget."""
        self._load()  # Refresh in case another process updated
        limit = int(self._data.get("daily_token_limit", 500000))
        used = int(self._data.get("tokens_today", 0))
        remaining = limit - used

        if remaining <= 0 or estimated_tokens > remaining:
            self._data["blocked_today"] = int(self._data.get("blocked_today", 0)) + 1
            self._save()
            print(f"🚫 [Qutato Budget] BLOCKED! Daily limit of {limit:,} tokens reached. Used: {used:,}")
            return False
        return True

    def log_spend(self, tokens_used: int):
        """Record a completed request's token usage."""
        self._data["tokens_today"] = int(self._data.get("tokens_today", 0)) + int(tokens_used)
        self._data["requests_today"] = int(self._data.get("requests_today", 0)) + 1
        self._save()

    def get_status(self) -> Dict[str, Any]:
        """Get current budget status."""
        self._load()
        limit = int(self._data.get("daily_token_limit", 500000))
        used = int(self._data.get("tokens_today", 0))
        remaining = limit - used
        return {
            "daily_token_limit": limit,
            "tokens_today": used,
            "remaining_tokens": max(0, remaining),
            "requests_today": int(self._data.get("requests_today", 0)),
            "blocked_today": int(self._data.get("blocked_today", 0)),
            "date": str(self._data.get("today")),
        }


budget_manager = BudgetManager()
