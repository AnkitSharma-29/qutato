import time
from typing import List, Dict, Optional

class Fact:
    def __init__(self, text: str, metadata: Optional[Dict] = None):
        self.text = text
        self.timestamp = time.time()
        self.metadata = metadata or {}

class QutatoMemory:
    """
    A lightweight Memory Engine for Qutato.
    Focuses on fact persistence and context retrieval.
    """
    def __init__(self):
        self.memories: List[Fact] = []

    def store(self, text: str, metadata: Optional[Dict] = None):
        """Add a new fact to memory."""
        fact = Fact(text, metadata)
        self.memories.append(fact)
        # Note: In production, this would involve embedding generation and vector storage.
        print(f"[Memory] Stored fact: '{text[:50]}...'")

    def retrieve(self, query: str, limit: int = 3) -> List[str]:
        """
        Retrieve relevant context for a query.
        (Simple keyword-based matching for the Open-Core version)
        """
        # Enterprise version uses Vector Search / Embeddings
        keywords = query.lower().split()
        scored_memories = []
        
        for fact in self.memories:
            score = sum(1 for word in keywords if word in fact.text.lower())
            if score > 0:
                scored_memories.append((score, fact.text))
        
        # Sort by score and then by most recent
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        results = [text for score, text in scored_memories[:limit]]
        
        return results

    def clear(self):
        self.memories = []

# Global memory instance for the core
memory_engine = QutatoMemory()
