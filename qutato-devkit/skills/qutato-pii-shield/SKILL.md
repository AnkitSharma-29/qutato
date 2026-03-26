---
name: qutato-pii-shield
description: Automatically detect and redact sensitive data before it reaches cloud LLMs — emails, SSNs, API keys, passwords
---

# 🔒 Qutato PII Shield

## Purpose
Every prompt you send to a cloud LLM can accidentally contain sensitive data. PII Shield scans and redacts it locally BEFORE it reaches OpenAI, Gemini, or any other provider.

## What It Detects
| PII Type | Example | Redacted As |
|----------|---------|-------------|
| Email | john@company.com | [REDACTED_EMAIL] |
| SSN | 123-45-6789 | [REDACTED_SSN] |
| Credit Card | 4111-1111-1111-1111 | [REDACTED_CREDIT_CARD] |
| API Key | sk-abc123... | [REDACTED_API_KEY] |
| AWS Key | AKIAIOSFODNN7EXAMPLE | [REDACTED_AWS_KEY] |
| Phone | +1-555-123-4567 | [REDACTED_PHONE] |
| IP Address | 192.168.1.100 | [REDACTED_IP_ADDRESS] |
| Password | password=MySecret123 | [REDACTED_PASSWORD] |
| DB Connection | mongodb://user:pass@host | [REDACTED_CONNECTION_STRING] |

## How to Use

### CLI
```bash
qutato-devkit redact "Contact john@company.com, SSN 123-45-6789"
# → Contact [REDACTED_EMAIL], SSN [REDACTED_SSN]
```

### Python
```python
from qutato_devkit.trust_engine import redact_pii

result = redact_pii("API key is sk-abc123456789012345678901")
print(result["redacted_text"])
# → API key is [REDACTED_API_KEY]
```

### Automatic (Trust Check)
PII redaction happens automatically during `trust_check` — no extra steps needed.

## Who Needs This
- **Data Scientists** — Prevent dataset PII from reaching cloud LLMs
- **Data Engineers** — Keep connection strings out of AI prompts
- **Developers** — Stop API keys from leaking through AI assistants
- **Anyone in regulated industries** — Healthcare, fintech, government
