import os
import importlib.util

class BasicAbstentionEngine:
    """Standard, reliable threshold logic for open-source users."""
    def __init__(self, base_threshold=0.85):
        self.base_threshold = base_threshold

    def should_abstain(self, model_confidence, task_urgency, sensitivity_score, **kwargs):
        # Reliable threshold: increases with sensitivity, decreases with urgency
        threshold = self.base_threshold + (0.1 * sensitivity_score) - (0.05 * task_urgency)
        return model_confidence < threshold, threshold

class AbstentionEngine:
    """
    The Trust Proxy. Dynamically loads advanced research logic if available,
    otherwise falls back to the Basic Engine.
    """
    def __init__(self):
        self.plugin_path = os.getenv("QUTATO_ABSTENTION_PLUGIN")
        self.engine = self._load_engine()

    def _load_engine(self):
        plugin_path = self.plugin_path
        if plugin_path and os.path.exists(plugin_path):
            try:
                spec = importlib.util.spec_from_file_location("advanced_engine", plugin_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    # Expecting AdvancedAbstentionEngine class in the plugin
                    return getattr(module, "AdvancedAbstentionEngine")()
            except Exception as e:
                print(f"⚠️ [Qutato] Failed to load abstention plugin: {e}. Falling back to Basic Engine.")
        
        return BasicAbstentionEngine()

    def should_abstain(self, *args, **kwargs):
        """Passes all data directly to the active engine (Basic or Advanced)."""
        return self.engine.should_abstain(*args, **kwargs)

# Singleton for the engine
abstention_engine = AbstentionEngine()
