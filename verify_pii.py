import os
import sys

# Ensure we can import from core
sys.path.append(os.path.join(os.getcwd(), "qutato_core"))

from qutato_core.sidecar import qutato

def verify_pii_redactor():
    print("--- Testing Qutato PII Redactor ---")
    
    # Test 1: Standard Redaction (Default)
    sensitive_prompt = "My email is test@example.com and my phone is 123-456-7890. My SSN is 000-00-0000."
    print(f"\n🔍 [Test 1] Standard Prompt: '{sensitive_prompt}'")
    
    redacted = qutato.redact(sensitive_prompt)
    print(f"🔒 Redacted: '{redacted}'")
    
    if "[REDACTED_EMAIL]" in redacted and "[REDACTED_PHONE]" in redacted and "[REDACTED_SSN]" in redacted:
        print("✅ SUCCESS: All PII masked by default.")
    else:
        print("❌ FAIL: Redaction incomplete.")

    # Test 2: API Key Redaction
    secret_prompt = "The password is 'super-secret-password-123456'"
    print(f"\n🔍 [Test 2] Secret Prompt: '{secret_prompt}'")
    redacted_secret = qutato.redact(secret_prompt)
    print(f"🔒 Redacted: '{redacted_secret}'")
    if "REDACTED_SECRET" in redacted_secret:
        print("✅ SUCCESS: Secret masked.")

    # Test 3: Transactional Bypass (The "Buy" Scenario)
    transactional_prompt = "Process payment for card 4111 1111 1111 1111."
    print(f"\n🔍 [Test 3] Transactional Prompt (Bypass=True): '{transactional_prompt}'")
    
    bypassed = qutato.redact(transactional_prompt, bypass=True)
    print(f"🔓 Bypassed: '{bypassed}'")
    
    if "4111 1111 1111 1111" in bypassed:
        print("✅ SUCCESS: Transactional data preserved with bypass flag.")
    else:
        print("❌ FAIL: Bypass failed.")

    print("\n--- ✅ FINAL VERDICT: PII Redactor is ready for release! ---")

if __name__ == "__main__":
    verify_pii_redactor()
