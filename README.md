# Qutato: The Smart Core Trust Platform

Qutato is a high-performance, standalone "Smart Core" for LLM infrastructure. It acts as the definitive trust layer, providing mathematical Abstention (anti-hallucination) and Quota governance while abstracting away underlying model providers.

## Key Features

- **Mathematical Abstention**: Forces LLMs to stay within their knowledge boundaries.
- **BYOK (Bring Your Own Key)**: Users provide their own LLM keys; Qutato provides the intelligence.
- **Quota Governance**: Redis-backed sub-millisecond tracking to prevent budget waste.
- **Universal Interface**: A single, clean API for all AI operations.

- **Gateway**: FastAPI proxy using LiteLLM for universal provider support.
- **Engine**: Core Abstention logic and Adversarial Probing.
- **Quota Manager**: Redis-backed sub-millisecond tracking.
