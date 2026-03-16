---
description: High-speed Qutato development workflow
---

# Qutato Fast-Track

This skill prioritizes sub-millisecond implementation cycles. Use via `/fast`.

1. **Interface First**: Define Pydantic models or abstract base classes.
2. **Minimal Logic**: Implement the first working path.
3. **Verify**: Immediately run `pytest` on the specific file.
4. **Refactor**: Only optimize after green tests.

# Qutato Verify-Only

Lightweight lint and type checking.

1. Run `mypy` or `flake8` on the target file.
2. Report errors only.
3. Do not attempt fixes unless requested.
