# 🛡️ Qutato DevKit — The Universal AI Trust & Automation Platform

> **One install. Every AI agent. Every screen. Every API. Fully local. Fully safe.**

Qutato DevKit is the **only tool** that combines safety + budget + memory + universal compatibility in one free, local-first package.

---

## ⚡ Quick Start (30 Seconds)

```bash
pip install -e ./qutato-devkit
qutato-devkit setup
qutato-devkit status
```

That's it. Qutato is protecting your AI interactions.

---

## What It Does

| Feature | What | Why |
|---------|------|-----|
| 💰 **Budget Manager** | Daily token caps, auto-reset | Stop runaway AI costs |
| 🔒 **PII Redactor** | Masks emails, SSNs, API keys, passwords | Your secrets never reach the cloud |
| 🧠 **Memory Brain** | Persistent fact storage across sessions | AI remembers everything |
| 🔄 **Loop Detector** | Kills agents repeating the same action | Saves hundreds of tokens |
| 🛡️ **Input Guardrails** | Blocks junk prompts, keyboard mashing | No wasted tokens |
| 🤖 **Agent Router** | Routes tasks to the best automation agent | One command does everything |
| 🔌 **MCP Server** | Works with Claude, Cursor, Gemini, VS Code | Universal IDE integration |

---

## Who Uses Qutato

| Level | Who |
|-------|-----|
| 🐣 **Beginner** | Students, vibe coders, AI hobbyists |
| 🔧 **Developer** | Full-stack devs, indie hackers, startups |
| 📊 **Data Pro** | Data scientists, data engineers, ML engineers |
| 🏢 **Enterprise** | Engineers at Google, Microsoft, Meta, Amazon |

---

## CLI Commands

```bash
qutato-devkit status              # System health + budget + agents
qutato-devkit check "prompt"      # Trust-check a prompt
qutato-devkit learn "fact"        # Store in Memory Brain
qutato-devkit recall "query"      # Search memories
qutato-devkit budget              # View budget
qutato-devkit budget --set 200000 # Set daily limit
qutato-devkit redact "text"       # Strip PII
qutato-devkit route "task"        # Pick best agent for task
qutato-devkit agents              # Show available agents
qutato-devkit mcp                 # Start MCP server
qutato-devkit setup               # Auto-configure IDE
```

---

## MCP Integration (IDE/Agent)

Add to your IDE's MCP settings:

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

### MCP Tools Available
| Tool | Description |
|------|-------------|
| `trust_check` | Full safety pipeline on any prompt |
| `learn_fact` | Store knowledge persistently |
| `recall_facts` | Query stored memories |
| `check_budget` | View remaining token budget |
| `set_budget` | Set daily token limit |
| `redact_pii` | Strip sensitive data from text |
| `route_task` | Route task to best agent |
| `system_status` | Full health check |

---

## Agent Ecosystem

Qutato automatically detects and routes to installed agents:

| Agent | Type | Install |
|-------|------|---------|
| [Browser-Use](https://github.com/browser-use/browser-use) | 🌐 Web automation | `pip install browser-use` |
| [Open Interpreter](https://github.com/OpenInterpreter/open-interpreter) | 💻 Code execution | `pip install open-interpreter` |
| [PyAutoGUI](https://github.com/asweigart/pyautogui) | 🖱️ Screen control | `pip install pyautogui` |
| [CrewAI](https://github.com/crewAIInc/crewAI) | 🤝 Multi-agent | `pip install crewai` |
| [LangChain](https://github.com/langchain-ai/langchain) | 🔗 Tool framework | `pip install langchain` |

### Example: Universal Task Routing
```bash
qutato-devkit route "Search Google for car images"
# → ✅ Routing to Browser-Use

qutato-devkit route "Analyze sales.csv and create a chart"
# → ✅ Routing to Open Interpreter

qutato-devkit route "Click the submit button on screen"
# → ✅ Routing to PyAutoGUI
```

---

## Python SDK (Direct Import)

```python
from qutato_devkit.trust_engine import trust_check, learn, recall, redact_pii
from qutato_devkit.agent_router import route_task

# Trust-check before sending to LLM
result = trust_check("Process user data for john@acme.com")
if result["safe"]:
    send_to_llm(result.get("redacted_text", original_prompt))

# Persistent memory
learn("Project uses Python 3.11 with FastAPI", tags=["stack"])
facts = recall("python version")

# Route tasks
task = route_task("Download the top 5 images from Google")
print(task["message"])  # → ✅ Routing to Browser-Use
```

---

## Skills Pack

Pre-built skills for Antigravity, Claude Code, Cursor, Gemini CLI:

| Skill | Description |
|-------|-------------|
| `qutato-quickstart` | Get started in 60 seconds |
| `qutato-trust-gate` | Vet AI outputs before accepting |
| `qutato-memory` | Store/recall project knowledge |
| `qutato-budget` | Token budget enforcement |
| `qutato-pii-shield` | Auto-redact sensitive data |

---

## Why Qutato Instead of NVIDIA NeMo Guardrails?

| | Qutato | NeMo Guardrails |
|---|---|---|
| Setup | 30 seconds | 30+ minutes |
| GPU required | ❌ No | ⚠️ Best with NVIDIA |
| Budget control | ✅ Built-in | ❌ None |
| Persistent memory | ✅ Built-in | ❌ None |
| MCP compatible | ✅ Yes | ❌ No |
| Speed overhead | 0.022ms | 50-200ms |
| Cost | Free | Free (but NVIDIA ecosystem $$) |

---

## Security

- 🔒 **Local-only** — All data in `~/.qutato/`, never leaves your machine
- 🚫 **Zero telemetry** — No tracking, no analytics, no phone-home
- 🔑 **API key gating** — Gateway requires auth even on localhost
- 📖 **Open source** — Every line auditable on GitHub

---

## Configuration

Edit `~/.qutato/config.json` or use CLI commands:

```bash
qutato-devkit budget --set 500000   # Daily token limit
```

---

## License

MIT — Free for everyone, forever.

---

Built with ❤️ by [Ankit Sharma](https://github.com/AnkitSharma-29)
