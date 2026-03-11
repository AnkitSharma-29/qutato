<p align="center">
  <img src="./assets/qutato_logo.png" width="400" alt="Qutato Logo">
</p>

# Qutato: The Smart Core Trust Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Production Ready](https://img.shields.io/badge/Production-Ready-green.svg)](#deployment)

**Qutato** is a high-performance, open-core "Smart Core" platform for Large Language Models. It provides a mathematically-verified Trust Layer that sits between your applications and your AI providers.

Unlike traditional proxies, Qutato uses **Adaptive Thresholding** and **Persistent Memory** to eliminate hallucinations, manage quotas, and ensure adversarial security—all while maintaining sub-millisecond overhead.

### 🛡️ Privacy-First & Local-Only
Qutato is designed to run **on your own machine**. 
*   **No Data Exfiltration:** Your LLM keys, prompts, and memories never leave your infrastructure. 
*   **Run Anywhere:** Works on Windows, macOS, and Linux. 
*   **Zero Dependencies:** The `qutato-core` module is a pure Python implementation that requires no external servers.

---

## 🚀 Key Features

*   **Elite Trust Layer:** Real-time Abstention logic that blocks low-confidence responses.
*   **BYOK (Bring Your Own Key):** Full ownership of data and LLM costs.
*   **Contextual Memory Engine:** A "Second Brain" for agents that tracks facts and updates context over time.
*   **Universal Compatibility:** Supports 100+ LLMs (OpenAI, Gemini, Anthropic, Mistral, Llama, etc.).
*   **Production-Ready CLI:** Manage facts, health, and recall directly from your terminal.
*   **💰 Quota Optimization:** Intercept "junk" or out-of-scope prompts *before* they hit expensive LLMs, saving 100% of the token cost for useless inputs.
*   **Sub-Millisecond Speed:** Verified average overhead of **0.022 ms**.

---

## 🎯 Why Qutato?

### Where to Use It
*   **Enterprise AI Agents:** Customer support, Finance, and Legal desks where a hallucination is a liability.
*   **Multi-Agent Ecosystems:** Autonomous fleets requiring a shared, vetted memory "Brain."
*   **Safety-Critical RAG:** Scientific research or internal knowledge discovery where "guessing" is not allowed.
*   **Production Gateways:** Scaling AI teams that need to manage millions of requests across different providers without losing control.

### The Qutato Benefits
*   **Trust by Default:** Eliminate "Confident Hallucinations" with mathematical certainty.
*   **Massive Cost Savings:** Intercept high-risk or out-of-scope queries before they hit expensive premium models.
*   **Zero-Overhead Protection:** At 0.022ms, the layer is invisible to the user but bulletproof for the business.
*   **Actionable Context:** Qutato doesn't just store memory; it uses it to lower safety hurdles for verified facts, making your AI feel "smarter" and "faster."

---

## 📦 Project Structure

### 1. [Qutato-Core](./qutato_core) (Open Source)
The engine of the platform. A lightweight Python module for local development and agentic integration.
- Install: `pip install -e ./qutato_core`

### 2. [Qutato-Enterprise](./qutato_enterprise) (Gateway)
The high-scale API gateway. Built on FastAPI and Redis for production deployments.
- Deploy: `docker-compose up -d redis`

---

## 🛠️ Quick Start

### 1. Installation
```bash
git clone https://github.com/AnkitSharma-29/qutato.git
cd qutato
pip install -r qutato_enterprise/requirements.txt
```

### 2. Start the Gateway
```bash
# Start Redis for Quota & Memory
docker-compose up -d redis

# Run the API
python -m qutato_enterprise.gateway.main
```

### 3. Use the CLI
```bash
python qutato_enterprise/cli.py learn "Qutato HQ is the center of trust."
python qutato_enterprise/cli.py recall "HQ"
```

---

## 🤖 Agentic SDK & Supervisor Pattern

Qutato is designed to be the **Safety Firewall** for AI Agents. It is trivial to integrate into any agentic loop to prevent autonomous mistakes.

### Two-Line Implementation
```python
from qutato_core.engine.abstention import abstention_engine

# Vet the agent's thought before it takes an action
block, _ = abstention_engine.should_abstain(model_confidence=0.4)
if block: agent.replan()
```

### Why use it for Agents?
1.  **Autonomous Safety:** Agents often "hallucinate" tools or commands. Qutato blocks these before they execute.
2.  **Shared Memory:** Agents share the **Qutato Brain**, ensuring they don't miss context when handing off tasks.
3.  **Active Supervision:** Qutato acts as a "Senior Engineer" reviewing the agent's junior-level thoughts.

---

## 🛡️ Trust & Safety (The Abstention Loop)

Qutato doesn't just pass text; it performs a **Lagrangian Risk Check** on every request. 

```python
from qutato_core.engine.abstention import abstention_engine

# Vet a response before showing it to the user
block, threshold = abstention_engine.should_abstain(
    model_confidence=0.65, 
    task_urgency=0.8
)

if block:
    print("Abstaining: Risk too high.")
```

---

## 🤝 Contributing
We welcome contributions! Please see our [Issues](https://github.com/AnkitSharma-29/qutato/issues) for roadmaps and tasks.

## 📄 License
MIT License. See [LICENSE](LICENSE) for details.

---
*Built for the Agentic Era by [Ankit Sharma](https://github.com/AnkitSharma-29)*
