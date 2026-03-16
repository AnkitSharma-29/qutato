import re
from typing import Dict, List, Tuple

class PIIRedactor:
    """
    High-performance PII Redaction Engine for Qutato Core.
    Protects user privacy by masking sensitive data before it reaches the LLM.
    """
    def __init__(self):
        # Optimized regex patterns for common PII
        self.patterns = {
            "EMAIL": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
            "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b",
            "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
            "PHONE": r"\b(?:\+?\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b",
            "API_KEY": r"(?i)(?:key|secret|token|auth|password|pwd)(?:[:=]|\s+is\s+)\s*['\"]?([a-zA-Z0-9_\-\.\~]{16,})['\"]?",
        }
        
        # Compiled patterns for speed
        self.compiled_patterns = {name: re.compile(pat) for name, pat in self.patterns.items()}

    def redact(self, text: str, bypass: bool = False) -> str:
        """
        Redacts PII from the given text.
        If bypass is True, redaction is skipped (e.g., for intentional transactions).
        """
        if bypass or not text:
            return text

        redacted_text = text
        for name, pattern in self.compiled_patterns.items():
            if name == "API_KEY":
                # Special handling for API keys to preserve the label but mask the value
                redacted_text = self._redact_secrets(redacted_text, pattern)
            else:
                redacted_text = pattern.sub(f"[REDACTED_{name}]", redacted_text)
                
        return redacted_text

    def _redact_secrets(self, text: str, pattern: re.Pattern) -> str:
        """Helper to redact secrets while preserving surrounding context."""
        def replace_func(match):
            full_match = match.group(0)
            secret_value = match.group(1)
            # Replace only the secret value within the full match string
            masked_value = "*" * 8 + secret_value[-4:] if len(secret_value) > 4 else "*" * 8
            return full_match.replace(secret_value, f"[REDACTED_SECRET_{masked_value}]")
            
        return pattern.sub(replace_func, text)

    def analyze(self, text: str) -> Dict[str, int]:
        """Analyzes text and returns counts of detected PII types."""
        findings = {}
        for name, pattern in self.compiled_patterns.items():
            matches = pattern.findall(text)
            if matches:
                findings[name] = len(matches)
        return findings

# Global singleton
pii_redactor = PIIRedactor()
