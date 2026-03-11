# Qutato: The Smart Core Trust Platform

Qutato is the definitive enterprise trust layer for Large Language Models. It provides a dual-tiered architecture for maximum flexibility and performance.

## Project Structure

### 1. [Qutato-Core](./qutato_core) (Open-Source Module)
A lightweight Python package for developers to integrate Abstention and local quota governance directly into their applications.
- **Mathematical Abstention**: Adaptive Thresholding for hallucination prevention.
- **Local Quota Control**: Budget management at the source.

### 2. [Qutato-Enterprise](./qutato_enterprise) (Hosted Gateway)
A production-grade, high-performance API gateway for large-scale deployments.
- **BYOK (Bring Your Own Key)**: Full data and cost ownership.
- **Global Governance**: Redis-backed sub-millisecond tracking across teams.
- **Elite Routing**: LiteLLM-powered failover and load balancing.

---

## Getting Started

### For Developers (Standalone Module)
```bash
pip install -e ./qutato_core
```

### For Teams (Enterprise Gateway)
```bash
cd qutato_enterprise
docker-compose up -d redis
pip install -r requirements.txt
python -m gateway.main
```

## Repository
Final platform core: `https://github.com/AnkitSharma-29/qutato.git`
