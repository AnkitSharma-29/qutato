import os
import sys
import asyncio
from dotenv import load_dotenv

# Set these before importing browser_use
from langchain_openai import ChatOpenAI

try:
    from browser_use import Agent
except ImportError:
    print("❌ browser-use is not installed. Run: pip install browser-use langchain-openai playwright")
    sys.exit(1)

from qutato_devkit.trust_engine import trust_check


async def run_qutato_browser(prompt: str, api_key: str):
    """
    1. Pass the prompt through Qutato's Trust Layer
    2. If safe, execute it using the Browser-Use agent
    """
    print(f"🛡️ Qutato is vetting your prompt: '{prompt}'...")
    
    # --- 1. Qutato Trust Check ---
    trust_report = trust_check(prompt)
    if not trust_report["safe"]:
        print(f"\n🚫 Qutato Blocked This Request")
        print(f"Reason: {trust_report.get('reason', 'Unknown safety violation')}")
        print(f"Action taken: {trust_report.get('action')}")
        return
        
    print("✅ Trust check passed! Continuing to Browser Agent...")
    
    # --- 2. Build the LLM for OpenRouter ---
    # We subclass ChatOpenAI because browser-use v0.12+ sometimes expects the '.provider' property
    from pydantic import ConfigDict
    
    class OpenRouterChat(ChatOpenAI):
        model_config = ConfigDict(extra="allow")
        
        @property
        def provider(self):
            return "openrouter"
            
        @property
        def model(self):
            return self.model_name

    llm = OpenRouterChat(
        model="openai/gpt-4o-mini", # Standard fallback for OpenRouter
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )
    
    # --- 3. Execute Browser-Use ---
    print("🌐 Launching AI Browser...")
    
    # Use the redacted instruction if PII was stripped by Qutato
    final_instruction = trust_report.get("redacted_text", prompt)
    
    agent = Agent(
        task=final_instruction,
        llm=llm
    )
    
    result = await agent.run()
    
    print("\n📦 Mission Complete")
    print("-------------------")
    print(result)


if __name__ == "__main__":
    load_dotenv()
    
    # Hardcoded key from user request, or fallback to environment variables
    api_key = os.environ.get("OPENROUTER_API_KEY", "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")
    
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = "Go to github.com and search for Qutato, then tell me what you find."
        
    asyncio.run(run_qutato_browser(task, api_key))
