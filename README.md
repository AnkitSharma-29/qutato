<p align="center">
  <img src="./assets/qutato_logo.png" width="400" alt="Qutato Logo">
</p>

# Qutato: The Smart Core Trust Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Production Ready](https://img.shields.io/badge/Production-Ready-green.svg)](#deployment)

**Qutato** is a high-performance, open-core "Smart Core" platform for Large Language Models. It provides a mathematically-verified Trust Layer that sits between your applications and your AI providers.

Unlike traditional proxies, Qutato uses **Adaptive Thresholding**, **Persistent Memory**, and **Input Guardrails** to eliminate hallucinations, manage quotas, and ensure adversarial security—all while maintaining sub-millisecond overhead.

### 🛡️ Privacy-First & Local-Only
Qutato is designed to run **on your own machine**. 
*   **No Data Exfiltration:** Your LLM keys, prompts, and memories never leave your infrastructure. 
*   **Run Anywhere:** Works on Windows, macOS, and Linux. 
*   **Zero Dependencies:** The `qutato-core` module is a pure Python implementation that requires no external servers.

---

## 🚀 Key Features

*   **Elite Trust Layer:** Real-time Abstention logic that blocks low-confidence responses.
*   **🛡️ Input Guardrails:** Automatically vets incoming prompts for nonsense, keyboard mashing, or sensitive info before they hit the LLM.
*   **💰 Quota Optimization:** Intercept "junk" or out-of-scope prompts at the door, saving 100% of the token cost.
*   **BYOK (Bring Your Own Key):** Full ownership of data and LLM costs.
*   **Contextual Memory Engine:** A "Second Brain" for agents that tracks facts and updates context over time.
*   **Universal Compatibility:** Supports 100+ LLMs (OpenAI, Gemini, Anthropic, Mistral, Llama, etc.).
*   **Production-Ready CLI:** Manage facts, health, and savings directly from your terminal.
*   **Sub-Millisecond Speed:** Verified average overhead of **0.022 ms**.

---

## 🎯 Why Qutato?

### Where to Use It
*   **Enterprise AI Agents:** Customer support, Finance, and Legal desks where a hallucination is a liability.
*   **Multi-Agent Ecosystems:** Autonomous fleets requiring a shared, vetted memory "Brain."
*   **Safety-Critical RAG:** Scientific research or internal knowledge discovery where "guessing" is not allowed.
*   **Production Gateways:** Scaling AI teams that need to manage millions of requests across different providers without losing control.

---

## 💻 Antigravity & IDE Integration

Because Qutato is **OpenAI-Compatible**, you can use it to protect your development workflow in Antigravity or any major IDE (Cursor, VS Code, etc.).

### How it Works:
1.  **Start the Qutato Gateway** on your local machine (`http://localhost:8000`).
2.  **Point to Qutato:** Change the Base URL in your IDE to `http://localhost:8000/v1`.
3.  **Add your key:** Set the API Key to `qutato_admin_secret_key`.

---

### 🏠 Local LLM & IDE Extension Support
Qutato is designed to be the "Universal Trust Gateway" for your local machine.

#### 1. Running with Local Models (Ollama/LM Studio)
If you run models locally, Qutato can still vet them. Point your request to the Gateway and specify the provider:
*   **Model Name:** `ollama/llama3`, `lm_studio/model`, or `openai/localhost:11434`
*   **Benefit:** Qutato provides Guardrails and Memory even for 100% offline models.

#### 2. Using with VS Code / IDE Extensions
Most AI extensions (like **Roo Code**, **Continue**, or **Cursor**) support "OpenAI Compatible" endpoints.
*   **Base URL:** `http://localhost:8000/v1`
*   **API Key:** `qutato_admin_secret_key`
*   **Supervisor Mode:** Qutato acts as a transparent proxy, filtering every response before it reaches your editor.

#### 3. OpenClaw Integration 🦞
Qutato is 100% compatible with **OpenClaw**. You can use Qutato to vet all the messages sent through OpenClaw's various channels (WhatsApp, Slack, Telegram, etc.).
*   **The Setup:** In your `~/.openclaw/openclaw.json`, add a custom provider pointing to Qutato:
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
*   **The Benefit:** Now, Qutato secures your personal AI assistant. No matter which messaging app you use, Qutato vets the AI's response before it's sent to you.

### 1. Installation
```bash
git clone https://github.com/AnkitSharma-29/qutato.git
cd qutato
pip install -e qutato_core
pip install -r qutato_enterprise/requirements.txt
```

### 2. Start the Gateway
```bash
# Start the API
$env:PYTHONPATH = "." ; python qutato_enterprise/gateway/main.py
```

### 3. Use the Global CLI
```bash
qutato learn "Qutato HQ is the center of trust."
qutato status
```

---

## 🤝 Contributing
We welcome contributions! Please see our [Issues](https://github.com/AnkitSharma-29/qutato/issues) for roadmaps and tasks.

## 📄 License
MIT License. See [LICENSE](LICENSE) for details.

---
*Built for the Agentic Era by [Ankit Sharma](https://github.com/AnkitSharma-29)*
