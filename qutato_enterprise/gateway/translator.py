"""
Qutato Universal Translator — Format Translation Layer

Normalizes incoming requests from any AI API format (Anthropic, Gemini, Ollama)
into the internal OpenAI-style representation, and denormalizes responses back.

All functions are pure — no side-effects, no I/O, no state.
"""

import uuid
import time
from typing import Any


# ---------------------------------------------------------------------------
# Internal representation (OpenAI-style)
# ---------------------------------------------------------------------------

def _make_internal(
    model: str,
    messages: list[dict],
    stream: bool = False,
    temperature: float | None = None,
    max_tokens: int | None = None,
    extra: dict | None = None,
) -> dict:
    """Build a canonical internal request dict."""
    req = {"model": model, "messages": messages, "stream": stream}
    if temperature is not None:
        req["temperature"] = temperature
    if max_tokens is not None:
        req["max_tokens"] = max_tokens
    if extra:
        req.update(extra)
    return req


# ===================================================================
#  NORMALIZERS  (foreign format  →  internal OpenAI-style)
# ===================================================================

def normalize_anthropic(body: dict) -> dict:
    """
    Anthropic Messages API → internal.

    Anthropic quirks handled:
      - `system` is a top-level string, not part of `messages`.
      - Each message `content` can be a string OR a list of content blocks
        like [{"type": "text", "text": "..."}].
      - Role "assistant" maps 1:1.
    """
    messages: list[dict] = []

    # System prompt is top-level in Anthropic
    system_text = body.get("system")
    if system_text:
        messages.append({"role": "system", "content": system_text})

    for msg in body.get("messages", []):
        role = msg.get("role", "user")
        content = msg.get("content", "")

        # Content can be a list of blocks or a plain string
        if isinstance(content, list):
            # Flatten text blocks; skip image blocks for now
            text_parts = [
                block.get("text", "")
                for block in content
                if isinstance(block, dict) and block.get("type") == "text"
            ]
            content = "\n".join(text_parts)

        messages.append({"role": role, "content": content})

    return _make_internal(
        model=body.get("model", ""),
        messages=messages,
        stream=body.get("stream", False),
        temperature=body.get("temperature"),
        max_tokens=body.get("max_tokens"),
    )


def normalize_gemini(body: dict) -> dict:
    """
    Google Gemini API → internal.

    Gemini quirks handled:
      - Uses `contents` (list) instead of `messages`.
      - Each content has `parts` list with `{"text": "..."}`.
      - Role "model" → "assistant".
      - System instruction may be in `systemInstruction`.
    """
    messages: list[dict] = []

    # System instruction
    sys_instr = body.get("systemInstruction")
    if sys_instr:
        if isinstance(sys_instr, dict):
            parts = sys_instr.get("parts", [])
            sys_text = " ".join(p.get("text", "") for p in parts if isinstance(p, dict))
        else:
            sys_text = str(sys_instr)
        if sys_text.strip():
            messages.append({"role": "system", "content": sys_text.strip()})

    for content in body.get("contents", []):
        role = content.get("role", "user")
        # Gemini uses "model" for assistant
        if role == "model":
            role = "assistant"

        parts = content.get("parts", [])
        text_parts = [
            p.get("text", "") for p in parts
            if isinstance(p, dict) and "text" in p
        ]
        text = "\n".join(text_parts)
        messages.append({"role": role, "content": text})

    # Gemini generation config
    gen_config = body.get("generationConfig", {})

    return _make_internal(
        model=body.get("model", ""),
        messages=messages,
        stream=body.get("stream", False),
        temperature=gen_config.get("temperature"),
        max_tokens=gen_config.get("maxOutputTokens"),
    )


def normalize_ollama_chat(body: dict) -> dict:
    """
    Ollama /api/chat → internal.

    Ollama's chat format is nearly identical to OpenAI.
    Main differences: `options` dict for temperature, etc.
    """
    messages = body.get("messages", [])
    options = body.get("options", {})

    return _make_internal(
        model=body.get("model", ""),
        messages=messages,
        stream=body.get("stream", False),
        temperature=options.get("temperature"),
        max_tokens=options.get("num_predict"),
    )


def normalize_ollama_generate(body: dict) -> dict:
    """
    Ollama /api/generate → internal.

    Converts a single prompt string into a one-message conversation.
    """
    messages = []
    system = body.get("system")
    if system:
        messages.append({"role": "system", "content": system})

    prompt = body.get("prompt", "")
    messages.append({"role": "user", "content": prompt})

    options = body.get("options", {})

    return _make_internal(
        model=body.get("model", ""),
        messages=messages,
        stream=body.get("stream", False),
        temperature=options.get("temperature"),
        max_tokens=options.get("num_predict"),
    )


# ===================================================================
#  DENORMALIZERS  (internal OpenAI response  →  foreign format)
# ===================================================================

def _get_response_text(response: dict) -> str:
    """Extract the assistant text from an OpenAI-style response."""
    choices = response.get("choices", [])
    if choices:
        return choices[0].get("message", {}).get("content", "")
    return ""


