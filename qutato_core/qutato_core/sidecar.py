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
from qutato_core.engine.quota import quota_manager
import json


class QutaoSidecar:
    """Direct Python integration for AI agents — no HTTP needed."""

    def is_safe(self, prompt: str) -> bool:
        """Vet a prompt using Qutato's Guardrails. Returns True if safe."""
        report = prompt_detector.analyze_prompt(prompt)
        if report["is_junk"]:
            print(f"🚫 [Qutato Sidecar] Blocked JUNK: '{prompt[:40]}...'")
            quota_manager.log_savings("sidecar_agent", estimated_tokens=10)
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

    def log_saving(self, tokens: int = 250, user_id: str = "antigravity_agent") -> None:
        """Log a quota saving (e.g., when skipping an unnecessary LLM call)."""
        quota_manager.log_savings(user_id, estimated_tokens=tokens)
        print(f"💰 [Qutato Sidecar] Logged saving: {tokens} tokens")

    def status(self) -> dict:
        """Get Qutato's current status as a dictionary."""
        saved_calls, saved_tokens = quota_manager.get_savings("antigravity_agent")
        total_calls, total_tokens = quota_manager.get_savings("default_user")
        return {
            "memory_health": "Optimized",
            "known_facts": len(memory_engine.memories),
            "agent_saved_calls": saved_calls,
            "agent_saved_tokens": saved_tokens,
            "total_saved_calls": total_calls + saved_calls,
            "total_saved_tokens": total_tokens + saved_tokens,
            "db_path": memory_engine.db_path
        }


# Global singleton — import and use directly
qutato = QutaoSidecar()
