import os

class CoreConfig:
    # Redis Defaults
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    
    # Storage Paths
    def get_stats_path(self):
        home = os.path.expanduser("~")
        qutato_dir = os.path.join(home, ".qutato")
        return os.path.join(qutato_dir, "qutato_stats.json")

core_config = CoreConfig()
