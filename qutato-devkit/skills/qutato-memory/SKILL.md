---
name: qutato-memory
description: Store and recall project knowledge across sessions — persistent AI memory that never forgets
---

# 🧠 Qutato Memory Brain

## Purpose
AI assistants forget everything between sessions. Memory Brain gives them long-term memory — store facts, decisions, configs, and context that persist forever.

## Use Cases
- Store project architecture decisions
- Remember database schemas and API endpoints
- Track deadlines and milestones
- Save debugging knowledge for future reference
- Share context between different AI agents

## How to Use

### Store a Fact
```bash
qutato-devkit learn "Backend uses FastAPI on port 8080"
qutato-devkit learn "Database is PostgreSQL 15 with pgvector" --tags database,config
qutato-devkit learn "Sprint deadline is April 15, 2026" --tags deadline,sprint
```

### Recall Facts
```bash
qutato-devkit recall "database"
# → Returns: "Database is PostgreSQL 15 with pgvector"

qutato-devkit recall "deadline"
# → Returns: "Sprint deadline is April 15, 2026"

qutato-devkit recall ""
# → Returns ALL stored facts
```

### Forget Facts
```bash
qutato-devkit forget abc123     # Remove specific fact by ID
qutato-devkit forget --all      # Clear all memories
```

### Via Python
```python
from qutato_devkit.trust_engine import learn, recall, forget

learn("API rate limit is 100 req/min", tags=["api", "config"])
results = recall("rate limit")
print(results["facts"])
```

### Via MCP
Use `learn_fact` and `recall_facts` tools from any MCP-compatible IDE.

## Storage
All memories are stored locally in `~/.qutato/memory.json` — portable, private, zero cloud.
