import os
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.security import APIKeyHeader
from litellm import completion
import uvicorn
from gateway.config import settings

app = FastAPI(title=settings.APP_NAME)

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=True)

def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return api_key

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}

@app.post("/v1/chat/completions")
async def chat_completions(request: Request, api_key: str = Depends(verify_api_key)):
    try:
        data = await request.json()
        user_id = data.get("user_id", "default_user")
        
        # 1. Quota Check
        if not quota_manager.check_quota(user_id):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Quota exceeded. Please upgrade your plan."
            )
        
        # 2. Abstention Logic (Placeholder for model confidence/urgency analysis)
        # In a real scenario, we might run a fast 'prober' model here first.
        mock_confidence = 0.7  # Imagine this comes from a prober
        is_sensitive = data.get("sensitive", False)
        
        should_abstain, threshold = abstention_engine.should_abstain(
            model_confidence=mock_confidence,
            task_urgency=0.5,
            sensitivity_score=1.0 if is_sensitive else 0.0
        )
        
        if should_abstain:
            return {
                "id": "abstain-123",
                "object": "chat.completion",
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": "I must abstain from answering this. Confidence too low or sensitivity too high."
                    },
                    "finish_reason": "abstention"
                }],
                "usage": {"total_tokens": 0},
                "abstention_threshold": threshold
            }
        
        # 3. Forward to LiteLLM
        response = completion(**data)
        
        # 4. Record Usage
        total_tokens = response.get("usage", {}).get("total_tokens", 0)
        quota_manager.increment_usage(user_id, total_tokens)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
