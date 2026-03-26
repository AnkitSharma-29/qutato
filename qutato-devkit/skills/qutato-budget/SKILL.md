---
name: qutato-budget
description: Set daily token budgets and prevent runaway AI costs — the seatbelt for AI spending
---

# 💰 Qutato Budget Manager

## Purpose
AI agents can burn thousands of tokens in minutes. Budget Manager caps daily spend, kills runaway loops, and tracks every token saved.

## How to Use

### Set Daily Budget
```bash
qutato-devkit budget --set 200000    # 200K tokens/day
qutato-devkit budget --set 500000    # 500K tokens/day (default)
qutato-devkit budget --set 50000     # 50K tokens/day (tight budget)
```

### Check Budget Status
```bash
qutato-devkit budget
# Shows: daily limit, used today, remaining, total saved
```

### Via Python
```python
from qutato_devkit.trust_engine import get_budget_status, set_daily_budget

set_daily_budget(200_000)
status = get_budget_status()
print(f"Remaining: {status['remaining']:,} tokens")
```

### Via MCP
Use `check_budget` and `set_budget` tools.

## How It Saves Money
1. **Daily Cap** — Blocks all LLM calls once limit is reached
2. **Junk Blocker** — Each blocked junk prompt saves ~10 tokens
3. **Loop Killer** — Each killed loop saves ~250+ tokens
4. **Auto-Reset** — Budget resets at midnight automatically

## Recommended Budgets
| Use Case | Budget |
|----------|--------|
| Learning/Student | 50,000 tokens/day |
| Solo developer | 200,000 tokens/day |
| Team project | 500,000 tokens/day |
| Heavy automation | 1,000,000 tokens/day |
