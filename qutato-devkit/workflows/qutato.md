---
description: Run Qutato trust checks, memory, and budget from your development workflow
---

# /qutato Workflow

Use these commands to integrate Qutato into your development workflow.

## Commands

### /qutato:setup
Initialize Qutato for the current project.

1. Run `qutato-devkit setup` to auto-detect IDE and configure
2. Verify with `qutato-devkit status`

### /qutato:check
Trust-gate the current AI output before accepting it.

1. Run `qutato-devkit check "paste the AI output here"`
2. If blocked, request a new response from the AI
3. If PII detected, use the redacted version instead

### /qutato:remember
Store important project context in Memory Brain.

1. Run `qutato-devkit learn "fact to remember" --tags project,context`
2. Verify with `qutato-devkit recall "search query"`

### /qutato:budget
Set and monitor token budget for the session.

1. Run `qutato-devkit budget` to check current status
2. Run `qutato-devkit budget --set 200000` to set daily limit
3. Monitor with `qutato-devkit status`

### /qutato:route
Route a task to the best available automation agent.

1. Run `qutato-devkit route "describe your task in natural language"`
2. Follow the recommended agent instructions
3. Install missing agents if needed

### /qutato:agents
Check which automation agents are available.

// turbo
1. Run `qutato-devkit agents`

### /qutato:mcp
Start the MCP server for IDE integration.

1. Run `qutato-devkit mcp`
2. Configure your IDE's MCP settings to connect
