"""LLM client with graceful fallback.

This module is intentionally provider-agnostic: it exposes a single
:meth:`LLMClient.complete` method that takes a system+user prompt and returns
a string. Provider backends are plugged in via callables registered against
``LLMParams.provider``; if none is registered or a call fails, the configured
fallback policy is applied (retry with backoff, then return ``None`` so the
caller can fall back to the deterministic engine).
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Protocol

from config import LLMParams, load_settings

from ..errors import LLMError
from ..logging_utils import get_logger


class ProviderBackend(Protocol):
    def __call__(self, *, system: str, user: str, params: LLMParams) -> str: ...


@dataclass
class LLMClient:
    """Wraps a provider backend with retries and fallback policy."""

    params: LLMParams
    backend: ProviderBackend | None = None
    logger: Any = None

    def __post_init__(self) -> None:
        if self.logger is None:
            self.logger = get_logger()

    def complete(self, *, system: str, user: str) -> str | None:
        """Return a completion string, or ``None`` if all retries failed.

        ``None`` (rather than raising) signals callers to use the deterministic
        fallback engine; this keeps the request pipeline resilient.
        """
        if self.backend is None:
            self.logger.debug("llm.no_backend", extra={"provider": self.params.provider})
            return None
        last_error: Exception | None = None
        for attempt in range(1, self.params.max_retries + 1):
            try:
                self.logger.debug(
                    "llm.call.start",
                    extra={"provider": self.params.provider, "model": self.params.model, "attempt": attempt},
                )
                started = time.time()
                result = self.backend(system=system, user=user, params=self.params)
                elapsed = int((time.time() - started) * 1000)
                self.logger.info(
                    "llm.call.ok",
                    extra={"provider": self.params.provider, "attempt": attempt, "elapsed_ms": elapsed},
                )
                return result
            except Exception as exc:  # broad: any provider failure is retryable
                last_error = exc
                self.logger.warning(
                    "llm.call.error",
                    extra={"provider": self.params.provider, "attempt": attempt, "error": str(exc)},
                )
                if attempt < self.params.max_retries:
                    time.sleep(self.params.retry_backoff_seconds * attempt)
        if last_error is not None and not self.params.fallback_on_error:
            raise LLMError(f"LLM call failed after {self.params.max_retries} attempts: {last_error}")
        return None


_DEFAULT_CLIENT: LLMClient | None = None
_PROVIDERS: dict[str, ProviderBackend] = {}


def register_provider(name: str, backend: ProviderBackend) -> None:
    """Register a callable backend for a provider name (e.g. 'anthropic')."""
    _PROVIDERS[name] = backend


def get_llm_client(params: LLMParams | None = None) -> LLMClient:
    """Return a process-wide :class:`LLMClient` bound to the configured provider."""
    global _DEFAULT_CLIENT
    params = params or load_settings().llm
    # Lazily register built-in stdlib provider adapters (anthropic, ...).
    try:
        from .providers import register_default_providers
        register_default_providers()
    except Exception:
        pass
    if _DEFAULT_CLIENT is None or _DEFAULT_CLIENT.params != params:
        backend = _PROVIDERS.get(params.provider) if params.provider != "fallback" else None
        _DEFAULT_CLIENT = LLMClient(params=params, backend=backend)
    return _DEFAULT_CLIENT
