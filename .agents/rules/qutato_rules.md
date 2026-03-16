# Qutato Turbo: Adaptive Governance

Unified rules for high-performance agentic engineering.

## Adaptive Verbosity (Tiered Thinking)
- **Default (Tier 1 - Sprint)**: 
  - Keep responses under 3 sentences.
  - No explanations for obvious code changes.
  - Skip "Sure, I can help" filler.
- **Complexity Trigger (Tier 2 - Deep Dive)**:
  - If the task involves >3 files or complex architectural changes, automatically provide "Technical Reasoning" blocks.
  - User can override with "Expand" or "Keep it short".

## Context Pruning
- Never read more than 800 lines of a file unless explicitly necessary.
- Use `grep` or `find` before `list_dir` for large repositories.
- When outputting code, only show the relevant diff or chunk unless the file is <50 lines.

## Terminal Efficiency
- Prefer `ls -R` or `fd` for discovery.
- Use single-line bash commands where possible.
- Avoid interactive prompts; use `--yes` or `-y` flags.

## Quality Standards
- No console logs in production.
- Pydantic models must have descriptions for all fields.
- Type hints are mandatory for new functions.
