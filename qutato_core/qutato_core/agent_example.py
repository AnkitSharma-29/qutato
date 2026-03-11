from qutato_core.engine.abstention import abstention_engine
import time

class QutatoSupervisor:
    """
    A Qutato Supervisor for Agentic Systems.
    It monitors agent thoughts and outputs before they are finalized.
    """
    def __init__(self, sensitivity_threshold=0.8):
        self.threshold = sensitivity_threshold

    def validate_action(self, agent_thought: str, confidence: float):
        """
        Validate if an agent's proposed action is safe to execute.
        """
        print(f"\n[Qutato Supervisor] Inspecting Thought: '{agent_thought[:50]}...'")
        
        # Use Qutato math to vet the agent
        should_abstain, threshold = abstention_engine.should_abstain(
            model_confidence=confidence,
            task_urgency=0.7, # Agents often have high urgency
            sensitivity_score=0.5
        )
        
        if should_abstain:
            print(f"⚠️  [BLOCK] Agent confidence too low ({confidence} < {threshold}). Blocking action.")
            return False
        
        print(f"✅ [ALLOW] Action vetted. Proceeding.")
        return True

# --- Example Agentic Loop ---
def run_agent_loop():
    supervisor = QutatoSupervisor()
    
    # Mocking an agent that tries 3 steps
    actions = [
        {"thought": "I will search for public data.", "conf": 0.9},
        {"thought": "I will attempt to access internal server logs.", "conf": 0.4}, # Risky/Low confidence
        {"thought": "I will summarize the findings.", "conf": 0.85},
    ]

    for action in actions:
        if supervisor.validate_action(action["thought"], action["conf"]):
            print(f"Agent executing: {action['thought']}")
        else:
            print("Agent recovering: Recalculating safer path...")
        time.sleep(1)

if __name__ == "__main__":
    run_agent_loop()
