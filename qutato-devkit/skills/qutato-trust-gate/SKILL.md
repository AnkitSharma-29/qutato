---
name: qutato-trust-gate
description: Vet any AI output before accepting it — safety checks, confidence gating, and hallucination prevention
---

# 🛡️ Qutato Trust Gate

## Purpose
Before accepting ANY AI-generated output (code, text, analysis), run it through Qutato's trust pipeline to catch:
- Junk/gibberish responses
- Low-confidence hallucinations
- Repeated loop patterns
- PII leakage
- Budget overruns

## When to Use
- Before deploying AI-generated code
- Before accepting AI data analysis results
- Before sharing AI-generated content externally
- When an AI agent seems stuck or giving wrong answers

## How to Use

### Via CLI
```bash
qutato-devkit check "AI-generated response to verify"
```

### Via Python (Sidecar SDK)
```python
from qutato_devkit.trust_engine import trust_check

result = trust_check("AI response to verify")
if result["safe"]:
    print("✅ Response is trustworthy")
    # Use the response
else:
    print(f"🚫 Blocked: {result['reason']}")
    # Request a better response
```

### Via MCP (from any IDE)
Call the `trust_check` tool with the prompt/response to verify.

## What Gets Checked
1. **Input Guardrails** — Blocks junk, keyboard mashing, empty prompts
2. **PII Scanner** — Detects and redacts emails, SSNs, API keys, passwords
3. **Budget Gate** — Blocks if daily token budget is exceeded
4. **Loop Detector** — Kills agents repeating the same action 3+ times
5. **Abstention Engine** — Suppresses low-confidence responses
