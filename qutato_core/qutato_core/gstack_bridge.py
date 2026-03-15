import sys
import json
import httpx
from qutato_core.engine.adversarial_prober import adversarial_prober

class GStackBridge:
    """
    Bridge for gstack compatibility.
    Allows Bun/Claude Code to call Qutato vetting logic.
    """
    def __init__(self, gateway_url="http://localhost:8000"):
        self.gateway_url = gateway_url

    def vet_prompt(self, prompt: str, role: str = None):
        """
        Directly vet a prompt using the core engine.
        Useful for local CLI calls from gstack.
        """
        return adversarial_prober.probe(prompt, role=role)

    def remote_vet(self, prompt: str, role: str = None, api_key: str = "qutato_admin_secret_key"):
        """
        Vet a prompt via the Gateway API.
        """
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{self.gateway_url}/v1/chat/completions",
                    headers={
                        "X-API-KEY": api_key,
                        "X-QUTATO-ROLE": role or "Generic",
                        "X-LLM-API-KEY": "mock-key"
                    },
                    json={
                        "model": "gpt-4o",
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    timeout=5.0
                )
                if response.status_code == 403:
                    return {"is_safe": False, "reason": response.json().get("detail")}
                return {"is_safe": True, "response": response.json()}
        except Exception as e:
            return {"is_safe": False, "error": str(e)}

def handle_cli():
    """CLI Entry point for `qutato gstack`"""
    import argparse
    parser = argparse.ArgumentParser(description="Qutato gstack Bridge")
    parser.add_argument("--role", help="Engineering role (CEO, Architect, Security, QA)")
    parser.add_argument("--prompt", help="Prompt to vet")
    
    args = parser.parse_args()
    
    bridge = GStackBridge()
    report = bridge.vet_prompt(args.prompt, role=args.role)
    
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    handle_cli()
