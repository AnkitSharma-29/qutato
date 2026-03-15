# Qutato x gstack Engineering Governance

This project uses Qutato Smart Core integrated with `gstack` workflow skills.

## Role-Based Vetting
When prompting the agent, you can specify your current role to enable specialized safety patterns:
- **CEO Mode**: Challenges product assumptions and prevents reckless shipping.
- **Architect Mode**: Enforces decoupling and system integrity.
- **Security Mode**: Prevents hardcoded secrets and insecure configurations.
- **QA Mode**: Ensures tests are never skipped.

## gstack Skills
The following skills are available as `gstack` slash commands:

### `/plan-review` (Architect Mode)
Vets the current design proposal for architectural soundness.
```bash
qutato gstack --role Architect --prompt "Review current design"
```

### `/security-audit` (Security Mode)
Scans for security anti-patterns.
```bash
qutato gstack --role Security --prompt "Scan for hardcoded secrets"
```

### `/qa-ship` (QA Mode)
Verifies that test coverage is maintained before shipping.
```bash
qutato gstack --role QA --prompt "Verify test coverage"
```

## Coding Standards
1. **Local-First**: No data should be transmitted to external servers without explicit user consent.
2. **Minimal Overhead**: Qutato additions must maintain < 0.1ms latency.
3. **Pydantic Everywhere**: Use Pydantic for data validation and settings.
4. **FastAPI for Gateway**: All API endpoints must be asynchronous.

---
*Built for the Agentic Era by [Ankit Sharma](https://github.com/AnkitSharma-29)* 🛡️
