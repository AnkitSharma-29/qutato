"""
Unit tests for the Qutato Universal Translator.

Tests all normalize/denormalize functions and auto-detection logic.
Run: $env:PYTHONPATH = "." ; python -m pytest tests/test_translator.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from qutato_enterprise.gateway.translator import (
    normalize_anthropic,
    normalize_gemini,
    normalize_ollama_chat,
    normalize_ollama_generate,
    denormalize_to_anthropic,
    denormalize_to_gemini,
    denormalize_to_ollama_chat,
    denormalize_to_ollama_generate,
    detect_format,
    normalize,
    denormalize,
)


# ===================================================================
#  NORMALIZE TESTS
# ===================================================================

class TestNormalizeAnthropic:
    def test_basic_message(self):
        body = {
            "model": "claude-3-opus-20240229",
            "max_tokens": 1024,
            "messages": [
                {"role": "user", "content": "What is the meaning of life?"}
            ]
        }
        result = normalize_anthropic(body)
        assert result["model"] == "claude-3-opus-20240229"
        assert result["max_tokens"] == 1024
        assert len(result["messages"]) == 1
        assert result["messages"][0]["role"] == "user"
        assert result["messages"][0]["content"] == "What is the meaning of life?"

    def test_system_prompt(self):
        body = {
            "model": "claude-3-sonnet",
            "system": "You are a helpful assistant.",
            "messages": [
                {"role": "user", "content": "Hello"}
            ]
        }
        result = normalize_anthropic(body)
        assert len(result["messages"]) == 2
        assert result["messages"][0]["role"] == "system"
        assert result["messages"][0]["content"] == "You are a helpful assistant."
        assert result["messages"][1]["role"] == "user"

    def test_content_blocks(self):
        body = {
            "model": "claude-3-opus",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "First part."},
                        {"type": "text", "text": "Second part."}
                    ]
                }
            ]
        }
        result = normalize_anthropic(body)
        assert result["messages"][0]["content"] == "First part.\nSecond part."


class TestNormalizeGemini:
    def test_basic_content(self):
        body = {
            "model": "gemini-pro",
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": "Explain quantum computing"}]
                }
            ]
        }
        result = normalize_gemini(body)
        assert result["model"] == "gemini-pro"
        assert len(result["messages"]) == 1
        assert result["messages"][0]["role"] == "user"
        assert result["messages"][0]["content"] == "Explain quantum computing"

    def test_model_role_maps_to_assistant(self):
        body = {
            "model": "gemini-pro",
            "contents": [
                {"role": "user", "parts": [{"text": "Hi"}]},
                {"role": "model", "parts": [{"text": "Hello!"}]},
                {"role": "user", "parts": [{"text": "How are you?"}]},
            ]
        }
        result = normalize_gemini(body)
        assert result["messages"][1]["role"] == "assistant"
        assert result["messages"][1]["content"] == "Hello!"

    def test_system_instruction(self):
        body = {
            "model": "gemini-pro",
            "systemInstruction": {
                "parts": [{"text": "You are a pirate."}]
            },
            "contents": [
                {"role": "user", "parts": [{"text": "Ahoy!"}]}
            ]
        }
        result = normalize_gemini(body)
        assert len(result["messages"]) == 2
        assert result["messages"][0]["role"] == "system"
        assert result["messages"][0]["content"] == "You are a pirate."

    def test_generation_config(self):
        body = {
            "model": "gemini-pro",
            "contents": [{"role": "user", "parts": [{"text": "Hi"}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 256
            }
        }
        result = normalize_gemini(body)
        assert result["temperature"] == 0.7
        assert result["max_tokens"] == 256


class TestNormalizeOllamaChat:
    def test_basic_chat(self):
        body = {
            "model": "llama3",
            "messages": [
                {"role": "user", "content": "Hello Llama"}
            ]
        }
        result = normalize_ollama_chat(body)
        assert result["model"] == "llama3"
        assert result["messages"][0]["content"] == "Hello Llama"

    def test_options(self):
        body = {
            "model": "llama3",
            "messages": [{"role": "user", "content": "Hi"}],
            "options": {"temperature": 0.5, "num_predict": 128}
        }
        result = normalize_ollama_chat(body)
        assert result["temperature"] == 0.5
        assert result["max_tokens"] == 128


class TestNormalizeOllamaGenerate:
    def test_basic_generate(self):
        body = {
            "model": "llama3",
            "prompt": "Why is the sky blue?"
        }
        result = normalize_ollama_generate(body)
        assert result["model"] == "llama3"
        assert len(result["messages"]) == 1
        assert result["messages"][0]["role"] == "user"
        assert result["messages"][0]["content"] == "Why is the sky blue?"

    def test_system_prompt(self):
        body = {
            "model": "llama3",
            "system": "You are a scientist.",
            "prompt": "Explain gravity."
        }
        result = normalize_ollama_generate(body)
        assert len(result["messages"]) == 2
        assert result["messages"][0]["role"] == "system"
        assert result["messages"][1]["role"] == "user"


# ===================================================================
#  DENORMALIZE TESTS
# ===================================================================

MOCK_OPENAI_RESPONSE = {
    "id": "chatcmpl-abc123",
    "object": "chat.completion",
    "model": "gpt-4o",
    "choices": [{
        "message": {"role": "assistant", "content": "Hello, world!"},
        "finish_reason": "stop"
    }],
    "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 5,
        "total_tokens": 15
    }
}


class TestDenormalizeAnthropic:
    def test_response_shape(self):
        result = denormalize_to_anthropic(MOCK_OPENAI_RESPONSE)
        assert result["type"] == "message"
        assert result["role"] == "assistant"
        assert result["content"][0]["type"] == "text"
        assert result["content"][0]["text"] == "Hello, world!"
        assert result["usage"]["input_tokens"] == 10
        assert result["usage"]["output_tokens"] == 5


class TestDenormalizeGemini:
    def test_response_shape(self):
        result = denormalize_to_gemini(MOCK_OPENAI_RESPONSE)
        assert len(result["candidates"]) == 1
        assert result["candidates"][0]["content"]["role"] == "model"
        assert result["candidates"][0]["content"]["parts"][0]["text"] == "Hello, world!"
        assert result["usageMetadata"]["totalTokenCount"] == 15


class TestDenormalizeOllama:
    def test_chat_response(self):
        result = denormalize_to_ollama_chat(MOCK_OPENAI_RESPONSE)
        assert result["message"]["role"] == "assistant"
        assert result["message"]["content"] == "Hello, world!"
        assert result["done"] is True

    def test_generate_response(self):
        result = denormalize_to_ollama_generate(MOCK_OPENAI_RESPONSE)
        assert result["response"] == "Hello, world!"
        assert result["done"] is True


# ===================================================================
#  AUTO-DETECTION TESTS
# ===================================================================

class TestDetectFormat:
    def test_openai(self):
        body = {
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": "Hello"}]
        }
        assert detect_format(body) == "openai"

    def test_anthropic_with_system(self):
        body = {
            "model": "claude-3-opus",
            "system": "You are helpful.",
            "messages": [{"role": "user", "content": "Hello"}]
        }
        assert detect_format(body) == "anthropic"

    def test_anthropic_with_content_blocks(self):
        body = {
            "model": "claude-3-opus",
            "messages": [{
                "role": "user",
                "content": [{"type": "text", "text": "Hello"}]
            }]
        }
        assert detect_format(body) == "anthropic"

    def test_gemini(self):
        body = {
            "model": "gemini-pro",
            "contents": [
                {"role": "user", "parts": [{"text": "Hello"}]}
            ]
        }
        assert detect_format(body) == "gemini"

    def test_ollama_generate(self):
        body = {
            "model": "llama3",
            "prompt": "Hello"
        }
        assert detect_format(body) == "ollama_generate"

    def test_unknown(self):
        body = {"foo": "bar"}
        assert detect_format(body) == "unknown"


# ===================================================================
#  ROUND-TRIP TESTS
# ===================================================================

class TestRoundTrip:
    """Verify that normalize → denormalize produces a valid shape."""

    def test_anthropic_round_trip(self):
        body = {
            "model": "claude-3-opus",
            "system": "Be helpful.",
            "messages": [{"role": "user", "content": "Hi"}]
        }
        internal = normalize(body, fmt="anthropic")
        assert internal["messages"][0]["role"] == "system"
        assert internal["messages"][1]["role"] == "user"

        output = denormalize(MOCK_OPENAI_RESPONSE, fmt="anthropic")
        assert output["type"] == "message"

    def test_gemini_round_trip(self):
        body = {
            "model": "gemini-pro",
            "contents": [{"role": "user", "parts": [{"text": "Hello"}]}]
        }
        internal = normalize(body, fmt="gemini")
        assert internal["messages"][0]["role"] == "user"

        output = denormalize(MOCK_OPENAI_RESPONSE, fmt="gemini")
        assert "candidates" in output

    def test_auto_detect_and_normalize(self):
        # Gemini body on generic normalize()
        body = {
            "model": "gemini-pro",
            "contents": [{"role": "user", "parts": [{"text": "Auto!"}]}]
        }
        internal = normalize(body)  # auto-detect
        assert internal["messages"][0]["content"] == "Auto!"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
