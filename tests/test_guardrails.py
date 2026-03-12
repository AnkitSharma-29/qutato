import httpx

def test_junk_blocking():
    url = "http://localhost:8000/v1/chat/completions"
    headers = {
        "X-API-KEY": "qutato_admin_secret_key",
        "X-LLM-API-KEY": "sk-dummy"
    }
    
    # Test Junk Prompt
    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "asdfghjkl"}] # Junk
    }
    
    try:
        response = httpx.post(url, json=payload, headers=headers)
        print(f"Junk Test - Status Code: {response.status_code}")
        print(f"Junk Test - Message: {response.json().get('detail')}")
    except Exception as e:
        print(f"Test Failed: {e}")

if __name__ == "__main__":
    test_junk_blocking()
