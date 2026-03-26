"""
⚡ Qutato DevKit CLI — Command-line interface for Qutato

Commands:
  qutato-devkit status    — Show system health, budget, and memory stats
  qutato-devkit setup     — Auto-detect IDE and configure Qutato
  qutato-devkit mcp       — Start the MCP server
  qutato-devkit check     — Trust-check a prompt
  qutato-devkit learn     — Store a fact in Memory Brain
  qutato-devkit recall    — Search Memory Brain
  qutato-devkit forget    — Clear memories
  qutato-devkit budget    — View/set token budget
  qutato-devkit redact    — Redact PII from text
  qutato-devkit route     — Route a task to the best agent
  qutato-devkit agents    — Show available automation agents
"""

import json
import sys
import os
from pathlib import Path

try:
    import click
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from qutato_devkit.trust_engine import (
    trust_check,
    learn,
    recall,
    forget,
    redact_pii,
    get_budget_status,
    set_daily_budget,
    get_status,
)
from qutato_devkit.agent_router import (
    route_task,
    detect_available_agents,
    get_ecosystem_status,
)

if RICH_AVAILABLE:
    console = Console()


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _print_json(data: dict):
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=2, default=str))


def _print_rich_status(status: dict):
    """Print status using rich panels."""
    if not RICH_AVAILABLE:
        _print_json(status)
        return

    # Header
    console.print(Panel(
        "[bold green]🛡️ Qutato DevKit[/bold green] — "
        f"v{status.get('version', '1.0.0')} — "
        f"[bold]{status.get('status', 'unknown').upper()}[/bold]",
        box=box.DOUBLE,
    ))

    # Budget Table
    budget = status.get("budget", {})
    budget_table = Table(title="💰 Budget", box=box.ROUNDED)
    budget_table.add_column("Metric", style="cyan")
    budget_table.add_column("Value", style="green")
    budget_table.add_row("Daily Limit", f"{budget.get('daily_limit', 0):,} tokens")
    budget_table.add_row("Used Today", f"{budget.get('used_today', 0):,} tokens")
    budget_table.add_row("Remaining", f"{budget.get('remaining', 0):,} tokens")
    budget_table.add_row(
        "Usage",
        f"{budget.get('percentage_used', 0)}%"
    )
    budget_table.add_row(
        "Total Saved",
        f"[bold green]{budget.get('total_saved', 0):,} tokens[/bold green]"
    )
    console.print(budget_table)

    # Memory
    console.print(f"\n🧠 Memory Brain: [bold]{status.get('memories', 0)}[/bold] facts stored")
    console.print(f"📁 Storage: [dim]{status.get('storage', '~/.qutato')}[/dim]")

    # Features
    features = status.get("features", {})
    feature_list = "  ".join(
        f"[green]✅ {k.replace('_', ' ').title()}[/green]"
        if v else f"[red]❌ {k.replace('_', ' ').title()}[/red]"
        for k, v in features.items()
    )
    console.print(f"\n⚙️  Features: {feature_list}")


