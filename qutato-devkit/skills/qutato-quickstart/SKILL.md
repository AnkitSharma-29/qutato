---
name: qutato-quickstart
description: Get started with Qutato DevKit in 60 seconds — trust layer, memory, and budget for any AI agent
---

# 🛡️ Qutato Quick Start

## What is Qutato?
Qutato DevKit is a trust layer for AI agents. It saves money, protects data, and remembers everything — all running locally on your machine.

## Install (30 seconds)
```bash
pip install -e ./qutato-devkit
```

## Your First Commands

### 1. Check system status
```bash
qutato-devkit status
```

### 2. Trust-check a prompt before sending to AI
```bash
qutato-devkit check "Write a function to process user data"
```

### 3. Store a fact in Memory Brain
```bash
qutato-devkit learn "Project uses Python 3.11 with FastAPI backend"
```

### 4. Recall facts later
```bash
qutato-devkit recall "python version"
```

### 5. Set daily budget to prevent overspending
```bash
qutato-devkit budget --set 200000
```

### 6. Redact PII before sending to cloud LLMs
```bash
qutato-devkit redact "Send email to john@company.com with API key sk-abc123xyz"
```

### 7. Route a task to the best agent
```bash
qutato-devkit route "Search Google for car images"
```

## Connect to Your IDE (MCP)
```bash
qutato-devkit setup   # Auto-detects your IDE
qutato-devkit mcp     # Start MCP server
```

Then add to your IDE's MCP settings:
```json
{
  "mcpServers": {
    "qutato-devkit": {
      "command": "qutato-devkit",
      "args": ["mcp"]
    }
  }
}
```

## That's it! 🎉
Qutato is now protecting every AI interaction automatically.
