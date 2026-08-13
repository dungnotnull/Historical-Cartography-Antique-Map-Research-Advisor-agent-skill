"""Stdlib HTTP LLM provider adapters.

Real, functional adapters using only the Python standard library (``urllib``)
so the skill can call a live model without third-party HTTP deps. Each adapter
implements the ``ProviderBackend`` protocol from ``skill/llm/client.py`` and is
registered via ``register_provider`` so ``get_llm_client`` picks it up when the
configured ``LLMParams.provider`` matches.

Currently provides an Anthropic Messages API adapter. Add OpenAI-style adapters
by following the same pattern and registering them in
``register_default_providers``.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from config import LLMParams

from .client import register_provider

_ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
_ANTHROPIC_VERSION = "2023-06-01"


class AnthropicProvider:
    """Calls the Anthropic Messages API via ``urllib``.

    Reads the API key from ``HCRA_ANTHROPIC_API_KEY`` or ``ANTHROPIC_API_KEY``.
    Raises on HTTP/non-2xx errors so the ``LLMClient`` retry/fallback policy
    applies uniformly.
    """

    def __call__(self, *, system: str, user: str, params: LLMParams) -> str:
        api_key = os.environ.get("HCRA_ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("No Anthropic API key set (HCRA_ANTHROPIC_API_KEY / ANTHROPIC_API_KEY).")

        body = json.dumps({
            "model": params.model,
            "max_tokens": params.max_tokens,
            "temperature": params.temperature,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }).encode("utf-8")

        request = urllib.request.Request(
            _ANTHROPIC_URL,
            data=body,
            method="POST",
            headers={
                "content-type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": _ANTHROPIC_VERSION,
            },
        )
        timeout = params.request_timeout_seconds
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed URL
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"Anthropic API HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')[:200]}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Anthropic API network error: {exc.reason}") from exc

        # Anthropic returns {"content": [{"type":"text","text": "..."}], ...}
        content = payload.get("content") or []
        for block in content:
            if block.get("type") == "text" and block.get("text"):
                return str(block["text"])
        # No text block — surface the raw payload for debugging.
        return json.dumps(payload)


_OPENAI_URL = "https://api.openai.com/v1/chat/completions"


class OpenAIProvider:
    """Calls the OpenAI Chat Completions API via ``urllib``.

    Reads the API key from ``HCRA_OPENAI_API_KEY`` or ``OPENAI_API_KEY``.
    Raises on missing key / HTTP / network errors so the ``LLMClient``
    retry/fallback policy applies uniformly.
    """

    def __call__(self, *, system: str, user: str, params: LLMParams) -> str:
        api_key = os.environ.get("HCRA_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("No OpenAI API key set (HCRA_OPENAI_API_KEY / OPENAI_API_KEY).")

        body = json.dumps({
            "model": params.model,
            "max_tokens": params.max_tokens,
            "temperature": params.temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }).encode("utf-8")

        request = urllib.request.Request(
            _OPENAI_URL,
            data=body,
            method="POST",
            headers={
                "content-type": "application/json",
                "authorization": f"Bearer {api_key}",
            },
        )
        timeout = params.request_timeout_seconds
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed URL
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"OpenAI API HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')[:200]}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"OpenAI API network error: {exc.reason}") from exc

        choices = payload.get("choices") or []
        if choices:
            content = choices[0].get("message", {}).get("content")
            if content:
                return str(content)
        return json.dumps(payload)


def register_default_providers() -> None:
    """Register the built-in stdlib provider adapters."""
    register_provider("anthropic", AnthropicProvider())
    register_provider("openai", OpenAIProvider())
