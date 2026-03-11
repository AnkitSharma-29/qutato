# Qutato-Core: The Open Trust Layer

This is the standalone, open-source core of the Qutato platform. It provides the mathematical engines for LLM Abstention and local quota governance.

## Installation

```bash
pip install -e ./qutato_core
```

## Usage

```python
from qutato_core.engine.abstention import abstention_engine

# Calculate if a model response should be trusted
should_abstain, threshold = abstention_engine.should_abstain(
    model_confidence=0.7,
    task_urgency=0.5,
    sensitivity_score=1.0
)

if should_abstain:
    print(f"Abstaining (Threshold: {threshold})")
```
