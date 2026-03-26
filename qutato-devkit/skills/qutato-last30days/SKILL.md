---
description: "Safe Deep Research: Perform topic research using Qutato Trust Layer and the Last30Days Skill"
---

# 🕵️‍♂️ Safe Deep Research (Qutato + Last30Days)

The `last30days` skill is a powerful research agent that queries Reddit, X, YouTube, Hacker News, and Polymarket. Because it makes multiple API calls and reads potentially untrusted social content, you must **always** enforce Qutato's Trust Layer when using it.

## 🛡️ The Qutato Safety Protocol

Whenever the user asks you to research a topic or trend using `/last30days`, follow these steps:

### 1. Check the Budget
Before launching a deep research task, verify that there is enough token budget remaining. Research tasks can be expensive.
`qutato check_budget`

If the budget is low (< 50,000 tokens), ask the user for confirmation before proceeding.

### 2. Vet the Input
Run the user's research topic through the trust checker. This ensures no PII is accidentally sent to the public APIs that `last30days` queries.
`qutato check "your topic here"`

- If `safe` is false due to PII, modify the search query to use the `redacted_text`.
- If blocked by guardrails, politely decline the research task.

### 3. Execute the Research
Run the `last30days` skill on the verified (and potentially redacted) topic.
`/last30days [verified_topic]`

### 4. Vet the Output (Optional but Recommended)
Social media content can contain toxic material or unexpected PII. When `last30days` returns its synthesized briefing, you can optionally run it through `qutato redact` before presenting the final summary to the user.

## Example Workflow

**User:** "Research the latest drama about CEO John Smith (john@example.com) from the last 30 days."

**You (The Agent):**
1. `qutato check_budget` -> (Budget OK)
2. `qutato check "latest drama about CEO John Smith (john@example.com)"` -> Returns `redacted_text`: "latest drama about CEO John Smith ([REDACTED_EMAIL])"
3. Run `/last30days latest drama about CEO John Smith` (omitting the PII naturally based on the trust check).
4. Summarize the findings for the user safely!