def _get_usage(response: dict) -> dict:
    """Extract usage from an OpenAI-style response."""
    return response.get("usage", {})


def denormalize_to_anthropic(response: dict) -> dict:
    """Internal OpenAI response → Anthropic Messages API response."""
    text = _get_response_text(response)
    usage = _get_usage(response)

    return {
        "id": response.get("id", f"msg_{uuid.uuid4().hex[:24]}"),
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": text}],
        "model": response.get("model", ""),
        "stop_reason": "end_turn",
        "usage": {
            "input_tokens": usage.get("prompt_tokens", 0),
            "output_tokens": usage.get("completion_tokens", 0),
        },
    }


def denormalize_to_gemini(response: dict) -> dict:
    """Internal OpenAI response → Gemini API response."""
    text = _get_response_text(response)
    usage = _get_usage(response)

    return {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": text}],
                    "role": "model",
                },
                "finishReason": "STOP",
            }
        ],
        "usageMetadata": {
            "promptTokenCount": usage.get("prompt_tokens", 0),
            "candidatesTokenCount": usage.get("completion_tokens", 0),
            "totalTokenCount": usage.get("total_tokens", 0),
        },
    }


def denormalize_to_ollama_chat(response: dict) -> dict:
    """Internal OpenAI response → Ollama /api/chat response."""
    text = _get_response_text(response)
    usage = _get_usage(response)

    return {
        "model": response.get("model", ""),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S.000000Z", time.gmtime()),
        "message": {"role": "assistant", "content": text},
        "done": True,
        "total_duration": 0,
        "eval_count": usage.get("completion_tokens", 0),
        "prompt_eval_count": usage.get("prompt_tokens", 0),
    }


def denormalize_to_ollama_generate(response: dict) -> dict:
    """Internal OpenAI response → Ollama /api/generate response."""
    text = _get_response_text(response)
    usage = _get_usage(response)

    return {
        "model": response.get("model", ""),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S.000000Z", time.gmtime()),
        "response": text,
        "done": True,
        "total_duration": 0,
        "eval_count": usage.get("completion_tokens", 0),
        "prompt_eval_count": usage.get("prompt_tokens", 0),
    }


# ===================================================================
#  AUTO-DETECTION
# ===================================================================

def detect_format(body: dict) -> str:
    """
    Detect the format of an incoming request body.

    Returns one of: "openai", "anthropic", "gemini", "ollama_chat",
                    "ollama_generate", "unknown".

    Detection heuristics (in priority order):
      1. `contents` key with list of parts  →  gemini
      2. Top-level `system` (string) + messages with content blocks  →  anthropic
      3. `prompt` key with no `messages`  →  ollama_generate
      4. `messages` key (list)  →  check for ollama vs openai
         - Ollama bodies usually have `options` or no `api_key` — but we
           default to openai since Ollama chat is OpenAI-compatible anyway.
      5. Fallback  →  unknown
    """
    # Gemini: has "contents" with parts
    if "contents" in body and isinstance(body.get("contents"), list):
        return "gemini"

    # Anthropic: has top-level "system" string, or messages with content blocks
    if isinstance(body.get("system"), str) and "messages" in body:
        return "anthropic"
    if "messages" in body and isinstance(body["messages"], list) and body["messages"]:
        first_content = body["messages"][0].get("content")
        if isinstance(first_content, list):
            # Content blocks are Anthropic-style
            if any(isinstance(b, dict) and b.get("type") == "text" for b in first_content):
                return "anthropic"

    # Ollama generate: has "prompt" but no "messages"
    if "prompt" in body and "messages" not in body:
        return "ollama_generate"

    # OpenAI / Ollama chat (functionally the same)
    if "messages" in body and isinstance(body.get("messages"), list):
        return "openai"

    return "unknown"


# ===================================================================
#  CONVENIENCE DISPATCHER
# ===================================================================

def normalize(body: dict, fmt: str | None = None) -> dict:
    """
    Normalize any supported format to internal.
    If fmt is None, auto-detect.
    """
    if fmt is None:
        fmt = detect_format(body)

    normalizers = {
        "openai": lambda b: b,  # already internal format
        "anthropic": normalize_anthropic,
        "gemini": normalize_gemini,
        "ollama_chat": normalize_ollama_chat,
        "ollama_generate": normalize_ollama_generate,
    }

    normalizer = normalizers.get(fmt)
    if normalizer is None:
        raise ValueError(f"Unknown format: {fmt}")

    return normalizer(body)


def denormalize(response: dict, fmt: str) -> dict:
    """
    Denormalize internal response to the target format.
    """
    denormalizers = {
        "openai": lambda r: r,  # already in OpenAI format
        "anthropic": denormalize_to_anthropic,
        "gemini": denormalize_to_gemini,
        "ollama_chat": denormalize_to_ollama_chat,
        "ollama_generate": denormalize_to_ollama_generate,
    }

    denormalizer = denormalizers.get(fmt)
    if denormalizer is None:
        raise ValueError(f"Unknown format: {fmt}")

    return denormalizer(response)
