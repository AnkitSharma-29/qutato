"""
Qutato Loop Detector — Auto-Kill Runaway Agent Loops

Detects when an AI agent is stuck sending the same (or very similar)
requests repeatedly, and blocks further attempts to save tokens.

Usage:
    from qutato_core.engine.loop_detector import loop_detector

    if loop_detector.is_loop(prompt):
        print("Loop detected! Blocking.")
    else:
        # proceed with LLM call
"""

import time
from collections import deque


class LoopDetector:
    """Detects repetitive agent behavior and auto-kills loops."""

    def __init__(self, window_size: int = 10, similarity_threshold: float = 0.8, max_repeats: int = 3):
        """
        Args:
            window_size: Number of recent prompts to track
            similarity_threshold: How similar two prompts must be to count as "same" (0-1)
            max_repeats: How many similar prompts before declaring a loop
        """
        self.window_size = window_size
        self.similarity_threshold = similarity_threshold
        self.max_repeats = max_repeats
        self._history = deque(maxlen=window_size)
        self._loop_count = 0
        self._total_loops_killed = 0

    def _similarity(self, a: str, b: str) -> float:
        """Simple character-level similarity (Jaccard on words)."""
        if not a or not b:
            return 0.0
        words_a = set(a.lower().split())
        words_b = set(b.lower().split())
        if not words_a or not words_b:
            return 1.0 if a.lower().strip() == b.lower().strip() else 0.0
        intersection = words_a & words_b
        union = words_a | words_b
        return len(intersection) / len(union) if union else 0.0

    def is_loop(self, prompt: str) -> bool:
        """
        Check if this prompt is part of a repetitive loop.
        Returns True if the agent appears to be stuck.
        """
        # Count how many recent prompts are very similar to this one
        similar_count = 0
        for past_prompt in self._history:
            if self._similarity(prompt, past_prompt) >= self.similarity_threshold:
                similar_count += 1

        # Add to history
        self._history.append(prompt)

        # Check if we've exceeded the repeat threshold
        if similar_count >= self.max_repeats:
            self._loop_count += 1
            self._total_loops_killed += 1
            print(f"🔄 [Qutato Loop Detector] LOOP DETECTED! '{prompt[:40]}...' repeated {similar_count + 1} times. Auto-killing.")
            return True

        # Reset loop count if we see a new prompt
        if similar_count == 0:
            self._loop_count = 0

        return False

    def get_stats(self) -> dict:
        """Get loop detection stats."""
        return {
            "total_loops_killed": self._total_loops_killed,
            "current_streak": self._loop_count,
            "history_size": len(self._history),
        }

    def reset(self):
        """Clear the history."""
        self._history.clear()
        self._loop_count = 0


loop_detector = LoopDetector()