def _print_rich_agents(ecosystem: dict):
    """Print agents using rich table."""
    if not RICH_AVAILABLE:
        _print_json(ecosystem)
        return

    table = Table(title="🤖 Agent Ecosystem", box=box.ROUNDED)
    table.add_column("Agent", style="cyan bold")
    table.add_column("Type", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Install", style="dim")

    agents = ecosystem.get("agents", {})
    for key, info in agents.items():
        status = "[green]✅ Installed[/green]" if info["installed"] else "[red]❌ Missing[/red]"
        table.add_row(
            info["name"],
            info["type"],
            status,
            info["install"] if not info["installed"] else "—",
        )

    console.print(table)
    console.print(
        f"\n📊 {ecosystem.get('installed', 0)}/{ecosystem.get('total_agents', 0)} "
        f"agents installed"
    )


# ─── CLI Commands ─────────────────────────────────────────────────────────────

if RICH_AVAILABLE:

    @click.group()
    @click.version_option(version="1.0.0", prog_name="qutato-devkit")
    def main():
        """🛡️ Qutato DevKit — The Universal AI Trust & Automation Platform"""
        pass

    @main.command()
    def status():
        """Show system health, budget, memory stats, and agent ecosystem."""
        st = get_status()
        _print_rich_status(st)
        console.print()
        eco = get_ecosystem_status()
        _print_rich_agents(eco)

    @main.command()
    @click.argument("prompt")
    def check(prompt):
        """Trust-check a prompt before sending to an LLM."""
        result = trust_check(prompt)
        if result["safe"]:
            if result.get("action") == "redacted":
                console.print(Panel(
                    f"[yellow]⚠️ PII Detected & Redacted[/yellow]\n\n"
                    f"Original: {prompt}\n"
                    f"Cleaned: {result.get('redacted_text', prompt)}",
                    title="Trust Check",
                    box=box.ROUNDED,
                ))
            else:
                console.print(Panel(
                    f"[green]✅ SAFE[/green] — {result.get('reason', 'OK')}",
                    title="Trust Check",
                    box=box.ROUNDED,
                ))
        else:
            console.print(Panel(
                f"[red]🚫 BLOCKED[/red] — {result.get('reason', 'Unsafe')}\n"
                f"Action: {result.get('action', 'blocked')}\n"
                f"Tokens saved: {result.get('tokens_saved', 0)}",
                title="Trust Check",
                box=box.ROUNDED,
            ))

    @main.command(name="learn")
    @click.argument("fact")
    @click.option("--tags", "-t", multiple=True, help="Tags for categorization")
    def learn_cmd(fact, tags):
        """Store a fact in Memory Brain."""
        result = learn(fact, tags=list(tags) if tags else None)
        if result.get("stored"):
            console.print(f"[green]✅ Learned:[/green] {fact}")
            console.print(f"   ID: {result['id']} | Total: {result['total_memories']} memories")
        else:
            console.print(f"[yellow]⚠️ {result.get('reason', 'Already exists')}[/yellow]")

    @main.command(name="recall")
    @click.argument("query", default="")
    def recall_cmd(query):
        """Search Memory Brain for facts."""
        result = recall(query)
        facts = result.get("facts", [])
        if not facts:
            console.print("[yellow]No matching facts found.[/yellow]")
            return

        table = Table(title=f"🧠 Memory Results ({result['count']} found)", box=box.ROUNDED)
        table.add_column("ID", style="dim")
        table.add_column("Fact", style="cyan")
        table.add_column("Tags", style="magenta")
        table.add_column("Created", style="dim")

        for f in facts:
            table.add_row(
                f.get("id", ""),
                f.get("fact", ""),
                ", ".join(f.get("tags", [])),
                f.get("created", "")[:10],
            )
        console.print(table)

    @main.command(name="forget")
    @click.argument("fact_id", required=False)
    @click.option("--all", "clear_all", is_flag=True, help="Clear all memories")
    def forget_cmd(fact_id, clear_all):
        """Remove facts from Memory Brain."""
        if clear_all:
            result = forget(None)
        elif fact_id:
            result = forget(fact_id)
        else:
            console.print("[yellow]Specify a fact ID or use --all to clear everything.[/yellow]")
            return
        console.print(f"[green]{json.dumps(result)}[/green]")

    @main.command()
    @click.option("--set", "set_tokens", type=int, help="Set daily token limit")
    def budget(set_tokens):
        """View or set daily token budget."""
        if set_tokens:
            result = set_daily_budget(set_tokens)
            console.print(f"[green]✅ Budget set to {set_tokens:,} tokens/day[/green]")
        else:
            result = get_budget_status()
            budget_table = Table(title="💰 Budget Status", box=box.ROUNDED)
            budget_table.add_column("Metric", style="cyan")
            budget_table.add_column("Value", style="green")
            budget_table.add_row("Daily Limit", f"{result['daily_limit']:,}")
            budget_table.add_row("Used Today", f"{result['used_today']:,}")
            budget_table.add_row("Remaining", f"{result['remaining']:,}")
            budget_table.add_row("Total Saved", f"{result.get('total_saved', 0):,}")
            console.print(budget_table)

    @main.command()
    @click.argument("text")
    def redact(text):
        """Redact PII from text."""
        result = redact_pii(text)
        if result["safe"]:
            console.print(f"[green]✅ No PII found[/green] — text is clean.")
        else:
            console.print(Panel(
                f"[yellow]⚠️ PII Found ({result['count']} items)[/yellow]\n\n"
                f"[dim]Original:[/dim] {text}\n"
                f"[dim]Redacted:[/dim] {result['redacted_text']}",
                title="PII Redaction",
                box=box.ROUNDED,
            ))

    @main.command()
    @click.argument("task")
    def route(task):
        """Route a task to the best available agent."""
        result = route_task(task)
        status_color = "green" if result["status"] == "ready" else "yellow"
        console.print(Panel(
            f"[{status_color}]{result.get('message', '')}[/{status_color}]\n\n"
            f"Task: {result.get('task', '')}\n"
            f"Confidence: {result.get('confidence', 0):.0%}",
            title="🤖 Task Router",
            box=box.ROUNDED,
        ))

    @main.command()
    def agents():
        """Show available automation agents."""
        eco = get_ecosystem_status()
        _print_rich_agents(eco)

    @main.command()
    def mcp():
        """Start the MCP server for IDE/agent integration."""
        from qutato_devkit.mcp_server import main as mcp_main
        mcp_main()

    @main.command()
    def setup():
        """Auto-detect IDE and configure Qutato integration."""
        console.print(Panel(
            "[bold green]🛡️ Qutato DevKit Setup[/bold green]",
            box=box.DOUBLE,
        ))

        # 1. Create ~/.qutato directory
        from qutato_devkit.trust_engine import _ensure_dirs, QUTATO_DIR
        _ensure_dirs()
        console.print(f"[green]✅ Storage:[/green] {QUTATO_DIR}")

        # 2. Detect IDE
        ide_detected = []
        if Path.home().joinpath(".vscode").exists():
            ide_detected.append("VS Code")
        if Path.home().joinpath(".cursor").exists():
            ide_detected.append("Cursor")
        if Path.home().joinpath(".gemini").exists():
            ide_detected.append("Antigravity")

        if ide_detected:
            console.print(f"[green]✅ IDEs found:[/green] {', '.join(ide_detected)}")
        else:
            console.print("[yellow]⚠️ No known IDE detected — using standalone mode[/yellow]")

        # 3. Generate MCP config
        mcp_config = {
            "mcpServers": {
                "qutato-devkit": {
                    "command": "qutato-devkit",
                    "args": ["mcp"],
                    "env": {},
                }
            }
        }
        config_path = QUTATO_DIR / "mcp-settings.json"
        config_path.write_text(json.dumps(mcp_config, indent=2))
        console.print(f"[green]✅ MCP config:[/green] {config_path}")

        # 4. Check agent ecosystem
        eco = get_ecosystem_status()
        console.print(f"[green]✅ Agents:[/green] {eco['installed']}/{eco['total_agents']} installed")

        # 5. Summary
        console.print()
        console.print(Panel(
            "[bold]Setup complete! Next steps:[/bold]\n\n"
            "1. [cyan]qutato-devkit status[/cyan] — Check everything works\n"
            "2. [cyan]qutato-devkit check \"your prompt\"[/cyan] — Test trust checking\n"
            "3. [cyan]qutato-devkit learn \"important fact\"[/cyan] — Store knowledge\n"
            "4. [cyan]qutato-devkit mcp[/cyan] — Start MCP server for IDE\n"
            "\nConnect MCP to your IDE:\n"
            f"  Config file: [dim]{config_path}[/dim]\n"
            "  Copy the config to your IDE's MCP settings.",
            title="🚀 Ready!",
            box=box.ROUNDED,
        ))

else:
    # Fallback CLI without Rich/Click
    def main():
        """Simple CLI fallback without rich/click."""
        args = sys.argv[1:]
        if not args:
            print("🛡️ Qutato DevKit CLI")
            print("  Commands: status, check, learn, recall, budget, redact, route, agents, mcp, setup")
            print("  Install rich & click for best experience: pip install rich click")
            return

        cmd = args[0]
        if cmd == "status":
            _print_json(get_status())
        elif cmd == "check" and len(args) > 1:
            _print_json(trust_check(args[1]))
        elif cmd == "learn" and len(args) > 1:
            _print_json(learn(args[1]))
        elif cmd == "recall":
            _print_json(recall(args[1] if len(args) > 1 else ""))
        elif cmd == "budget":
            _print_json(get_budget_status())
        elif cmd == "redact" and len(args) > 1:
            _print_json(redact_pii(args[1]))
        elif cmd == "route" and len(args) > 1:
            _print_json(route_task(args[1]))
        elif cmd == "agents":
            _print_json(get_ecosystem_status())
        elif cmd == "mcp":
            from qutato_devkit.mcp_server import main as mcp_main
            mcp_main()
        else:
            print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
