import re
from typing import Dict, List

class AdversarialProber:
    """
    Detects adversarial patterns such as prompt injection, jailbreaks,
    and context hijacking.
    """
    def __init__(self):
        # Known jailbreak and injection patterns
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

    def probe(self, prompt: str) -> Dict:
        """
        Scan a prompt for adversarial intent.
        Returns a report with 'is_adversarial' and 'matched_patterns'.
        """
        matched = []
        for pattern in self.adversarial_patterns:
            if re.search(pattern, prompt):
                matched.append(pattern)

        is_adversarial = len(matched) > 0
        
        return {
            "is_adversarial": is_adversarial,
            "matched_patterns": matched,
            "risk_level": "high" if is_adversarial else "low"
        }

# Global singleton
adversarial_prober = AdversarialProber()
