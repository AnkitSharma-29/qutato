import re
from typing import Tuple, Dict

class PromptDetector:
    """
    Analyzes input prompts for quality, sensitive topics, and junk patterns.
    """
    def __init__(self):
        # Patterns for junk/spam/nonsense
        self.junk_patterns = [
            r"^[asdfghjkl;qwertyuiop]+$", # Keyboard mashing
            r"^(\w)\1{5,}$",             # Repeated characters
            r"^.{1,3}$",                 # Too short
        ]
        
        # Sensitive topics that might trigger stricter abstention
        self.sensitive_keywords = ["medical", "legal", "finance", "password", "secret", "pii"]

    def analyze_prompt(self, prompt: str) -> Dict:
        """
        Analyze a prompt and return a safety report.
        """
        prompt_lower = prompt.lower()
        
        # 1. Check for Junk
        is_junk = any(re.match(pattern, prompt_lower) for pattern in self.junk_patterns)
        
        # 2. Check for Sensitivity
        is_sensitive = any(keyword in prompt_lower for keyword in self.sensitive_keywords)
        
        # 3. Calculate "Prompt Quality" (Simplified)
        quality_score = 1.0
        if is_junk:
            quality_score = 0.1
        elif len(prompt) < 10:
            quality_score = 0.5
            
        return {
            "is_junk": is_junk,
            "is_sensitive": is_sensitive,
            "quality_score": quality_score
        }

prompt_detector = PromptDetector()
