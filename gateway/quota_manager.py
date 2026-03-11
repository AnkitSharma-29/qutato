import redis
from gateway.config import settings

class QuotaManager:
    def __init__(self):
        self.r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)

    def check_quota(self, user_id: str):
        # Placeholder logic for quota check
        limit = self.r.get(f"quota:limit:{user_id}")
        if limit is None:
            # Default limit of 1000 tokens for demo
            self.r.set(f"quota:limit:{user_id}", 1000)
            limit = 1000
        
        used = self.r.get(f"quota:used:{user_id}") or 0
        return int(used) < int(limit)

    def increment_usage(self, user_id: str, tokens: int):
        self.r.incrby(f"quota:used:{user_id}", tokens)

quota_manager = QuotaManager()
