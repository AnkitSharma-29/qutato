from fastapi import FastAPI, Depends, Header, HTTPException, Request, status
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import litellm
import uvicorn
import os
import logging
import datetime
import json
import uuid
from qutato_enterprise.gateway.config import settings
from qutato_enterprise.gateway.callbacks import pre_call_abstention_callback, post_call_success_callback
from qutato_core.engine.budget import budget_manager
from qutato_core.engine.loop_detector import loop_detector
from qutato_core.engine.updater import check_for_updates
from qutato_core.version import __version__
from qutato_enterprise.gateway.translator import detect_format, normalize, denormalize
from typing import Union, Any, Dict
from collections import deque
import time

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

# --- 1. CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In strict production, replace with your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. Rate Limiting Middleware ---
class RateLimiter:
    """Simple in-memory sliding window rate limiter."""
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.counts: Dict[str, deque] = {} # user_id -> deque of timestamps

    def is_allowed(self, user_id: str) -> bool:
        now = time.time()
        if user_id not in self.counts:
            self.counts[user_id] = deque()
        
        # Prune old timestamps
        history = self.counts[user_id]
        while history and history[0] < now - self.window_seconds:
            history.popleft()
        
        if len(history) < self.max_requests:
            history.append(now)
            return True
        return False

rate_limiter = RateLimiter(max_requests=settings.DEBUG and 1000 or 100) # Increased limit for local dev

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Skip rate limiting for health checks and status
    if request.url.path in ["/", "/v1/status", "/v1/formats"]:
        return await call_next(request)

    user_id = request.headers.get("user_id", "default")
    if not rate_limiter.is_allowed(user_id):
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Qutato Rate Limiter active to protect local compute."}
        )
    return await call_next(request)

# --- 3. Persistent Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("qutato")

def audit_log(user_id: str, action: str, detail: str = ""):
    """Records an entry in the persistent qutato.log audit trail."""
    timestamp = datetime.datetime.now().isoformat()
    log_msg = f"user={user_id} action={action} {detail}"
    logger.info(log_msg)


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


@app.get("/v1/status")
async def get_status(q_api_key: str = Depends(verify_qutato_key)):
    """Exposes the full Qutato status (budget, savings, facts) for external monitoring."""
    from qutato_core.engine.memory import memory_engine
    from qutato_core.engine.quota import quota_manager
    from qutato_core.engine.budget import budget_manager
    from qutato_core.engine.loop_detector import loop_detector
    
    try:
        saved_calls, saved_tokens = quota_manager.get_total_savings()
        budget = budget_manager.get_status()
        loops = loop_detector.get_stats()
        
        return {
            "status": "active",
            "version": __version__,
            "memory": {
                "health": "Optimized",
                "known_facts": len(memory_engine.memories),
            },
            "savings": {
                "total_calls": saved_calls,
                "total_tokens": saved_tokens
            },
            "budget": budget,
            "loops": loops
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal Trust Layer Error: {str(e)}"}
        )


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
) -> Union[dict, StreamingResponse]:
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

        # --- 1.2 Adversarial Probing ---
        from qutato_core.engine.adversarial_prober import adversarial_prober
        adv_report = adversarial_prober.probe(last_prompt)
        if adv_report["is_adversarial"]:
            print(f"🛑 [Qutato] [{source_format.upper()}] Blocked ADVERSARIAL: {adv_report['matched_patterns']}")
            from qutato_core.engine.quota import quota_manager
            quota_manager.log_savings(user_id, estimated_tokens=100)
            raise HTTPException(
                status_code=403,
                detail=f"Security Alert: Adversarial pattern detected ({adv_report['matched_patterns'][0]}). Access denied."
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
    is_streaming = litellm_data.get("stream", False)

    if is_streaming:
        return await _handle_streaming_response(litellm_data, llm_api_key, user_id, sensitive, fmt=source_format)

    response = await litellm.acompletion(
        **litellm_data,
        api_key=llm_api_key,
        extra_headers={"user_id": user_id, "sensitive": str(sensitive)}
    )

    # --- 5. Log Actual Token Spend (Non-streaming) ---
    tokens_used = response.get("usage", {}).get("total_tokens", 500)
    budget_manager.log_spend(tokens_used)
    audit_log(user_id, "completion", f"tokens={tokens_used} model={data.get('model')}")

    return response

async def _handle_streaming_response(litellm_data: dict, llm_api_key: str, user_id: str, sensitive: bool, fmt: str) -> StreamingResponse:
    """Handles streaming responses from LiteLLM and bridges them to FastAPI."""
    from qutato_enterprise.gateway.translator import denormalize_chunk
    
    async def stream_generator():
        try:
            response = await litellm.acompletion(
                **litellm_data,
                api_key=llm_api_key,
                stream=True,
                extra_headers={"user_id": user_id, "sensitive": str(sensitive)}
            )
            
            # LiteLLM returns an async generator for stream=True
            async for chunk in response:
                # Denormalize each chunk to the target format if needed
                if hasattr(chunk, "dict"):
                    chunk_dict = chunk.dict()
                    translated_chunk = denormalize_chunk(chunk_dict, fmt=fmt)
                    yield f"data: {json.dumps(translated_chunk)}\n\n"
            
            yield "data: [DONE]\n\n"
            audit_log(user_id, "stream_completion", f"model={litellm_data.get('model')} format={fmt}")
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(stream_generator(), media_type="text/event-stream")


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
) -> Union[dict, StreamingResponse]:
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

        # If it's a streaming response, return it directly
        if isinstance(response, StreamingResponse):
            return response

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

        # If streaming, return directly
        if isinstance(response, StreamingResponse):
            return response

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
