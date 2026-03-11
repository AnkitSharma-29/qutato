from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.security import APIKeyHeader
import litellm
import uvicorn
from qutato_enterprise.gateway.config import settings
from qutato_enterprise.gateway.callbacks import pre_call_abstention_callback, post_call_success_callback
from qutato_core.engine.budget import budget_manager
from qutato_core.engine.loop_detector import loop_detector
from qutato_core.engine.updater import print_update_notification
from qutato_core.version import __version__

# Qutato Smart Core: The definitive Trust & Abstention platform.
# This engine hides provider complexity and ensures mathematical safety.

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

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}

@app.post("/v1/chat/completions")
async def chat_completions(request: Request, q_api_key: str = Depends(verify_qutato_key)):
    try:
        data = await request.json()
        
        # 1. Extract LLM API Key from headers or body
        # Preference: Header 'X-LLM-API-KEY' or 'Authorization'
        llm_api_key = request.headers.get("X-LLM-API-KEY") or data.get("api_key")
        
        if not llm_api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing LLM API Key. Please provide 'X-LLM-API-KEY' header or 'api_key' in body."
            )
        
        # 2. Prepare request for LiteLLM
        user_id = data.get("user_id", "default_user")
        sensitive = data.get("sensitive", False)
        
        # 3. Prompt Vetting (Input Guardrails)
        messages = data.get("messages", [])
        if messages:
            last_prompt = messages[-1].get("content", "")
            from qutato_core.engine.detector import prompt_detector
            report = prompt_detector.analyze_prompt(last_prompt)
            
            print(f"🔍 [Qutato] Vetting Input: '{last_prompt[:50]}...'")
            
            if report["is_junk"]:
                print(f"🚫 [Qutato] Blocked JUNK input. Saving quota.")
                from qutato_core.engine.quota import quota_manager
                quota_manager.log_savings(user_id, estimated_tokens=10) # Log junk interception
                raise HTTPException(
                    status_code=400, 
                    detail="Junk input detected. Qutato blocked this to save your quota."
                )
            
            # 4. Loop Detection
            if loop_detector.is_loop(last_prompt):
                print(f"🔄 [Qutato] Loop detected. Auto-killing request.")
                from qutato_core.engine.quota import quota_manager
                quota_manager.log_savings(user_id, estimated_tokens=250)
                raise HTTPException(
                    status_code=429,
                    detail="Agent loop detected. Qutato stopped this to save your budget."
                )

            # 5. Budget Check
            model = data.get("model", "default")
            if not budget_manager.can_spend(model, estimated_tokens=500):
                raise HTTPException(
                    status_code=403,
                    detail=f"Daily budget limit reached. Spent: {budget_manager.get_status()['spent_today']}"
                )

            # Auto-elevate sensitivity if keywords detected
            if report["is_sensitive"]:
                sensitive = True

        # liteLLM acompletion call
        response = await litellm.acompletion(
            **data,
            api_key=llm_api_key,
            additional_args={"user_id": user_id, "sensitive": sensitive}
        )
        
        # 6. Log Actual Spend if successful
        tokens_used = response.get("usage", {}).get("total_tokens", 500)
        budget_manager.log_spend(model, tokens_used)
        
        return response
    except HTTPException as e:
        # Re-raise HTTPExceptions (like our 400 Junk blocks) so they return correctly
        raise e
    except Exception as e:
        # Check if the error was a triggered Abstention
        if "ABSTAIN" in str(e):
            return {
                "id": "abstain-123",
                "object": "chat.completion",
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": str(e)
                    },
                    "finish_reason": "abstention"
                }],
                "usage": {"total_tokens": 0}
            }
        
        # Handle Rate Limit / Quota Exceeded from callbacks
        if "Quota exceeded" in str(e) or "429" in str(e):
            raise HTTPException(status_code=429, detail=str(e))
            
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    from qutato_core.engine.logo import print_logo
    print_logo()
    print(f"🚀 [Qutato] Starting Gateway v{__version__}...")
    # Check for updates on startup (non-blocking)
    print_update_notification()
    uvicorn.run(app, host="0.0.0.0", port=8000)
