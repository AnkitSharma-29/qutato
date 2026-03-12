import json
import os
import time
from typing import List, Dict, Optional, Any

class Fact:
    def __init__(self, text: str, metadata: Optional[Dict[str, Any]] = None, timestamp: Optional[float] = None):
        """
        Record of a single memorized fact.
        Explicitly coerced to standard types for senior-dev interoperability.
        """
        self.text: str = str(text)
        self.timestamp: float = float(timestamp or time.time())
        self.metadata: Dict[str, Any] = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text, 
            "timestamp": self.timestamp, 
            "metadata": self.metadata
        }

class QutatoMemory:
    """
    Persistent Memory Engine for Qutato.
    Saves and loads facts from a local JSON database using atomic writes.
    """
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            home = os.path.expanduser("~")
            qutato_dir = os.path.join(home, ".qutato")
            os.makedirs(qutato_dir, exist_ok=True)
            db_path = os.path.join(qutato_dir, "qutato_memory.json")
        self.db_path: str = str(db_path)
        self.memories: List[Fact] = []
        self._load()

    def _load(self):
        """Loads and vettes memory data from disk with error recovery."""
        if not os.path.exists(self.db_path):
            return

        try:
            with open(self.db_path, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.memories = []
                    for item in data:
                        if isinstance(item, dict) and "text" in item:
                            self.memories.append(Fact(
                                text=str(item.get("text", "")),
                                metadata=item.get("metadata"),
                                timestamp=item.get("timestamp")
                            ))
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️ [Qutato Memory] Warning: Memory file corrupted ({str(e)}).")

    def _save(self):
        """Atomic write using temp-rename to prevent data loss during power failure/crash."""
        temp_path = self.db_path + ".tmp"
        try:
            with open(temp_path, "w") as f:
                json.dump([m.to_dict() for m in self.memories], f, indent=2)
            os.replace(temp_path, self.db_path)
        except IOError as e:
            print(f"❌ [Qutato Memory] Critical Error: Failed to save memories! {str(e)}")
            if os.path.exists(temp_path):
                try: os.remove(temp_path)
                except: pass

    def store(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a new fact and persist to disk atomically."""
        clean_text = str(text).strip()
        if not clean_text:
            return
        fact = Fact(clean_text, metadata)
        self.memories.append(fact)
        self._save()
        preview = clean_text[:50]
        print(f"🧠 [Memory] Persisted fact: '{preview}...'")

    def retrieve(self, query: str, limit: int = 3) -> List[str]:
        """Keyword-based retrieval using relevance scoring."""
        clean_query = str(query).strip()
        if not clean_query:
            return []
            
        keywords = clean_query.lower().split()
        scored_memories = []
        
        for fact in self.memories:
            score = sum(1 for word in keywords if word in fact.text.lower())
            if score > 0:
                scored_memories.append((score, fact.text))
        
        # Sort by relevance (highest score first)
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        # Extract matches
        matches = [text for _, text in scored_memories]
        return matches[:limit]

    def clear(self):
        """Flush the entire memory bank and delete disk file."""
        self.memories = []
        if os.path.exists(self.db_path):
            try: os.remove(self.db_path)
            except: pass

memory_engine = QutatoMemory()
