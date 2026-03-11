import httpx
import json

class QutatoClient:
    def __init__(self, qutato_api_key: str, base_url: str = "http://localhost:8000/v1"):
        self.qutato_api_key = qutato_api_key
        self.base_url = base_url

    def complete(self, model: str, messages: list, llm_api_key: str, sensitive: bool = False, user_id: str = "default_user", **kwargs):
        """
        Talk to the Qutato Smart Core.
        Hides all LiteLLM/Provider complexity.
        """
        url = f"{self.base_url}/chat/completions"
        headers = {
            "X-API-KEY": self.qutato_api_key,
            "X-LLM-API-KEY": llm_api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "user_id": user_id,
            "sensitive": sensitive,
            **kwargs
        }
        
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

# Convenient wrapper
def create_client(api_key: str, base_url: str = "http://localhost:8000/v1"):
    return QutatoClient(qutato_api_key=api_key, base_url=base_url)
