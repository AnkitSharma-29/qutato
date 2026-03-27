<p align="center">
<pre>
   ____        _        _        
  / __ \      | |      | |       
 | |  | |_   _| |_ __ _| |_ ___  
 | |  | | | | | __/ _` | __/ _ \ 
 | |__| | |_| | || (_| | || (_) |
  \___\_\\__,_|\__\__,_|\__\___/ 
                                 
</pre>
</p>

# 🛡️ Qutato — The Smart Core Trust Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Active Development](https://img.shields.io/badge/Status-Active%20Development-blue.svg)](#quick-start)
[![Open Source](https://img.shields.io/badge/Open-Source-brightgreen.svg)](https://github.com/AnkitSharma-29/qutato)

Qutato is a local-first AI trust layer. It sits between your applications and your LLM providers, vetting every request and response with mathematical precision. The Gateway is the control plane — the product is **trust**.

If you want an AI safety layer that is fast, private, and always-on, this is it.

[GitHub](https://github.com/AnkitSharma-29/qutato) · [SaaS Strategy](./docs/saas_strategy.md) · [Issues](https://github.com/AnkitSharma-29/qutato/issues)

Preferred setup: install via `pip` and run the gateway. Works on **Windows**, **macOS**, and **Linux**.

```bash
pip install -e qutato_core
```

---

## Models (selection + auth)

- **100+ LLM providers** supported via [LiteLLM](https://github.com/BerriAI/litellm): OpenAI, Gemini, Anthropic, Mistral, Llama, Cohere, and more.
- **BYOK (Bring Your Own Key):** Your API keys stay on your machine. Qutato never stores or transmits them.
- **Model failover:** If one provider fails, Qutato can route to a fallback automatically.

---

## Install (recommended)

Runtime: Python ≥ 3.9.

```bash
git clone https://github.com/AnkitSharma-29/qutato.git
cd qutato
pip install -e qutato_core
```

## Quick start (TL;DR)

```bash
# Use the global CLI from anywhere
qutato status
qutato learn "The project deadline is next Friday."
qutato recall "deadline"
```



---

- **Secure by default:** Treat all external access as untrusted input.
- **Local-only by default:** All data stays in `~/.qutato/` — portable, global, and private.

Run `qutato status` to surface health and configuration.

```bash
qutato status
```

---

## Highlights

- **[Daily Budget Cap](#budget-manager)** — Prevent runaway local agents. Set a daily token limit (e.g., 500,000) and Qutato blocks all further LLM calls once reached.
- **[Agent Loop Detector](#loop-detector)** — Auto-kills runaway agent loops. If an agent repeats the same action 3 times, Qutato stops it to save your budget.
- **[Universal Agent Router](#agent-router)** — Detects and routes tasks to the best automation agent (Browser-Use, Open Interpreter, PyAutoGUI, etc.).
- **[Input Guardrails](#input-guardrails)** — Junk detection, keyboard mashing filter, sensitive keyword flagging. Blocks bad prompts before they cost you tokens.
- **[Persistent Memory Brain](#memory-engine)** — A "Second Brain" for agents that stores facts and recalls context across sessions.
- **[MCP Server Support](#mcp)** — Connect Qutato directly to Cursor, Claude Code, or Antigravity via the Model Context Protocol.
- **[Universal Compatibility](#integrations)** — Works with OpenClaw, Roo Code, Continue, Ollama, LM Studio, and any OpenAI-compatible tool.
- **[Qutato Turbo](#qutato-turbo)** — Sub-millisecond adaptive optimization. Includes Concise Mode and Context Pruning to save up to 40% on token costs.
- **[Global CLI](#cli-commands)** — `qutato` and `qutato-devkit` commands available from any terminal.

---

## 🛠️ Qutato DevKit: The Automation Platform

The **Qutato DevKit** is a unified toolkit for building and running autonomous AI agents safely. It bridges the gap between raw LLM power and real-world execution.

| Component | Purpose |
|:---|:---|
| **MCP Server** | Exposes 9 trust tools (learn, recall, redact, check) to any IDE. |
| **Agent Router** | Intelligent task dispatching to system-level automation agents. |
| **Skills Pack** | Modular "Playbooks" that teach your AI how to use Qutato securely. |
| **Browser Script** | Pre-configured `browser-use` execution with built-in trust checks. |

---

## Everything we built so far

### Core platform
- **Gateway API** — Control plane for all LLM traffic. Handles routing, vetting, and quota tracking.
- **DevKit CLI** — Setup agents, manage MCP, and verify system-wide safety.
- **CLI surface:** `qutato status`, `qutato learn`, `qutato recall`, `qutato forget`, `qutato-devkit setup`.
- **Persistent storage:** All data lives in `~/.qutato/` — portable, global, and private.

### Trust + safety

#### Budget Manager (Solo Builder's Shield) 💰
- **Daily Cap:** Set a maximum number of tokens your agents are allowed to use each day.
- **Volume Tracking:** Focuses on raw token volume and request counts, perfect for local models (Ollama).
- **Auto-Reset:** Resets at midnight local time automatically.
- **CLI Commands:** `qutato budget --set-tokens 500000`, `qutato budget --reset`.

### Loop Detector 🔄
- **Auto-Kill:** Detects when an agent is repeating the same prompt/logic in a loop.
- **Pattern Matching:** Uses Jaccard similarity to catch subtle variations of the same loop.
- **Cost Protection:** Each killed loop saves hundreds of tokens and prevents runaway bills.

### Input Guardrails
- **Junk Detection:** Blocks keyboard mashing (`asdfghjkl`), repeated characters, and nonsensical prompts.
- **Sensitive Keyword Flagging:** Detects passwords, secret keys, and private data in prompts.
- **Short Prompt Filter:** Prevents wasteful single-character or empty requests.

#### Abstention Engine
- **Adaptive Thresholding:** mathematically derived from risk minimization.
- **Confidence Gating:** If the AI's internal confidence is below the threshold, Qutato suppresses the response.
- **Lagrangian Derivation:** The threshold is derived from a formal trade-off between false positives and false negatives.

#### PII Redactor (Privacy Shield) 🔒
- **Automatic Masking**: Detects and masks Emails, SSNs, Credit Cards, and API Keys *locally* before they reach the LLM provider.
- **Privacy vs. Execution Pattern**: The LLM (Mastermind) sees redacted data, but your local Python code (Executor) uses the real data from a secure vault to fulfill tasks (e.g., Amazon purchases).
- **Transactional Bypass**: Use `--bypass-pii` (CLI) or `bypass_pii_redaction=True` (SDK) for intentional data sharing.

#### Quota Savings
- **Junk Interception:** Each blocked junk prompt saves ~10 tokens.
- **Abstention Savings:** Each suppressed hallucination saves ~250 tokens.
- **Real-Time Counter:** `qutato status` shows your cumulative savings.
- **Persistent Tracking:** Saved in `~/.qutato/qutato_stats.json`.

### Plug-and-Play Architecture (Zero Config)
- **Out-of-the-box**: Qutato works immediately without any special configuration. It defaults to a high-performance **Basic Abstention Engine** that uses reliable adaptive thresholding.
- **Advanced Extensions**: Power users and researchers can plug in their own custom engines by setting the `QUTATO_ABSTENTION_PLUGIN` environment variable. (e.g., `rescue_plugin.py` for recovery tasks).
- **Skill Ecosystem**: Includes ready-to-use skills like `qutato-antigravity-monitor` for automatic server recovery.
- **Community Safe**: No proprietary code or secret logic is required for the platform to provide full value.

### Sidecar (Agent SDK)
- **Direct Python API** — No HTTP gateway needed. Agents import `qutato` and call it directly.
- **Functions:** `qutato.is_safe()`, `qutato.learn()`, `qutato.recall()`, `qutato.log_saving()`, `qutato.status()`.
- **Use case:** Any Python-based agent (Antigravity, AutoGPT, LangChain, CrewAI) can use Qutato as its trust layer.

```python
from qutato_core.sidecar import qutato

