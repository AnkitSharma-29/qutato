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

    def should_abstain(self, 
                       model_confidence, 
                       task_urgency, 
                       sensitivity_score,
                       has_memory_match=False):
        """
        Calculate adaptive threshold and decide whether to abstain.
        Enhanced with Memory Context: If memory has a match, we can trust the model more.
        """
        threshold = self.calculate_adaptive_threshold(model_confidence, task_urgency, sensitivity_score)
        
        # Memory Offset: If we have context, lower the threshold (make it easier to say yes)
        if has_memory_match:
            threshold -= 0.15 # 15% boost to trust
            threshold = max(0.1, threshold) # Cap at 0.1
            
        return model_confidence < threshold, threshold

# Singleton for the engine
abstention_engine = AbstentionEngine()
