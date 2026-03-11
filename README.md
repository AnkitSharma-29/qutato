# Qutato: Advanced LLM Quota & Trust Layer

Qutato is a high-performance, scalable gateway designed to intercept LLM requests to prevent hallucinations (via Abstention), protect against adversarial attacks, and optimize token quota/costs.

## Quick Start (Development)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start Redis:
   ```bash
   docker-compose up -d redis
   ```

3. Run the gateway:
   ```bash
   python -m gateway.main
   ```

## Architecture

- **Gateway**: FastAPI proxy using LiteLLM for universal provider support.
- **Engine**: Core Abstention logic and Adversarial Probing.
- **Quota Manager**: Redis-backed sub-millisecond tracking.
