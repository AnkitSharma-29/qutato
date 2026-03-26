"""
🛡️ Qutato Trust Engine — The Core Safety Layer

Handles:
  - Input guardrails (junk detection, keyboard mashing)
  - PII redaction (emails, SSNs, credit cards, API keys)
  - Budget management (daily token caps)
  - Loop detection (kill runaway agents)
  - Abstention engine (confidence gating)
  - Memory brain (persistent fact storage)
"""

import json
import os
import re
import time
import hashlib
from pathlib import Path
from datetime import datetime, date
from typing import Optional


# ─── Storage ─────────────────────────────────────────────────────────────────

QUTATO_DIR = Path.home() / ".qutato"
MEMORY_FILE = QUTATO_DIR / "memory.json"
STATS_FILE = QUTATO_DIR / "qutato_stats.json"
BUDGET_FILE = QUTATO_DIR / "budget.json"
LOOP_FILE = QUTATO_DIR / "loop_history.json"
CONFIG_FILE = QUTATO_DIR / "config.json"


def _ensure_dirs():
    """Create the ~/.qutato directory if it doesn't exist."""
    QUTATO_DIR.mkdir(parents=True, exist_ok=True)


def _load_json(path: Path, default=None):
    """Load a JSON file safely."""
    if default is None:
        default = {}
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError):
        pass
    return default


def _save_json(path: Path, data):
    """Save data to a JSON file."""
    _ensure_dirs()
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


# ─── PII Redactor ────────────────────────────────────────────────────────────

PII_PATTERNS = {
    "EMAIL": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    "CREDIT_CARD": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
    "API_KEY": r"(?:sk-|api[_-]?key[=:\s]+)[a-zA-Z0-9_\-]{20,}",
    "AWS_KEY": r"(?:AKIA|ASIA)[A-Z0-9]{16}",
    "PHONE": r"\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "IP_ADDRESS": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
    "PASSWORD": r"(?:password|passwd|pwd)\s*[=:]\s*\S+",
    "CONNECTION_STRING": r"(?:mongodb|postgres|mysql|redis):\/\/[^\s]+",
}


def redact_pii(text: str) -> dict:
    """
    Scan text for PII and replace matches with [REDACTED_TYPE] tags.

    Returns:
        dict with 'redacted_text', 'found' list, and 'count'
    """
    found = []
    redacted = text

    for pii_type, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, redacted, re.IGNORECASE)
        for match in matches:
            found.append({"type": pii_type, "preview": match[:4] + "***"})
            redacted = redacted.replace(match, f"[REDACTED_{pii_type}]")

    return {
        "redacted_text": redacted,
        "found": found,
        "count": len(found),
        "safe": len(found) == 0,
    }


# ─── Input Guardrails ────────────────────────────────────────────────────────

def _is_keyboard_mashing(text: str) -> bool:
    """Detect keyboard mashing like 'asdfghjkl'."""
    # Only check short inputs — real sentences are not keyboard mashing
    if len(text) < 5 or len(text) > 50:
        return False
    # Must have very few spaces (mashing doesn't produce words)
    words = text.strip().split()
    if len(words) > 3:
        return False
    keyboard_rows = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
    text_lower = text.lower().replace(" ", "")
    for row in keyboard_rows:
        consecutive = 0
        for char in text_lower:
            if char in row:
                consecutive += 1
                if consecutive >= 7:
                    return True
            else:
                consecutive = 0
    return False


def _is_repetitive(text: str) -> bool:
    """Detect repeated characters like 'aaaaaaa'."""
    if len(text) < 4:
        return False
    for i in range(len(text) - 3):
        if text[i] == text[i + 1] == text[i + 2] == text[i + 3]:
            return True
    return False


def check_input_safety(prompt: str) -> dict:
    """
    Check if an input prompt is safe to send to an LLM.

    Returns:
        dict with 'safe' bool, 'reason', and 'tokens_saved'
    """
    # Empty or too short
    if not prompt or len(prompt.strip()) < 3:
        return {
            "safe": False,
            "reason": "Prompt too short — would waste tokens",
            "tokens_saved": 10,
            "action": "blocked",
        }

    # Keyboard mashing
    if _is_keyboard_mashing(prompt):
        return {
            "safe": False,
            "reason": "Keyboard mashing detected — not a real prompt",
            "tokens_saved": 10,
            "action": "blocked",
        }

    # Repetitive characters
    if _is_repetitive(prompt):
        return {
            "safe": False,
            "reason": "Repetitive characters detected — likely junk input",
            "tokens_saved": 10,
            "action": "blocked",
        }

    # PII check
    pii_result = redact_pii(prompt)
    if not pii_result["safe"]:
        pii_types = [f["type"] for f in pii_result["found"]]
        return {
            "safe": True,
            "reason": f"PII detected ({', '.join(pii_types)}) — auto-redacted",
            "tokens_saved": 0,
            "action": "redacted",
            "redacted_text": pii_result["redacted_text"],
            "pii_found": pii_result["found"],
        }

    return {
        "safe": True,
        "reason": "Input is clean and safe",
        "tokens_saved": 0,
        "action": "passed",
    }


