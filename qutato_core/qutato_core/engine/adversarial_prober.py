import re
from typing import Dict, List

class AdversarialProber:
    """
    Detects adversarial patterns such as prompt injection, jailbreaks,
    and context hijacking.
    """
    def __init__(self):
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
        
        return {
            "is_adversarial": is_adversarial,
            "matched_patterns": matched,
            "risk_level": "high" if is_adversarial else "low"
        }

# Global singleton
adversarial_prober = AdversarialProber()
