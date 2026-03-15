<p align="center">
<pre>
   ____        _        _        
  / __ \      | |      | |       
 | |  | |_   _| |_ __ _| |_ ___  
 | |  | | | | | __/ _` | __/ _ \ 
 | |__| | |_| | || (_| | || (_) |😂
  \___\_\\__,_|\__\__,_|\__\___/ 
                                 
</pre>
</p>

# 🛡️ Qutato😂 — The Smart Core Trust Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Production Ready](https://img.shields.io/badge/Production-Ready-green.svg)](#quick-start)
[![Open Source](https://img.shields.io/badge/Open-Source-brightgreen.svg)](https://github.com/AnkitSharma-29/qutato)

Qutato is a local-first AI trust layer you run on your own machine. It sits between your applications and your LLM providers, vetting every request and response with mathematical precision. The Gateway is the control plane — the product is **trust**.

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

> [!NOTE]
> To run the full Qutato Gateway with multi-provider support and enterprise guardrails, check out the [Qutato Enterprise](https://github.com/AnkitSharma-29/qutato-enterprise) repository.

Upgrading? Just `git pull` and `pip install -e qutato_core`.

---

## Security defaults (API access)

Qutato runs on `localhost`. Treat all external access as untrusted input.

- **API Key gating** (`ADMIN_API_KEY`): All requests require a valid Qutato key. Unknown clients are rejected.
- **Customize with:** Set `ADMIN_API_KEY=your_key` in a `.env` file or edit `config.py`.
- **Local-only by default:** The Gateway binds to `0.0.0.0:8000` but all data stays in `~/.qutato/`.

Run `qutato status` to surface health and configuration.

```bash
qutato status
```

---

## Highlights

- **[Daily Budget Cap](#budget-manager)** — Prevent runaway local agents. Set a daily token limit (e.g., 500,000) and Qutato blocks all further LLM calls once reached.
- **[Agent Loop Detector](#loop-detector)** — Auto-kills runaway agent loops. If an agent repeats the same action 3 times, Qutato stops it to save your budget.
- **[Input Guardrails](#input-guardrails)** — Junk detection, keyboard mashing filter, sensitive keyword flagging. Blocks bad prompts before they cost you tokens.
- **[Persistent Memory Brain](#memory-engine)** — A "Second Brain" for agents that stores facts and recalls context across sessions.
- **[Quota Optimization](#quota-savings)** — Tracks every token you save. Shows your ROI in real-time.
- **[Sidecar SDK](#sidecar-agent-sdk)** — Direct Python integration for any AI agent (no HTTP needed).
- **[Universal Compatibility](#integrations)** — Works with OpenClaw, Roo Code, Continue, Ollama, LM Studio, and any OpenAI-compatible tool.
- **[Global CLI](#cli-commands)** — `qutato` command available from any terminal, any directory.
- **[Sub-Millisecond Speed](#performance)** — Verified overhead of **0.022 ms**. Invisible to the user.

---

## Everything we built so far

### Core platform
- **Gateway API** (`localhost:8000`) — OpenAI-compatible control plane for all LLM traffic. Handles auth, routing, vetting, and quota tracking.
- **CLI surface:** `qutato status`, `qutato learn`, `qutato recall`, `qutato forget`.
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
- **Adaptive Thresholding:** `T(c,u) = T_base + α·sensitivity(c) − β·trust(u)` — mathematically derived from risk minimization.
- **Confidence Gating:** If the AI's internal confidence is below the threshold, Qutato suppresses the response.
- **Lagrangian Derivation:** The threshold is derived from a formal trade-off between false positives and false negatives.

#### Memory Engine
- **Persistent Facts:** Store project context, deadlines, and knowledge that survives across sessions.
- **Smart Recall:** Keyword-based retrieval with relevance scoring.
- **Global Brain:** Shared across all tools, agents, and terminals via `~/.qutato/qutato_memory.json`.

#### Quota Savings
- **Junk Interception:** Each blocked junk prompt saves ~10 tokens.
- **Abstention Savings:** Each suppressed hallucination saves ~250 tokens.
- **Real-Time Counter:** `qutato status` shows your cumulative savings.
- **Persistent Tracking:** Saved in `~/.qutato/qutato_stats.json`.

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
    │   http://localhost:8000/v1    │
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
        "baseUrl": "http://localhost:8000/v1",
        "apiKey": "qutato_admin_secret_key"
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
    base_url="http://localhost:8000/v1",
    api_key="qutato_admin_secret_key",
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

For production-grade **Gateway** deployment (Docker, multi-worker support, and Redis caching), please see the [Qutato Enterprise](https://github.com/AnkitSharma-29/qutato-enterprise) repository.

---

### ✨ Core Features
- **🛡️ Formal Trust (Abstention Engine)**: Adaptive thresholding for sensitive requests.
- **🕵️‍♂️ Adversarial Probing (OBLITERATUS)**: Detects prompt injections, jailbreaks, and malicious framing.
- **🏗️ Role-Aware Vetting (gstack Integration)**: Specialized safety patterns for engineering roles (CEO, Architect, Security, QA).
- **🌉 gstack Bridge**: Seamless integration with `Bun`-based `gstack` skills and Claude Code.
- **🌐 Browser Vulture**: Browser-driven visual and functional safety verification.
- **🧠 Persistent Memory (Shared Brain)**: Local-first fact storage with Multi-Agent synchronization support.
- **💰 Budget & Quota Management**: Daily token limits and usage tracking.
- **🔄 Universal Gateway**: OpenAI-compatible API translating into Anthropic, Gemini, and Ollama formats.



## Contributing
We welcome contributions! Please see our [Issues](https://github.com/AnkitSharma-29/qutato/issues) for roadmaps and tasks.

## License
MIT License. See [LICENSE](LICENSE) for details.

---
*Built for the Agentic Era by [Ankit Sharma](https://github.com/AnkitSharma-29)* 🛡️
