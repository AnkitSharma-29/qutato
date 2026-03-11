import redis
import json
import os
from qutato_core.config import core_config

class QuotaManager:
    def __init__(self, stats_path: str = None):
        if stats_path is None:
            stats_path = core_config.get_stats_path()
            
        self.stats_path = stats_path
        self._stats = {"saved_calls": 0, "saved_tokens": 0}
        self._load_local_stats()
        
        try:
            self.r = redis.Redis(
                host=core_config.REDIS_HOST, 
                port=core_config.REDIS_PORT, 
                decode_responses=True
            )
            self.r.ping()
            self.use_redis = True
        except:
            print(f"[Warning] Redis not found. Using local stats file: {self.stats_path}")
            self.use_redis = False

    def _load_local_stats(self):
        if os.path.exists(self.stats_path):
            try:
                with open(self.stats_path, "r") as f:
                    self._stats = json.load(f)
            except:
                pass

    def _save_local_stats(self):
        with open(self.stats_path, "w") as f:
            json.dump(self._stats, f)

    def check_quota(self, user_id: str):
        if not self.use_redis: return True
        # Placeholder logic for quota check
        # Placeholder logic for quota check
        limit = self.r.get(f"quota:limit:{user_id}")
        if limit is None:
            # Default limit of 1000 tokens for demo
            self.r.set(f"quota:limit:{user_id}", 1000)
            limit = 1000
        
        used = self.r.get(f"quota:used:{user_id}") or 0
        return int(used) < int(limit)

    def increment_usage(self, user_id: str, tokens: int):
        if self.use_redis:
            self.r.incrby(f"quota:used:{user_id}", tokens)

    def log_savings(self, user_id: str, estimated_tokens: int = 250):
        if self.use_redis:
            self.r.incr(f"quota:saved_calls:{user_id}")
            self.r.incrby(f"quota:saved_tokens:{user_id}", estimated_tokens)
        else:
            self._stats["saved_calls"] += 1
            self._stats["saved_tokens"] += estimated_tokens
            self._save_local_stats()

    def get_savings(self, user_id: str):
        if self.use_redis:
            calls = self.r.get(f"quota:saved_calls:{user_id}") or 0
            tokens = self.r.get(f"quota:saved_tokens:{user_id}") or 0
            return int(calls), int(tokens)
        
        # Ensure we have the latest from disk in case another process updated it
        self._load_local_stats()
        return self._stats.get("saved_calls", 0), self._stats.get("saved_tokens", 0)

quota_manager = QuotaManager()
