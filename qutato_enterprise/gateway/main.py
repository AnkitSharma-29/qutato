from fastapi import FastAPI, Depends, Header, HTTPException, Request, status
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
import litellm
import uvicorn
import os
from qutato_enterprise.gateway.config import settings
from qutato_enterprise.gateway.callbacks import pre_call_abstention_callback, post_call_success_callback
from qutato_core.engine.budget import budget_manager
from qutato_core.engine.loop_detector import loop_detector
from qutato_core.engine.updater import check_for_updates
from qutato_core.version import __version__
from qutato_enterprise.gateway.translator import detect_format, normalize, denormalize

# Qutato Smart Core: The definitive Trust & Abstention platform.
# Universal Gateway — accepts OpenAI, Anthropic, Gemini, and Ollama formats.

SUPPORTED_FORMATS = {
    "openai": {
        "endpoint": "/v1/chat/completions",
        "description": "OpenAI Chat Completions API",
    },
    "anthropic": {
        "endpoint": "/anthropic/v1/messages",
        "description": "Anthropic Messages API",
    },
    "gemini": {
        "endpoint": "/gemini/v1/generateContent",
        "description": "Google Gemini GenerateContent API",
    },
    "ollama_chat": {
        "endpoint": "/api/chat",
        "description": "Ollama Chat API",
    },
    "ollama_generate": {
        "endpoint": "/api/generate",
        "description": "Ollama Generate API",
    },
}

app = FastAPI(title=settings.APP_NAME)
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=True)


def verify_qutato_key(api_key: str = Depends(api_key_header)):
    """Verifies that the user has a valid Qutato subscription/key."""
    if api_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Qutato API Key"
        )
    return api_key


# -------------------------------------------------------------------
#  Health / Discovery
# -------------------------------------------------------------------

@app.get("/")
def read_root():
    """Health check for users who open localhost:8000 in their browser."""
    return {
        "status": "online",
        "message": "🛡️ Qutato Gateway is running. Universal AI Trust Platform is active.",
        "version": __version__,
        "supported_formats": list(SUPPORTED_FORMATS.keys()),
        "docs_url": "http://localhost:8000/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}


@app.get("/v1/formats")
async def list_formats():
    """Discovery endpoint — lists all supported API formats and their endpoints."""
    return {
        "gateway": "Qutato Universal Gateway",
        "version": __version__,
        "formats": SUPPORTED_FORMATS,
    }


# -------------------------------------------------------------------
#  Shared Trust Pipeline
# -------------------------------------------------------------------

async def _process_request(
    data: dict,
    llm_api_key: str,
    source_format: str,
    request: Request,
) -> dict:
    """
    Core processing pipeline used by ALL format endpoints.

    Takes an already-normalized (OpenAI-style) request body, runs it through
    the full trust stack, calls the LLM via LiteLLM, and returns the raw
    OpenAI-style response dict.
    """
    user_id = data.get("user_id", "default_user")
    sensitive = data.get("sensitive", False)

    # --- 1. Input Guardrails ---
    messages = data.get("messages", [])
    if messages:
        last_prompt = messages[-1].get("content", "")
        from qutato_core.engine.detector import prompt_detector
        report = prompt_detector.analyze_prompt(last_prompt)

        print(f"🔍 [Qutato] [{source_format.upper()}] Vetting: '{last_prompt[:50]}...'")

        if report["is_junk"]:
            print(f"🚫 [Qutato] Blocked JUNK input. Saving quota.")
            from qutato_core.engine.quota import quota_manager
            quota_manager.log_savings(user_id, estimated_tokens=10)
            raise HTTPException(
                status_code=400,
                detail="Junk input detected. Qutato blocked this to save your quota."
            )

        # --- 2. Loop Detection ---
        if loop_detector.is_loop(last_prompt):
            print(f"🔄 [Qutato] Loop detected. Auto-killing request.")
            from qutato_core.engine.quota import quota_manager
            quota_manager.log_savings(user_id, estimated_tokens=250)
            raise HTTPException(
                status_code=429,
                detail="Agent loop detected. Qutato stopped this to save your budget."
            )

        # --- 3. Budget Check ---
        if not budget_manager.can_spend(estimated_tokens=500):
            remaining = budget_manager.get_status()['remaining_tokens']
            raise HTTPException(
                status_code=403,
                detail=f"Daily token limit reached. You only have {remaining:,} tokens left today."
            )

        # Auto-elevate sensitivity if keywords detected
        if report["is_sensitive"]:
            sensitive = True

    # --- 4. LLM Call via LiteLLM ---
    # Strip non-LiteLLM keys before forwarding
    litellm_data = {k: v for k, v in data.items() if k not in ("user_id", "sensitive", "api_key")}

    response = await litellm.acompletion(
        **litellm_data,
        api_key=llm_api_key,
        additional_args={"user_id": user_id, "sensitive": sensitive}
    )

    # --- 5. Log Actual Token Spend ---
    tokens_used = response.get("usage", {}).get("total_tokens", 500)
    budget_manager.log_spend(tokens_used)

    return response


def _extract_llm_key(request: Request, data: dict) -> str:
    """Extract the LLM API key from headers or body."""
    llm_api_key = (
        request.headers.get("X-LLM-API-KEY")
        or request.headers.get("x-api-key")         # Anthropic-style
        or request.headers.get("x-goog-api-key")    # Gemini-style
        or data.get("api_key")
    )
    if not llm_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing LLM API Key. Provide 'X-LLM-API-KEY', 'x-api-key', 'x-goog-api-key' header, or 'api_key' in body."
        )
    return llm_api_key