if qutato.is_safe(user_prompt):
    response = call_llm(user_prompt)
else:
    print("Blocked by Qutato")
```

### Automation & Browser Agents 🌐
Qutato provides native integration wrappers for the industry's best automation tools:
- **[Browser-Use](https://github.com/browser-use/browser-use)**: AI-driven Chrome automation with Qutato safety checks.
- **[Agent-Browser](https://github.com/vercel-labs/agent-browser)**: Vercel's CLI browser automation, forced through the trust gate.
- **[Last30Days](https://github.com/mvanhorn/last30days-skill)**: Safe multi-platform research (Reddit, X, YouTube) with budget and PII shielding.
- **[Open Interpreter](https://github.com/OpenInterpreter/open-interpreter)**: Secure terminal and system task execution.

### CLI commands

| Command | Description |
|:---|:---|
| `qutato status` | Health check, known facts, quota savings |
| `qutato learn "fact"` | Store a new fact in the memory brain |
| `qutato recall "query"` | Search for facts by keyword |
| `qutato forget` | Clear the memory brain |

---

## How it works (short)

```
Your App / IDE Extension / AI Agent / OpenClaw / CLI
                    │
                    ▼
    ┌───────────────────────────────┐
    │       Qutato Gateway          │
    │      (control plane)          │
    │                               │
    │  ┌─────────┐ ┌────────────┐  │
    │  │ Input    │ │ Abstention │  │
    │  │ Guards   │ │ Engine     │  │
    │  └─────────┘ └────────────┘  │
    │  ┌─────────┐ ┌────────────┐  │
    │  │ Memory   │ │ Quota      │  │
    │  │ Brain    │ │ Tracker    │  │
    │  └─────────┘ └────────────┘  │
    └──────────────┬────────────────┘
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
    OpenAI     Gemini     Ollama
    (Cloud)    (Cloud)    (Local)
