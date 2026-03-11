import numpy as np

class AbstentionEngine:
    def __init__(self, base_threshold=0.85):
        self.base_threshold = base_threshold

    def calculate_adaptive_threshold(self, confidence, urgency, sensitivity=1.0, alpha=0.1, beta=0.05):
        """
        Implementation of the adaptive threshold equation:
        Tdynamic(c, u) = Tbase + alpha * sensitivity(c) - beta * trust(u)
        
        Note: Simplified for the initial version.
        """
        # Tdynamic = Tbase + α * sensitivity(c) - β * urgency(u)
        # We want to increase the threshold (be more restrictive) when sensitivity is high
        # We want to decrease it (be more helpful) when urgency is high
        
        dynamic_threshold = self.base_threshold + (alpha * sensitivity) - (beta * urgency)
        return np.clip(dynamic_threshold, 0.0, 1.0)

    def should_abstain(self, model_confidence, task_urgency, sensitivity_score):
        threshold = self.calculate_adaptive_threshold(model_confidence, task_urgency, sensitivity_score)
        
        return model_confidence < threshold, threshold

# Singleton for the engine
abstention_engine = AbstentionEngine()