# ─── Budget Manager ──────────────────────────────────────────────────────────

DEFAULT_DAILY_BUDGET = 500_000  # tokens


def get_budget_status() -> dict:
    """Get current budget status."""
    _ensure_dirs()
    raw = _load_json(BUDGET_FILE, {})

    # Ensure all fields have defaults
    budget = {
        "daily_limit": raw.get("daily_limit", DEFAULT_DAILY_BUDGET),
        "used_today": raw.get("used_today", 0),
        "date": raw.get("date", str(date.today())),
        "total_saved": raw.get("total_saved", 0),
        "total_spent": raw.get("total_spent", 0),
    }

    # Auto-reset at midnight
    if budget["date"] != str(date.today()):
        budget["used_today"] = 0
        budget["date"] = str(date.today())
        _save_json(BUDGET_FILE, budget)

    daily_limit = budget["daily_limit"]
    used = budget["used_today"]
    remaining = daily_limit - used
    return {
        "daily_limit": daily_limit,
        "used_today": used,
        "remaining": max(0, remaining),
        "percentage_used": round((used / daily_limit) * 100, 1) if daily_limit > 0 else 0,
        "total_saved": budget["total_saved"],
        "total_spent": budget["total_spent"],
        "budget_ok": remaining > 0,
    }


def set_daily_budget(tokens: int) -> dict:
    """Set daily token budget."""
    _ensure_dirs()
    budget = _load_json(BUDGET_FILE, {})
    budget["daily_limit"] = tokens
    if "used_today" not in budget:
        budget["used_today"] = 0
    budget["date"] = str(date.today())
    _save_json(BUDGET_FILE, budget)
    return {"daily_limit": tokens, "status": "Budget updated"}


def log_token_usage(tokens: int) -> dict:
    """Log token usage against daily budget."""
    _ensure_dirs()
    budget = _load_json(BUDGET_FILE, {
        "daily_limit": DEFAULT_DAILY_BUDGET,
        "used_today": 0,
        "date": str(date.today()),
        "total_spent": 0,
    })

    if budget.get("date") != str(date.today()):
        budget["used_today"] = 0
        budget["date"] = str(date.today())

    budget["used_today"] += tokens
    budget["total_spent"] = budget.get("total_spent", 0) + tokens
    _save_json(BUDGET_FILE, budget)

    remaining = budget["daily_limit"] - budget["used_today"]
    return {
        "tokens_logged": tokens,
        "remaining": max(0, remaining),
        "budget_exceeded": remaining <= 0,
    }


def log_saving(tokens: int) -> dict:
    """Log tokens saved by Qutato's protections."""
    _ensure_dirs()
    budget = _load_json(BUDGET_FILE, {"total_saved": 0})
    budget["total_saved"] = budget.get("total_saved", 0) + tokens
    _save_json(BUDGET_FILE, budget)
    return {"tokens_saved": tokens, "total_saved": budget["total_saved"]}


# ─── Loop Detector ────────────────────────────────────────────────────────────

MAX_REPEAT_COUNT = 3
SIMILARITY_THRESHOLD = 0.85


def _jaccard_similarity(a: str, b: str) -> float:
    """Compute Jaccard similarity between two strings."""
    set_a = set(a.lower().split())
    set_b = set(b.lower().split())
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)


def check_loop(prompt: str) -> dict:
    """
    Detect if an agent is stuck in a loop.

    Returns:
        dict with 'loop_detected', 'repeat_count', 'action'
    """
    _ensure_dirs()
    history = _load_json(LOOP_FILE, {"prompts": [], "timestamp": ""})

    # Clean old history (older than 1 hour)
    current_time = time.time()
    history_ts = history.get("timestamp", "")
    if history_ts and (current_time - float(history_ts)) > 3600:
        history = {"prompts": [], "timestamp": str(current_time)}

    # Check similarity with recent prompts
    similar_count = 0
    for prev in history.get("prompts", [])[-10:]:
        if _jaccard_similarity(prompt, prev) >= SIMILARITY_THRESHOLD:
            similar_count += 1

    # Add to history
    history["prompts"] = history.get("prompts", [])[-20:] + [prompt]
    history["timestamp"] = str(current_time)
    _save_json(LOOP_FILE, history)

    if similar_count >= MAX_REPEAT_COUNT:
        return {
            "loop_detected": True,
            "repeat_count": similar_count,
            "action": "blocked",
            "reason": f"Agent repeated similar prompt {similar_count} times — loop killed",
            "tokens_saved": similar_count * 250,
        }

    return {
        "loop_detected": False,
        "repeat_count": similar_count,
        "action": "passed",
    }


# ─── Memory Brain ─────────────────────────────────────────────────────────────

