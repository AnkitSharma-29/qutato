import os
import sys
import time
from datetime import datetime

# Ensure we can import from core and research vault
sys.path.append(os.path.join(os.getcwd(), "qutato_core"))
sys.path.append(os.path.dirname(os.getcwd())) # parent of qutato is scratch

from qutato_core.engine.memory import QutatoMemory

def verify_versioned_memory():
    print("--- Testing Metaxy-Powered Versioned Memory ---")
    
    # 1. Setup paths
    memory_plugin_path = r"c:\Users\ankit\.gemini\antigravity\scratch\qutato_research\memory_plugin.py"
    os.environ["QUTATO_MEMORY_PLUGIN"] = memory_plugin_path
    
    # 2. Instantiate QutatoMemory to load plugin
    mem = QutatoMemory()
    
    if mem.memory_plugin:
        print("✅ Success: Memory Plugin loaded dynamically.")
        
        # 3. Store some initial facts
        print("📝 Storing initial facts...")
        mem.store("The sun is a star.")
        mem.store("Water freezes at 0 degrees Celsius.")
        
        # 4. Create a snapshot
        print("📸 Creating snapshot 'baseline'...")
        snap_id = mem.memory_plugin.create_snapshot("Baseline facts")
        if not snap_id:
            print("❌ Error: Failed to create snapshot.")
            return

        # 5. Store more facts (some potentially wrong/bad)
        print("📝 Storing more facts (post-snapshot)...")
        mem.store("The moon is made of green cheese.")
        
        # 6. Verify retrieval includes the new fact
        matches = mem.retrieve("moon")
        if any("green cheese" in m for m in matches):
            print("✅ Verified: New fact is present in memory.")
        else:
            print("❌ Error: New fact not found.")
            
        # 7. Rollback to the snapshot
        print(f"⏪ Rolling back to {snap_id}...")
        success = mem.memory_plugin.rollback(snap_id)
        if success:
            print("✅ Success: Rollback completed.")
            
            # 8. Verify the bad fact is GONE
            matches = mem.retrieve("moon")
            if any("green cheese" in m for m in matches):
                print("❌ Error: Rollback failed! Bad fact still persists.")
            else:
                print("✅ FINAL VERIFIED: The Brain successfully forgot the 'poisoned' fact! Memory restored.")
        else:
            print("❌ Error: Rollback failed.")
    else:
        print("❌ Error: Memory Plugin failed to load.")

if __name__ == "__main__":
    verify_versioned_memory()
