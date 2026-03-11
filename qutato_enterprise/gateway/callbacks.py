import litellm
from qutato_core.engine.abstention import abstention_engine
from qutato_core.engine.quota import quota_manager
from fastapi import HTTPException

def pre_call_abstention_callback(kwargs):
    """
    Abstention Check Callback
    Runs before the request is sent to the LLM.
    """
    data = kwargs.get("additional_args", {})
    user_id = data.get("user_id", "default_user")
    
    # 1. Quota Check
    if not quota_manager.check_quota(user_id):
        raise HTTPException(status_code=429, detail="Quota exceeded")

    # 2. Abstention Logic
    mock_confidence = 0.7 
    is_sensitive = data.get("sensitive", False)
    
    should_abstain, threshold = abstention_engine.should_abstain(
        model_confidence=mock_confidence,
        task_urgency=0.5,
        sensitivity_score=1.0 if is_sensitive else 0.0
    )
    
    if should_abstain:
        # Log the quota saved by not sending this to the LLM
        print(f"🛑 [Qutato] Confidence below threshold ({mock_confidence:.2f} < {threshold:.2f}). ABSTAINING (Saving Quota).")
        quota_manager.log_savings(user_id)
        raise Exception(f"ABSTAIN: Confidence too low ({mock_confidence} < {threshold})")
    
    print(f"✅ [Qutato] Trust Verified. Proceeding to LLM call.")

def post_call_success_callback(kwargs):
    """
    Success Callback
    Runs after a successful LLM response to record usage.
    """
    response_obj = kwargs.get("response_obj")
    user_id = kwargs.get("additional_args", {}).get("user_id", "default_user")
    
    if response_obj:
        total_tokens = response_obj.get("usage", {}).get("total_tokens", 0)
        quota_manager.increment_usage(user_id, total_tokens)

# Registering custom callbacks with LiteLLM
litellm.input_callback = [pre_call_abstention_callback]
litellm.success_callback = [post_call_success_callback]
