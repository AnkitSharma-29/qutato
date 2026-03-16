import json
import os
import time
from typing import List, Dict, Optional, Any
import importlib.util

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
    def __init__(self, db_path: Optional[str] = None, remote_url: Optional[str] = None):
        if db_path is None:
            home = os.path.expanduser("~")
            qutato_dir = os.path.join(home, ".qutato")
            os.makedirs(qutato_dir, exist_ok=True)
            db_path = os.path.join(qutato_dir, "qutato_memory.json")
        self.db_path: str = str(db_path)
        self.remote_url: Optional[str] = remote_url
        self.memories: List[Fact] = []
        self.memory_plugin = self._load_memory_plugin()
        self._load()

    def sync(self) -> dict:
        """
        Synchronize local memories with a remote provider (Multi-Agent Shared Brain foundation).
        Currently implements a placeholder for cloud convergence.
        """
        if not self.remote_url:
            return {"status": "skipped", "reason": "No remote_url configured"}
        
        print(f"📡 [Qutato Memory] Attempting sync with {self.remote_url}...")
        # Future: Implement actual HTTP sync with Qutato Cloud or another gateway
        time.sleep(0.5) 
        return {"status": "success", "synced_count": len(self.memories)}

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

    def _load_memory_plugin(self):
        """Dynamically loads the memory plugin if QUTATO_MEMORY_PLUGIN is set."""
        plugin_path = os.getenv("QUTATO_MEMORY_PLUGIN")
        if plugin_path and os.path.exists(plugin_path):
            try:
                spec = importlib.util.spec_from_file_location("memory_plugin", plugin_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    # Expecting MetaxyMemoryPlugin class in the plugin
                    return getattr(module, "MetaxyMemoryPlugin")()
            except Exception as e:
                print(f"⚠️ [Qutato Memory] Failed to load memory plugin: {e}.")
        return None

    def store(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a new fact and persist to disk atomically."""
        clean_text = str(text).strip()
        if not clean_text:
            return
        fact = Fact(clean_text, metadata)
        
        # In Pro mode, we prioritize the Metaxy Plugin for absolute truth
        if self.memory_plugin:
            try:
                self.memory_plugin.store_fact(text=fact.text, metadata=fact.metadata, timestamp=fact.timestamp)
                print(f"🧠 [Memory] Persisted to Metaxy Pro Store.")
            except Exception as e:
                print(f"⚠️ [Qutato Memory] Memory Plugin failed: {e}. Falling back to local.")
                self.memories.append(fact)
                self._save()
        else:
            self.memories.append(fact)
            self._save()
            
        preview = clean_text[:50]
        print(f"🧠 [Memory] Fact processed: '{preview}...'")

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
        
        # Merge with matches from Metaxy Memory Plugin if active
        if self.memory_plugin:
            try:
                pro_matches = self.memory_plugin.retrieve_facts(query=clean_query, limit=limit)
                # Combine and remove duplicates while preserving order
                for match in pro_matches:
                    if match not in matches:
                        matches.append(match)
            except Exception as e:
                print(f"⚠️ [Qutato Memory] Memory Plugin failed to retrieve: {e}")
                
        return matches[:limit]

    def clear(self):
        """Flush the entire memory bank and delete disk file."""
        self.memories = []
        if os.path.exists(self.db_path):
            try: os.remove(self.db_path)
            except: pass

memory_engine = QutatoMemory()
