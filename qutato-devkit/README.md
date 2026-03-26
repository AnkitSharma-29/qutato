# 🛡️ Qutato DevKit: The Universal AI Trust & Automation Platform

> **"One Command. Every Agent. Total Trust."**

Qutato DevKit is the ultimate local-first infrastructure for AI agents. It provides an enterprise-grade safety layer (PII redaction, budget control, loop detection) and persistent memory that integrates seamlessly with your existing automation tools.

Whether you're using **Browser-Use**, **Open Interpreter**, **Agent-Browser**, or **PyAutoGUI**, Qutato sits in the middle to ensure every action is safe, private, and cost-effective.

---

## ✨ Core Features

### 1. 🛡️ Trust Engine
The brain of Qutato safety. It intercepts every prompt and response to enforce:
- **PII Redaction:** Automatically detects and masks Emails, SSNs, Credit Cards, API Keys, and Phone Numbers locally.
- **Budget Manager:** Set daily token caps to prevent runaway automation costs.
- **Loop Detector:** Stops agents from getting stuck in infinite "Try Again" cycles.
- **Input Guardrails:** Blocks keyboard mashing and nonsensical junk inputs.

### 2. 🧠 Memory Brain
A persistent local knowledge store. Qutato remembers project context, user preferences, and past facts so your agents can "recall" them in future sessions without re-learning.

### 3. 🤖 Universal Agent Router
Automatically detects installed agents on your system and routes tasks to the best tool:
- Browsing tasks → `Browser-Use` or `Agent-Browser`
- Coding/System tasks → `Open Interpreter`
- GUI automation → `PyAutoGUI`

### 4. 🔌 Protocol Support (MCP)
Qutato is a first-class **Model Context Protocol (MCP)** server. Connect it to Cursor, Claude Code, Antigravity, or any MCP-compatible IDE to give your AI agent superpowers.

---

## 🚀 Quick Start

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/AnkitSharma-29/qutato.git
cd qutato/qutato-devkit

# Install as editable package
pip install -e .
```

### 2. Setup
Run the auto-configurator to detect your environment:
```bash
qutato-devkit setup
```

### 3. Use the CLI
```bash
# Check if a prompt is safe
qutato-devkit check "Email my boss at boss@company.com"

# Learn a fact
qutato-devkit learn "This project uses Python 3.12"

# View status
qutato-devkit status
```

---

## 🧩 Integrated Skills
The DevKit comes with modular **Skills** that teach any AI agent how to use Qutato:
- `qutato-quickstart`: 60-second onboarding.
- `qutato-trust-gate`: Instructions for vetting outputs.
- `qutato-pii-shield`: Rules for automatic data privacy.
- `qutato-last30days`: Safe integration for deep market research.
- `qutato-agent-browser`: Secure terminal-based browsing.

---

## 📁 Project Structure
- `qutato_devkit/`: The core Python source code.
- `skills/`: Markdown-based playbooks for AI agents.
- `configs/`: Pre-configured settings for MCP, CodeRabbit, and more.
- `workflows/`: GSD-compatible automation workflows.

---

## 🔒 Privacy First
All Qutato data is stored locally in `~/.qutato/`. **Zero telemetry. Zero clouds. Total control.**

---

Built with ❤️ for the future of Agentic Coding.
