import json
import os
import time
from typing import List, Dict, Optional

class Fact:
    def __init__(self, text: str, metadata: Optional[Dict] = None, timestamp: float = None):
        self.text = text
        self.timestamp = timestamp or time.time()
        self.metadata = metadata or {}

    def to_dict(self):
        return {"text": self.text, "timestamp": self.timestamp, "metadata": self.metadata}

class QutatoMemory:
    """
    Persistent Memory Engine for Qutato.
    Saves and loads facts from a local JSON database.
    """
    def __init__(self, db_path: str = "qutato_memory.json"):
        self.db_path = db_path
        self.memories: List[Fact] = []
        self._load()

    def _load(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, "r") as f:
                data = json.load(f)
                self.memories = [Fact(**item) for item in data]

    def _save(self):
        with open(self.db_path, "w") as f:
            json.dump([m.to_dict() for m in self.memories], f, indent=2)

    def store(self, text: str, metadata: Optional[Dict] = None):
        """Add a new fact and persist to disk."""
        fact = Fact(text, metadata)
        self.memories.append(fact)
        self._save()
        print(f"[Memory] Persisted fact: '{text[:50]}...'")

    def retrieve(self, query: str, limit: int = 3) -> List[str]:
        keywords = query.lower().split()
        scored_memories = []
        
        for fact in self.memories:
            score = sum(1 for word in keywords if word in fact.text.lower())
            if score > 0:
                scored_memories.append((score, fact.text))
        
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        return [text for score, text in scored_memories[:limit]]

    def clear(self):
        self.memories = []
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

memory_engine = QutatoMemory()