async def _handle_format_endpoint(
    request: Request,
    fmt: str,
) -> dict:
    """
    Shared handler for all format-specific endpoints.
    Normalizes → processes → denormalizes.
    """
    try:
        data = await request.json()
        llm_api_key = _extract_llm_key(request, data)

        # Normalize to internal (OpenAI) format
        internal_data = normalize(data, fmt=fmt)
        print(f"🌐 [Qutato] Translated {fmt.upper()} → internal format")

        # Process through trust pipeline
        response = await _process_request(internal_data, llm_api_key, fmt, request)

        # Denormalize back to caller's expected format
        output = denormalize(response, fmt=fmt)
        print(f"🌐 [Qutato] Translated response → {fmt.upper()} format")
        return output

    except HTTPException:
        raise
    except Exception as e:
        if "ABSTAIN" in str(e):
            # Build abstention in the caller's format
            abstention_response = {
                "id": "abstain-123",
                "object": "chat.completion",
                "choices": [{
                    "message": {"role": "assistant", "content": str(e)},
                    "finish_reason": "abstention"
                }],
                "usage": {"total_tokens": 0}
            }
            return denormalize(abstention_response, fmt=fmt)

        if "Quota exceeded" in str(e) or "429" in str(e):
            raise HTTPException(status_code=429, detail=str(e))

        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------------
#  Format-Specific Endpoints
# -------------------------------------------------------------------

@app.post("/v1/chat/completions")
async def chat_completions(request: Request, q_api_key: str = Depends(verify_qutato_key)):
    """
    OpenAI-compatible endpoint (original).
    Enhanced with auto-detection: if the body is Anthropic/Gemini/Ollama format
    it will be automatically translated.
    """
    try:
        data = await request.json()
        llm_api_key = _extract_llm_key(request, data)

        # Auto-detect format
        detected = detect_format(data)
        if detected != "openai":
            print(f"🌐 [Qutato] Auto-detected {detected.upper()} format on OpenAI endpoint")

        internal_data = normalize(data, fmt=detected)

        response = await _process_request(internal_data, llm_api_key, detected, request)

        # If auto-detected a non-OpenAI format, denormalize back
        if detected != "openai":
            return denormalize(response, fmt=detected)
        return response

    except HTTPException:
        raise
    except Exception as e:
        if "ABSTAIN" in str(e):
            return {
                "id": "abstain-123",
                "object": "chat.completion",
                "choices": [{
                    "message": {"role": "assistant", "content": str(e)},
                    "finish_reason": "abstention"
                }],
                "usage": {"total_tokens": 0}
            }
        if "Quota exceeded" in str(e) or "429" in str(e):
            raise HTTPException(status_code=429, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/anthropic/v1/messages")
async def anthropic_messages(request: Request, q_api_key: str = Depends(verify_qutato_key)):
    """Native Anthropic Messages API endpoint."""
    return await _handle_format_endpoint(request, fmt="anthropic")


@app.post("/gemini/v1/generateContent")
async def gemini_generate_content(request: Request, q_api_key: str = Depends(verify_qutato_key)):
    """Native Google Gemini GenerateContent endpoint."""
    return await _handle_format_endpoint(request, fmt="gemini")


@app.post("/api/chat")
async def ollama_chat(request: Request, q_api_key: str = Depends(verify_qutato_key)):
    """Native Ollama Chat endpoint."""
    return await _handle_format_endpoint(request, fmt="ollama_chat")


@app.post("/api/generate")
async def ollama_generate(request: Request, q_api_key: str = Depends(verify_qutato_key)):
    """Native Ollama Generate endpoint."""
    return await _handle_format_endpoint(request, fmt="ollama_generate")


# -------------------------------------------------------------------
#  Startup
# -------------------------------------------------------------------

if __name__ == "__main__":
    from qutato_core.engine.logo import print_logo
    print_logo()
    print(f"🚀 [Qutato] Starting Universal Gateway v{__version__}...")
    print(f"🌐 [Qutato] Supported formats: {', '.join(SUPPORTED_FORMATS.keys())}")
    # Check for updates    # Start Server
    try:
        check_for_updates() # Check for updates (non-blocking)
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        print(f"❌ Failed to start Qutato Gateway: {e}")
