import re
from typing import Dict, List
import os
import importlib.util
import hashlib

class AdversarialProber:
    """
    Detects adversarial patterns such as prompt injection, jailbreaks,
    and context hijacking.
    """
    def __init__(self):
        self.safety_cache_plugin = self._load_safety_cache_plugin()
        # Known jailbreak and injection patterns (Generic)
        self.adversarial_patterns = [
            # Prompt Injection
            r"(?i)ignore (all )?previous instructions",
            r"(?i)disregard (all )?previous instructions",
            r"(?i)you are now in (debug|developer|admin) mode",
            r"(?i)system (override|bypass)",
            
            # Jailbreaks (DAN-style)
            r"(?i)you are (now )?DAN",
            r"(?i)do anything now",
            r"(?i)stay in character",
            r"(?i)you are (now )?unfiltered",
            
            # Context Hijacking / Malicious Framing
            r"(?i)(how to|making) (bomb|drug|weapon|illegal|poison)",
            r"(?i)hypothetically speaking, how would one",
            r"(?i)for educational purposes only, (explain|show) how to",
        ]

        # gstack-inspired Role-Specific Patterns
        self.role_patterns = {
            "CEO": [
                r"(?i)just ship it regardless of (safety|security|budget)",
                r"(?i)pivot everything to crypto/web3 without a plan",
                r"(?i)ignore technical debt",
            ],
            "Architect": [
                r"(?i)use a global variable for state",
                r"(?i)tightly couple these services",
                r"(?i)skip the database migration",
            ],
            "Security": [
                r"(?i)hardcode the secret",
                r"(?i)disable (auth|ssl|tls|cors)",
                r"(?i)use md5 for (passwords|security)",
            ],
            "QA": [
                r"(?i)skip the tests",
                r"(?i)production is the test environment",
                r"(?i)manual testing is enough",
            ]
        }

    def probe(self, prompt: str, role: str = None) -> Dict:
        """
        Scan a prompt for adversarial intent.
        Optionally takes a 'role' to apply specialized role-based vetting.
        """
        # 0. Check Safety Cache
        prompt_hash = hashlib.sha256(f"{role or 'generic'}:{prompt}".encode()).hexdigest()
        if self.safety_cache_plugin:
            try:
                cached = self.safety_cache_plugin.check_cache(prompt_hash)
                if cached is not None:
                    print(f"⚡ [Qutato Safety] Cache hit for prompt ({prompt_hash[:8]}).")
                    return cached
            except Exception as e:
                print(f"⚠️ [Qutato Safety] Cache check failed: {e}")

        matched = []
        
        # 1. Generic Checks
        for pattern in self.adversarial_patterns:
            if re.search(pattern, prompt):
                matched.append(pattern)

        # 2. Role-Specific Checks (gstack integration)
        if role and role in self.role_patterns:
            for pattern in self.role_patterns.get(role, []):
                if re.search(pattern, prompt):
                    matched.append(f"[{role}] {pattern}")

        is_adversarial = len(matched) > 0
        result = {
            "is_adversarial": is_adversarial,
            "matched_patterns": matched,
            "risk_level": "high" if is_adversarial else "low"
        }
        
        # 3. Update Safety Cache
        if self.safety_cache_plugin:
            try:
                self.safety_cache_plugin.update_cache(prompt_hash, result)
            except Exception as e:
                print(f"⚠️ [Qutato Safety] Cache update failed: {e}")

        return result

    def _load_safety_cache_plugin(self):
        """Dynamically loads the safety cache plugin if QUTATO_SAFETY_CACHE_PLUGIN is set."""
        plugin_path = os.getenv("QUTATO_SAFETY_CACHE_PLUGIN")
        if plugin_path and os.path.exists(plugin_path):
            try:
                spec = importlib.util.spec_from_file_location("safety_cache_plugin", plugin_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    # Expecting MetaxySafetyCachePlugin class
                    return getattr(module, "MetaxySafetyCachePlugin")()
            except Exception as e:
                print(f"⚠️ [Qutato Safety] Failed to load safety cache plugin: {e}.")
        return None

# Global singleton
adversarial_prober = AdversarialProber()
