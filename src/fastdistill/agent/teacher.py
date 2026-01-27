# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from fastdistill.errors import FastDistillUserError
from fastdistill.models.llms import AnthropicLLM, OllamaLLM, OpenAILLM, SGLangLLM


def _env_or_value(
    value: Optional[str], env_key: str, default: Optional[str] = None
) -> Optional[str]:
    if value:
        return value
    env_value = os.getenv(env_key)
    if env_value:
        return env_value
    return default


def build_teacher_llm(
    *,
    provider: str,
    model: Optional[str],
    base_url: Optional[str],
    api_key: Optional[str],
    api_key_env: Optional[str],
    generation_kwargs: Optional[Dict[str, Any]],
) -> object:
    provider = provider.lower()
    generation_kwargs = generation_kwargs or {}

    if provider in {"openrouter", "openai"}:
        default_base_url = (
            "https://openrouter.ai/api/v1" if provider == "openrouter" else None
        )
        resolved_model = _env_or_value(
            model, "OPENROUTER_MODEL", "deepseek/deepseek-v3.2"
        )
        resolved_base_url = _env_or_value(
            base_url, "OPENROUTER_BASE_URL", default_base_url
        )
        resolved_api_key = api_key or _env_or_value(
            None, api_key_env or "OPENROUTER_API_KEY"
        )
        if not resolved_api_key:
            resolved_api_key = os.getenv("OPENAI_API_KEY")
        return OpenAILLM(
            model=resolved_model,
            base_url=resolved_base_url,
            api_key=resolved_api_key,
            generation_kwargs=generation_kwargs,
        )

    if provider == "anthropic":
        resolved_model = _env_or_value(model, "ANTHROPIC_MODEL")
        if not resolved_model:
            raise FastDistillUserError(
                "Anthropic model is required (set ANTHROPIC_MODEL or config)."
            )
        resolved_api_key = api_key or _env_or_value(
            None, api_key_env or "ANTHROPIC_API_KEY"
        )
        resolved_base_url = _env_or_value(base_url, "ANTHROPIC_BASE_URL")
        return AnthropicLLM(
            model=resolved_model,
            api_key=resolved_api_key,
            base_url=resolved_base_url,
            generation_kwargs=generation_kwargs,
        )

    if provider == "ollama":
        resolved_model = _env_or_value(model, "OLLAMA_MODEL", "qwen3:0.6b")
        resolved_base_url = _env_or_value(
            base_url, "OLLAMA_HOST", "http://localhost:11434"
        )
        timeout = int(os.getenv("OLLAMA_TIMEOUT", "120"))
        return OllamaLLM(
            model=resolved_model,
            host=resolved_base_url,
            timeout=timeout,
            generation_kwargs=generation_kwargs,
        )

    if provider == "sglang":
        resolved_model = _env_or_value(
            model, "SGLANG_MODEL", "qwen/qwen2.5-0.5b-instruct"
        )
        resolved_base_url = _env_or_value(
            base_url, "SGLANG_BASE_URL", "http://127.0.0.1:30000/v1"
        )
        resolved_api_key = api_key or _env_or_value(
            None, api_key_env or "SGLANG_API_KEY"
        )
        return SGLangLLM(
            model=resolved_model,
            base_url=resolved_base_url,
            api_key=resolved_api_key,
            generation_kwargs=generation_kwargs,
        )

    raise FastDistillUserError(
        f"Unknown teacher provider '{provider}'. Use openrouter, openai, anthropic, ollama, or sglang."
    )
