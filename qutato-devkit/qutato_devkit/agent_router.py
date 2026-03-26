"""
🤖 Qutato Agent Router — Route Tasks to the Best Available Agent

Detects which automation agents are installed and routes
natural language tasks to the most appropriate one.

Supported agents:
  - Browser-Use (web automation)
  - Open Interpreter (code execution)
  - PyAutoGUI (screen control)
  - CrewAI (multi-agent orchestration)
"""

import importlib
import shutil
from typing import Optional


# ─── Agent Detection ──────────────────────────────────────────────────────────

def _check_module(module_name: str) -> bool:
    """Check if a Python module is installed."""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False


def _check_command(cmd: str) -> bool:
    """Check if a CLI command is available."""
    return shutil.which(cmd) is not None


def detect_available_agents() -> dict:
    """
    Detect which automation agents are installed on the system.

    Returns dict of agent_name → availability info.
    """
    agents = {
        "browser_use": {
            "name": "Browser-Use",
            "type": "browser",
            "installed": _check_module("browser_use"),
            "description": "AI-controlled Chrome browser for web tasks",
            "install": "pip install browser-use",
            "github": "https://github.com/browser-use/browser-use",
            "use_cases": [
                "Web search", "Form filling", "Web scraping",
                "Screenshot capture", "Download files"
            ],
        },
        "open_interpreter": {
            "name": "Open Interpreter",
            "type": "desktop",
            "installed": _check_module("interpreter"),
            "description": "Run Python/Shell/JS code via natural language",
            "install": "pip install open-interpreter",
            "github": "https://github.com/OpenInterpreter/open-interpreter",
            "use_cases": [
                "File management", "Data analysis", "Code execution",
                "System tasks", "Document creation"
            ],
        },
        "pyautogui": {
            "name": "PyAutoGUI",
            "type": "screen",
            "installed": _check_module("pyautogui"),
            "description": "Mouse and keyboard control on any screen",
            "install": "pip install pyautogui",
            "github": "https://github.com/asweigart/pyautogui",
            "use_cases": [
                "Click automation", "Keyboard input", "Screenshot",
                "GUI testing", "Desktop app control"
            ],
        },
        "crewai": {
            "name": "CrewAI",
            "type": "multi_agent",
            "installed": _check_module("crewai"),
            "description": "Orchestrate teams of AI agents",
            "install": "pip install crewai",
            "github": "https://github.com/crewAIInc/crewAI",
            "use_cases": [
                "Research tasks", "Content creation",
                "Multi-step workflows", "Data processing"
            ],
        },
        "langchain": {
            "name": "LangChain",
            "type": "framework",
            "installed": _check_module("langchain"),
            "description": "Build LLM-powered apps with 600+ tools",
            "install": "pip install langchain",
            "github": "https://github.com/langchain-ai/langchain",
            "use_cases": [
                "API integration", "Document QA",
                "Database queries", "Tool chaining"
            ],
        },
    }

    return agents


# ─── Task Classification ─────────────────────────────────────────────────────

TASK_KEYWORDS = {
    "browser": [
        "search", "google", "browse", "website", "web", "url", "click",
        "download", "scrape", "navigate", "open page", "fill form",
        "login", "signup", "buy", "shop", "image search", "youtube",
    ],
    "desktop": [
        "file", "folder", "create", "delete", "move", "copy", "rename",
        "python", "script", "code", "run", "execute", "install", "pip",
        "data", "csv", "excel", "analyze", "plot", "chart", "database",
        "sql", "convert", "pdf", "document", "terminal", "command",
    ],
    "screen": [
        "click", "mouse", "keyboard", "type", "screenshot", "screen",
        "gui", "button", "drag", "drop", "window", "app", "desktop app",
    ],
    "multi_agent": [
        "research and", "find and then", "multiple steps", "workflow",
        "analyze and create", "team", "crew", "agents working together",
    ],
}

AGENT_TYPE_MAP = {
    "browser": "browser_use",
    "desktop": "open_interpreter",
    "screen": "pyautogui",
    "multi_agent": "crewai",
}


def classify_task(task: str) -> dict:
    """
    Classify a natural language task and recommend the best agent.

    Returns:
        dict with 'recommended_agent', 'confidence', 'all_scores'
    """
    task_lower = task.lower()
    scores = {}

    for task_type, keywords in TASK_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in task_lower)
        scores[task_type] = score

    if not any(scores.values()):
        return {
            "recommended_agent": "open_interpreter",
            "agent_type": "desktop",
            "confidence": 0.3,
            "reason": "Default fallback — Open Interpreter handles general tasks",
            "all_scores": scores,
        }

    best_type = max(scores, key=scores.get)
    best_score = scores[best_type]
    total = sum(scores.values()) or 1
    confidence = round(best_score / total, 2)

    agent_key = AGENT_TYPE_MAP[best_type]

    return {
        "recommended_agent": agent_key,
        "agent_type": best_type,
        "confidence": confidence,
        "reason": f"Task matches '{best_type}' patterns (score: {best_score})",
        "all_scores": scores,
    }


def route_task(task: str) -> dict:
    """
    Full task routing: classify → check agent availability → recommend.

    Returns routing decision with install instructions if agent missing.
    """
    classification = classify_task(task)
    agents = detect_available_agents()

    recommended = classification["recommended_agent"]
    agent_info = agents.get(recommended, {})

    if agent_info.get("installed"):
        return {
            "status": "ready",
            "task": task,
            "agent": agent_info["name"],
            "agent_key": recommended,
            "type": classification["agent_type"],
            "confidence": classification["confidence"],
            "message": f"✅ Routing to {agent_info['name']}",
        }
    else:
        # Find fallback
        fallback = None
        for key, info in agents.items():
            if info["installed"]:
                fallback = key
                break

        result = {
            "status": "agent_not_installed",
            "task": task,
            "recommended_agent": agent_info.get("name", recommended),
            "install_command": agent_info.get("install", ""),
            "github": agent_info.get("github", ""),
            "confidence": classification["confidence"],
        }

        if fallback:
            fb_info = agents[fallback]
            result["fallback"] = fb_info["name"]
            result["fallback_key"] = fallback
            result["message"] = (
                f"⚠️ {agent_info.get('name', recommended)} not installed. "
                f"Falling back to {fb_info['name']}."
            )
        else:
            result["message"] = (
                f"❌ No automation agents installed. "
                f"Install one: {agent_info.get('install', '')}"
            )

        return result


def get_ecosystem_status() -> dict:
    """Get a full overview of the Qutato agent ecosystem."""
    agents = detect_available_agents()
    installed = [k for k, v in agents.items() if v["installed"]]
    not_installed = [k for k, v in agents.items() if not v["installed"]]

    return {
        "total_agents": len(agents),
        "installed": len(installed),
        "installed_agents": [agents[k]["name"] for k in installed],
        "not_installed": [
            {"name": agents[k]["name"], "install": agents[k]["install"]}
            for k in not_installed
        ],
        "agents": agents,
    }
