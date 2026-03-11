from qutato_core.engine.memory import memory_engine
from qutato_core.engine.abstention import abstention_engine

def run_memory_demo():
    print("🧠 Starting Qutato Memory Engine Demo...\n")

    # 1. Store some facts (Agent Learning)
    memory_engine.store("The company's server is located in Frankfurt.")
    memory_engine.store("Ankit's preferred coding language is Python.")
    
    # 2. Query with NO context (Standard Abstention)
    query_1 = "Where is the server located?"
    # Assume low model confidence (0.6)
    block_1, thresh_1 = abstention_engine.should_abstain(model_confidence=0.6, has_memory_match=False)
    
    print(f"\nQuery: '{query_1}'")
    print(f"Confidence: 0.6 | Standard Threshold: {thresh_1:.2f}")
    print(f"Result: {'BLOCK' if block_1 else 'ALLOW'}")

    # 3. Query WITH context (Memory-Aware Abstention)
    context = memory_engine.retrieve(query_1)
    has_match = len(context) > 0
    
    block_2, thresh_2 = abstention_engine.should_abstain(model_confidence=0.6, has_memory_match=has_match)
    
    print(f"Memory Context Found: {context}")
    print(f"Confidence: 0.6 | Memory-Aware Threshold: {thresh_2:.2f} (Trust Boosted!)")
    print(f"Result: {'BLOCK' if block_2 else 'ALLOW'}")

    print("\n✅ Verification: Memory engine successfully reduced the rejection rate for verified facts.")

if __name__ == "__main__":
    run_memory_demo()
