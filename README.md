<p align="center">
  <img src="./assets/qutato_logo.png" width="400" alt="Qutato Logo">
</p>

# Qutato: The Smart Core Trust Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Production Ready](https://img.shields.io/badge/Production-Ready-green.svg)](#deployment)

**Qutato** is a high-performance, open-core "Smart Core" platform for Large Language Models. It provides a mathematically-verified Trust Layer that sits between your applications and your AI providers.

Unlike traditional proxies, Qutato uses **Adaptive Thresholding** and **Persistent Memory** to eliminate hallucinations, manage quotas, and ensure adversarial security—all while maintaining sub-millisecond overhead.

---

## 🚀 Key Features

*   **Elite Trust Layer:** Real-time Abstention logic that blocks low-confidence responses.
*   **BYOK (Bring Your Own Key):** Full ownership of data and LLM costs.
*   **Contextual Memory Engine:** A "Second Brain" for agents that tracks facts and updates context over time.
*   **Universal Compatibility:** Supports 100+ LLMs (OpenAI, Gemini, Anthropic, Mistral, Llama, etc.).
*   **Production-Ready CLI:** Manage facts, health, and recall directly from your terminal.
*   **Sub-Millisecond Speed:** Verified average overhead of **0.022 ms**.

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