```

---

## Integrations

### IDE Extensions (VS Code, Cursor, Roo Code, Continue)
Most AI extensions support "OpenAI Compatible" endpoints.
- **Base URL:** `http://localhost:8000/v1`
- **API Key:** `qutato_admin_secret_key`
- **Result:** Every AI response is vetted before it reaches your editor.

### OpenClaw 🦞
Qutato is fully compatible with OpenClaw. Add Qutato as a custom provider in `~/.openclaw/openclaw.json`:

```json
{
  "models": {
    "providers": {
      "qutato": {
        "baseUrl": "http://127.0.0.1:8000/v1",
        "apiKey": "your_qutato_key"
      }
    }
  }
}
```

### Local Models (Ollama / LM Studio)
Point your request to the Gateway and specify the provider:
- **Model Name:** `ollama/llama3`, `lm_studio/model`, or `openai/localhost:11434`
- **Benefit:** Qutato provides Guardrails and Memory even for 100% offline models.

### CrewAI (Multi-Agent Framework)
Qutato is the ultimate Trust Layer for multi-agent systems like [CrewAI](https://github.com/crewAIInc/crewAI). You can route an entire crew of autonomous agents through Qutato by setting the LLM `base_url`:

```python
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

# Point your CrewAI agents to the Qutato Gateway
qutato_llm = ChatOpenAI(
    base_url="http://127.0.0.1:8000/v1",
    api_key="your_qutato_key",
    model="gpt-4o"
)

researcher = Agent(
    role="Researcher",
    goal="Find facts",
    backstory="You are an AI researcher.",
    llm=qutato_llm
)
```

### Antigravity Agent
Use the Sidecar SDK for direct Python integration:

```python
from qutato_core.sidecar import qutato

qutato.is_safe("user prompt")    # Vet input
qutato.learn("important fact")   # Store in brain
qutato.recall("topic")           # Recall facts
qutato.log_saving(250)           # Log token saving
```

Or use the workflow: type `/qutato` in your Antigravity chat.

---

## Performance

Verified via high-intensity stress test (100 iterations):

| Metric | Result |
|:---|:---|
| **Average Latency** | **0.0222 ms** |
| **P95 Latency** | **0.0167 ms** |
| **Safety Effectiveness** | **84%** (Abstained on risky queries) |
| **Throughput** | **Thousands of ops/sec** on standard hardware |

Qutato adds less than **0.1 ms** of overhead. It is effectively invisible.

---

## Configuration

Qutato Core settings can be found in `qutato_core/config.py` or managed via the CLI.

| Key | Default | Description |
|:---|:---|:---|
| `DEFAULT_THRESHOLD` | `0.85` | Abstention sensitivity |
| `DEBUG` | `true` | Verbose logging |

---

## Security model (important)

Qutato is designed for **local-first, privacy-first** operation.

- **No Data Exfiltration:** Your LLM keys, prompts, and memories never leave your machine.
- **No Telemetry:** Zero analytics, zero tracking, zero phone-home.
- **Local Storage Only:** All data persists in `~/.qutato/` on your filesystem.
- **API Key Gating:** Even on localhost, the Gateway requires authentication to prevent unauthorized access from other apps on your network.
- **Open Source Audit:** Every line of code is visible and verifiable on GitHub.

---

## From source (development)

```bash
git clone https://github.com/AnkitSharma-29/qutato.git
cd qutato
pip install -e qutato_core

# Run tests
pytest
```

---

### Deployment & Production

The Qutato Smart Core is designed to be embedded in your own applications using the [Sidecar SDK](#sidecar-agent-sdk).

---

### ✨ Core Features
- **⚡ Qutato Turbo**: Adaptive brevity and context pruning for high-speed local development.
- **🛡️ Formal Trust (Abstention Engine)**: Adaptive thresholding for sensitive requests.
- **🕵️‍♂️ Adversarial Probing (OBLITERATUS)**: Detects prompt injections, jailbreaks, and malicious framing.
- **🏗️ Role-Aware Vetting (gstack Integration)**: Pro-level safety patterns for Architect, Security, and QA roles.
- **🧠 Persistent Memory (Shared Brain)**: Local-first fact storage with Multi-Agent synchronization support.
- **💰 Budget & Quota Management**: Daily token limits and usage tracking.
- **🔄 Universal Gateway**: OpenAI-compatible API translating into Anthropic, Gemini, and Ollama formats.



## Contributing
We welcome contributions! Please see our [Issues](https://github.com/AnkitSharma-29/qutato/issues) for roadmaps and tasks.

## License
MIT License. See [LICENSE](LICENSE) for details.

---
*Built for the Agentic Era by [Ankit Sharma](https://github.com/AnkitSharma-29)* 🛡️