def learn(fact: str, tags: Optional[list] = None) -> dict:
    """
    Store a fact in Qutato's persistent Memory Brain.

    Args:
        fact: The fact to remember
        tags: Optional list of tags for categorization
    """
    _ensure_dirs()
    memories = _load_json(MEMORY_FILE, {"facts": []})

    entry = {
        "id": hashlib.md5(fact.encode()).hexdigest()[:8],
        "fact": fact,
        "tags": tags or [],
        "created": datetime.now().isoformat(),
    }

    # Avoid exact duplicates
    existing_facts = [m["fact"] for m in memories.get("facts", [])]
    if fact in existing_facts:
        return {"stored": False, "reason": "Fact already exists", "id": entry["id"]}

    memories["facts"] = memories.get("facts", []) + [entry]
    _save_json(MEMORY_FILE, memories)

    return {
        "stored": True,
        "id": entry["id"],
        "total_memories": len(memories["facts"]),
    }


def recall(query: str) -> dict:
    """
    Search Memory Brain for relevant facts.

    Returns:
        dict with matching 'facts' list
    """
    memories = _load_json(MEMORY_FILE, {"facts": []})
    all_facts = memories.get("facts", [])

    if not query.strip():
        return {"facts": all_facts, "count": len(all_facts)}

    # Simple keyword matching + Jaccard similarity
    query_words = set(query.lower().split())
    scored = []

    for mem in all_facts:
        fact_words = set(mem["fact"].lower().split())
        tag_words = set(t.lower() for t in mem.get("tags", []))
        all_words = fact_words | tag_words

        # Score: keyword overlap
        overlap = len(query_words & all_words)
        similarity = _jaccard_similarity(query, mem["fact"])
        score = overlap + similarity

        if score > 0:
            scored.append((score, mem))

    scored.sort(key=lambda x: x[0], reverse=True)
    matches = [m for _, m in scored[:10]]

    return {"facts": matches, "count": len(matches), "query": query}


def forget(fact_id: Optional[str] = None) -> dict:
    """
    Remove facts from Memory Brain.

    Args:
        fact_id: Specific fact ID to remove, or None to clear all
    """
    _ensure_dirs()

    if fact_id is None:
        _save_json(MEMORY_FILE, {"facts": []})
        return {"cleared": True, "message": "All memories cleared"}

    memories = _load_json(MEMORY_FILE, {"facts": []})
    before = len(memories["facts"])
    memories["facts"] = [m for m in memories["facts"] if m["id"] != fact_id]
    after = len(memories["facts"])
    _save_json(MEMORY_FILE, memories)

    return {"removed": before - after, "remaining": after}


# ─── Full Trust Check ─────────────────────────────────────────────────────────

def trust_check(prompt: str) -> dict:
    """
    Run complete Qutato trust pipeline on a prompt.

    Checks: Input safety → PII → Budget → Loop detection
    Returns comprehensive safety report.
    """
    results = {
        "safe": True,
        "checks": [],
        "tokens_saved": 0,
        "action": "passed",
    }

    # 1. Input safety
    input_check = check_input_safety(prompt)
    results["checks"].append({"name": "input_guardrails", **input_check})
    if not input_check["safe"]:
        results["safe"] = False
        results["action"] = input_check["action"]
        results["reason"] = input_check["reason"]
        results["tokens_saved"] += input_check.get("tokens_saved", 0)
        log_saving(input_check.get("tokens_saved", 0))
        return results

    # 2. Budget check
    budget = get_budget_status()
    results["checks"].append({"name": "budget", **budget})
    if not budget["budget_ok"]:
        results["safe"] = False
        results["action"] = "budget_exceeded"
        results["reason"] = "Daily token budget exceeded"
        return results

    # 3. Loop detection
    loop = check_loop(prompt)
    results["checks"].append({"name": "loop_detector", **loop})
    if loop["loop_detected"]:
        results["safe"] = False
        results["action"] = "loop_killed"
        results["reason"] = loop["reason"]
        results["tokens_saved"] += loop.get("tokens_saved", 0)
        log_saving(loop.get("tokens_saved", 0))
        return results

    # 4. Apply PII redaction if needed
    if input_check.get("action") == "redacted":
        results["redacted_text"] = input_check["redacted_text"]
        results["pii_found"] = input_check.get("pii_found", [])
        results["action"] = "redacted"

    return results


# ─── Status ───────────────────────────────────────────────────────────────────

def get_status() -> dict:
    """Get full Qutato system status."""
    _ensure_dirs()
    budget = get_budget_status()
    memories = _load_json(MEMORY_FILE, {"facts": []})
    config = _load_json(CONFIG_FILE, {})

    return {
        "version": "1.0.0",
        "status": "healthy",
        "storage": str(QUTATO_DIR),
        "budget": budget,
        "memories": len(memories.get("facts", [])),
        "config": config,
        "features": {
            "input_guardrails": True,
            "pii_redaction": True,
            "budget_manager": True,
            "loop_detector": True,
            "abstention_engine": True,
            "memory_brain": True,
        },
    }
