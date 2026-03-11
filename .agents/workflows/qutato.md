---
description: Use Qutato Smart Core for memory, vetting, and quota tracking
---

# Qutato Integration Workflow

Qutato is your local AI Trust Layer. Use these commands to leverage its Memory Brain and Guardrails directly from the Antigravity Agent.

## 1. Check Qutato Health & Savings
// turbo
```bash
qutato status
```
This shows your current memory health, known facts, and total quota saved.

## 2. Teach Qutato a New Fact
When you encounter important project context, deadlines, or facts, store them:
```bash
qutato learn "The deployment deadline is March 15th"
```

## 3. Recall Facts from the Brain
Before making assumptions, check if Qutato already knows:
// turbo
```bash
qutato recall "deadline"
```

## 4. Vet a Suspicious Input
If you receive a user prompt that looks like junk or nonsense, send it through the Qutato Gateway for vetting:
```powershell
$body = @{ model="gpt-4o"; messages=@(@{role="user"; content="THE_SUSPICIOUS_INPUT_HERE"}); user_id="antigravity_agent" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/v1/chat/completions" -Headers @{"X-API-KEY"="qutato_admin_secret_key"; "X-LLM-API-KEY"="mock-key"} -Body $body -ContentType "application/json" -ErrorAction SilentlyContinue
```

## 5. Log a Quota Saving Manually
If the agent decides to skip an unnecessary LLM call (e.g., answering from cache or memory), log the saving:
// turbo
```bash
python -c "from qutato_core.engine.quota import quota_manager; quota_manager.log_savings('antigravity_agent', 250); print('Logged 250 token saving')"
```
