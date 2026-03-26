"""
🔌 Qutato MCP Server — Expose Qutato as Universal MCP Tools

Makes Qutato's trust capabilities available to ANY MCP-compatible client:
  - Claude Code, Cursor, Gemini CLI, Antigravity, VS Code, etc.

Tools exposed:
  - trust_check: Full safety pipeline (guardrails + PII + budget + loops)
  - learn_fact: Store knowledge in persistent Memory Brain
  - recall_facts: Query stored memories
  - check_budget: View/set daily token budget
  - redact_pii: Strip sensitive data from text
  - route_task: Route a task to the best available agent
  - system_status: Full Qutato health check
"""

import json
import sys
import asyncio
from typing import Optional

# Try to import MCP SDK — graceful fallback if not installed
try:
    from mcp.server import Server
    from mcp.server.stdio import run_server
    from mcp.types import Tool, TextContent, Resource
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

from qutato_devkit.trust_engine import (
    trust_check,
    learn,
    recall,
    forget,
    redact_pii,
    get_budget_status,
    set_daily_budget,
    log_token_usage,
    log_saving,
    get_status,
    check_input_safety,
    check_loop,
)
from qutato_devkit.agent_router import (
    route_task,
    detect_available_agents,
    classify_task,
    get_ecosystem_status,
)


# ─── Tool Definitions ────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "trust_check",
        "description": (
            "Run Qutato's full trust pipeline on a prompt. "
            "Checks input safety, PII, budget, and loop detection. "
            "Returns whether the prompt is safe to send to an LLM."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The prompt to check for safety",
                }
            },
            "required": ["prompt"],
        },
    },
    {
        "name": "learn_fact",
        "description": (
            "Store a fact in Qutato's persistent Memory Brain. "
            "Facts persist across sessions and can be recalled later. "
            "Use for project context, decisions, deadlines, etc."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "fact": {
                    "type": "string",
                    "description": "The fact to remember",
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional tags for categorization (e.g., ['project', 'deadline'])",
                },
            },
            "required": ["fact"],
        },
    },
    {
        "name": "recall_facts",
        "description": (
            "Search Qutato's Memory Brain for stored facts. "
            "Returns facts matching the query. "
            "Use empty query to list all stored facts."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query to find relevant facts",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "forget_facts",
        "description": (
            "Remove facts from Memory Brain. "
            "Pass a fact_id to remove specific fact, "
            "or omit to clear all memories."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "fact_id": {
                    "type": "string",
                    "description": "ID of the fact to remove (omit to clear all)",
                }
            },
        },
    },
    {
        "name": "check_budget",
        "description": (
            "View current token budget status. "
            "Shows daily limit, tokens used, remaining, and savings."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "set_budget",
        "description": (
            "Set daily token budget limit. "
            "Qutato blocks LLM calls once the limit is reached."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "daily_tokens": {
                    "type": "integer",
                    "description": "Maximum tokens allowed per day (e.g., 500000)",
                }
            },
            "required": ["daily_tokens"],
        },
    },
    {
        "name": "redact_pii",
        "description": (
            "Scan text and replace PII with [REDACTED_TYPE] tags. "
            "Detects emails, SSNs, credit cards, API keys, passwords, "
            "phone numbers, IPs, and connection strings."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to scan for PII",
                }
            },
            "required": ["text"],
        },
    },
    {
        "name": "route_task",
        "description": (
            "Route a natural language task to the best available agent. "
            "Detects installed agents (Browser-Use, Open Interpreter, "
            "PyAutoGUI, CrewAI) and picks the most appropriate one."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Natural language description of the task",
                }
            },
            "required": ["task"],
        },
    },
    {
        "name": "system_status",
        "description": (
            "Get full Qutato system status: health, budget, "
            "memories, available agents, and feature status."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]


# ─── Tool Handler ─────────────────────────────────────────────────────────────

def handle_tool_call(tool_name: str, arguments: dict) -> str:
    """
    Handle an MCP tool call and return JSON result.

    This function works with or without the MCP SDK —
    it's the core logic shared by MCP server and CLI.
    """
    try:
        if tool_name == "trust_check":
            result = trust_check(arguments["prompt"])

        elif tool_name == "learn_fact":
            result = learn(
                arguments["fact"],
                tags=arguments.get("tags"),
            )

        elif tool_name == "recall_facts":
            result = recall(arguments.get("query", ""))

        elif tool_name == "forget_facts":
            result = forget(arguments.get("fact_id"))

        elif tool_name == "check_budget":
            result = get_budget_status()

        elif tool_name == "set_budget":
            result = set_daily_budget(arguments["daily_tokens"])

        elif tool_name == "redact_pii":
            result = redact_pii(arguments["text"])

        elif tool_name == "route_task":
            result = route_task(arguments["task"])

        elif tool_name == "system_status":
            status = get_status()
            ecosystem = get_ecosystem_status()
            result = {**status, "ecosystem": ecosystem}

        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        return json.dumps(result, indent=2, default=str)

    except Exception as e:
        return json.dumps({"error": str(e)})


# ─── MCP Server (if MCP SDK is installed) ─────────────────────────────────────

def create_mcp_server():
    """Create and configure the MCP server."""
    if not MCP_AVAILABLE:
        print("❌ MCP SDK not installed. Install with: pip install mcp")
        print("   Running in standalone mode — use CLI commands instead.")
        return None

    server = Server("qutato-devkit")

    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name=t["name"],
                description=t["description"],
                inputSchema=t["inputSchema"],
            )
            for t in TOOLS
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        result = handle_tool_call(name, arguments)
        return [TextContent(type="text", text=result)]

    return server


async def run_mcp_server():
    """Start the MCP server on stdio."""
    server = create_mcp_server()
    if server is None:
        return

    print("🛡️ Qutato MCP Server starting...", file=sys.stderr)
    print("   Tools: " + ", ".join(t["name"] for t in TOOLS), file=sys.stderr)
    print("   Ready for MCP client connections.", file=sys.stderr)

    await run_server(server)


# ─── Standalone JSON-RPC Mode (no MCP SDK needed) ─────────────────────────────

def run_standalone_server():
    """
    Simple stdin/stdout JSON-RPC server for environments
    where MCP SDK is not available.
    """
    print("🛡️ Qutato Standalone Server (JSON-RPC)", file=sys.stderr)
    print("   Send JSON requests via stdin.", file=sys.stderr)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            tool_name = request.get("tool", request.get("method", ""))
            arguments = request.get("arguments", request.get("params", {}))
            result = handle_tool_call(tool_name, arguments)
            print(result)
            sys.stdout.flush()
        except json.JSONDecodeError:
            print(json.dumps({"error": "Invalid JSON"}))
            sys.stdout.flush()


# ─── Entry Point ──────────────────────────────────────────────────────────────

def main():
    """Start the appropriate server mode."""
    if MCP_AVAILABLE:
        asyncio.run(run_mcp_server())
    else:
        run_standalone_server()


if __name__ == "__main__":
    main()
