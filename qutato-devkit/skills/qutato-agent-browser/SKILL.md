---
description: "Safe Browser Automation: Use Vercel's agent-browser CLI securely through Qutato"
---

# 🌐 Safe Browser Automation (Qutato + Agent-Browser)

[agent-browser](https://github.com/vercel-labs/agent-browser) is a headless AI browser automation CLI by Vercel. It allows you to navigate pages, click elements, and fill forms directly from the terminal. 

Because web browsing can expose the user's machine to unintended actions or send private data to external sites, you must **always** enforce Qutato's Trust Layer before interacting with `agent-browser`.

## 🛡️ The Qutato Safety Protocol

When using `agent-browser`, always follow this strict loop:

### 1. Vet the Data Before Filling Forms
If the user asks you to fill out a website form, **always** run the data through the Qutato Trust Engine first.
`qutato check "Fill the email field with john@private.com"`

If the engine flags PII, you must STOP and ask the user: "Qutato blocked this because it contains an email address. Do you want me to proceed with the redacted version, or cancel?"

### 2. Monitor Loop Traps
Web scraping and browsing agents easily get stuck in infinite loops (e.g., clicking the same "Next" button on a broken pagination).
Before executing the same exact command (`agent-browser click @e3`) multiple times, run it through `qutato check` to trigger the **Loop Detector**. If Qutato says `loop_detected: true`, you MUST stop and rethink your strategy.

### 3. The Execution Chain
Only after verifying safety should you execute the `agent-browser` commands.

```bash
# 1. Open your target
agent-browser open https://example.com

# 2. Get the snapshot to find refs (@e1, @e2)
agent-browser snapshot -i

# ... (Identify the ref you want to interact with) ...

# 3. Vet your intended action
qutato check "I am going to click on @e1 and fill @e2 with password123"

# 4. If safe, execute the action
agent-browser click @e1
# OR
agent-browser fill @e2 "password123"
```

By injecting Qutato between yourself and `agent-browser`, you guarantee the user's privacy and prevent runaway automation costs!
