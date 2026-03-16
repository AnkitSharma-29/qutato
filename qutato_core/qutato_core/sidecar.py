"""
Qutato Sidecar — Lightweight Agent Integration Module

This module provides a simple Python API for any AI agent (including Antigravity)
to use Qutato's Trust Layer without going through the HTTP Gateway.

Usage:
    from qutato_core.sidecar import qutato

    # Vet a prompt before sending to LLM
    if qutato.is_safe("user prompt here"):
        # proceed with LLM call
    else:
        print("Qutato blocked this prompt")

    # Store a fact
    qutato.learn("Important project context")

    # Recall facts
    results = qutato.recall("project")

    # Log a saving (when you skip an LLM call)
    qutato.log_saving(tokens=250)

    # Get current status
    status = qutato.status()
"""

from qutato_core.engine.memory import memory_engine
from qutato_core.engine.detector import prompt_detector
from qutato_core.engine.adversarial_prober import adversarial_prober
from qutato_core.engine.quota import quota_manager
from qutato_core.engine.budget import budget_manager
from qutato_core.engine.loop_detector import loop_detector
import json


class QutaoSidecar:
    """Direct Python integration for AI agents — no HTTP needed."""

    def is_safe(self, prompt: str, role: str = None) -> bool:
        """Full safety check: junk + adversarial + loop + budget. Returns True if safe."""
        # 1. Check for junk
        report = prompt_detector.analyze_prompt(prompt)
        if report["is_junk"]:
            print(f"🚫 [Qutato Sidecar] Blocked JUNK: '{prompt[:40]}...'")
            quota_manager.log_savings("sidecar_agent", estimated_tokens=10)
            budget_manager.log_block(reason="junk_input")
            return False

        # 2. Check for adversarial probes (Injections/Jailbreaks)
        adv_report = adversarial_prober.probe(prompt, role=role)
        if adv_report["is_adversarial"]:
            print(f"🛑 [Qutato Sidecar] Blocked ADVERSARIAL: '{prompt[:40]}...'")
            print(f"   Reason: Matched patterns {adv_report['matched_patterns']}")
            quota_manager.log_savings("sidecar_agent", estimated_tokens=100)
            budget_manager.log_block(reason=f"adversarial_probe ({role or 'Generic'})")
            return False

        # 3. Check for loops
        if loop_detector.is_loop(prompt):
            quota_manager.log_savings("sidecar_agent", estimated_tokens=250)
            budget_manager.log_block(reason="loop_detected")
            return False

        # 4. Check budget
        if not budget_manager.can_spend(estimated_tokens=500):
            return False

        if report["is_sensitive"]:
            print(f"⚠️  [Qutato Sidecar] Sensitive content detected in: '{prompt[:40]}...'")
        print(f"✅ [Qutato Sidecar] Safe: '{prompt[:40]}...'")
        return True

    def learn(self, fact: str) -> None:
        """Store a fact in Qutato's persistent memory."""
        memory_engine.store(fact)
        print(f"🧠 [Qutato Sidecar] Learned: '{fact[:50]}'")

    def recall(self, query: str, top_k: int = 3) -> list:
        """Recall facts from Qutato's memory."""
        results = memory_engine.retrieve(query, limit=top_k)
        print(f"🔍 [Qutato Sidecar] Found {len(results)} facts for '{query}'")
        return results

    def sync(self) -> dict:
        """Synchronize memory with a remote shared brain."""
        return memory_engine.sync()

    def log_saving(self, tokens: int = 250, user_id: str = "antigravity_agent") -> None:
        """Log a quota saving (e.g., when skipping an unnecessary LLM call)."""
        quota_manager.log_savings(user_id, estimated_tokens=tokens)
        print(f"💰 [Qutato Sidecar] Logged saving: {tokens} tokens")

    def log_spend(self, tokens: int = 500) -> None:
        """Log actual token spending after an LLM call."""
        budget_manager.log_spend(tokens)

    def budget(self) -> dict:
        """Get current budget status."""
        return budget_manager.get_status()

    def set_budget(self, daily_limit_tokens: int) -> None:
        """Set the daily token cap."""
        budget_manager.set_token_limit(daily_limit_tokens)

    def status(self) -> dict:
        """Get Qutato's full status as a dictionary."""
        agent_calls, agent_tokens = quota_manager.get_savings("antigravity_agent")
        total_calls, total_tokens = quota_manager.get_total_savings()
        budget = budget_manager.get_status()
        loops = loop_detector.get_stats()
        return {
            "memory_health": "Optimized",
            "known_facts": len(memory_engine.memories),
            "agent_saved_calls": agent_calls,
            "agent_saved_tokens": agent_tokens,
            "total_saved_calls": total_calls,
            "total_saved_tokens": total_tokens,
            "budget": budget,
            "loops_killed": loops["total_loops_killed"],
            "db_path": memory_engine.db_path
        }


# Global singleton — import and use directly
qutato = QutaoSidecar()
