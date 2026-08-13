"""Type-safe configuration: environment variables, LLM parameters, feature flags.

Design goals
------------
* **No external deps required for default operation.** ``pyyaml`` is imported
  lazily so the skill can run in a stripped-down runtime that only ships the
  standard library; if ``defaults.yaml`` cannot be parsed, env-derived defaults
  are still applied.
* **Immutable & validated.** Configuration objects are frozen dataclasses;
  every field is validated at construction time and a single
  :class:`ConfigError` is raised with a human-readable message on failure.
* **Environment-first.** Every tunable can be overridden via an environment
  variable, which is essential for 12-factor / containerised deployments.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Mapping

try:  # pragma: no cover - exercised when yaml is installed
    import yaml  # type: ignore
except Exception:  # pragma: no cover - fallback when yaml missing
    yaml = None  # type: ignore


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULTS_FILE = PROJECT_ROOT / "config" / "defaults.yaml"


class ConfigError(ValueError):
    """Raised when configuration values are invalid or inconsistent."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _coerce_bool(value: Any, *, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on", "y"}:
        return True
    if text in {"0", "false", "no", "off", "n"}:
        return False
    raise ConfigError(f"Cannot interpret {value!r} as a boolean flag.")


def _coerce_int(value: Any, *, default: int, minimum: int | None = None) -> int:
    if value is None or value == "":
        return default
    try:
        out = int(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"Cannot interpret {value!r} as an integer.") from exc
    if minimum is not None and out < minimum:
        raise ConfigError(f"Value {out} is below minimum {minimum}.")
    return out


def _coerce_str(value: Any, *, default: str) -> str:
    if value is None or value == "":
        return default
    return str(value).strip()


# ---------------------------------------------------------------------------
# Configuration blocks
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LLMParams:
    """Parameters governing LLM calls (tokens, temperature, retries, timeouts).

    These are *execution* parameters, not model-selection knobs. The provider
    is configured separately so the skill can run fully offline using the
    deterministic fallback engine.
    """

    provider: str = "fallback"
    model: str = "claude-sonnet-4-5"
    temperature: float = 0.2
    max_tokens: int = 4096
    request_timeout_seconds: float = 30.0
    max_retries: int = 3
    retry_backoff_seconds: float = 1.5
    fallback_on_error: bool = True

    def __post_init__(self) -> None:
        if not self.model:
            raise ConfigError("LLMParams.model must be a non-empty string.")
        if not (0.0 <= self.temperature <= 2.0):
            raise ConfigError(
                f"temperature must be within [0.0, 2.0]; got {self.temperature}."
            )
        if self.max_tokens <= 0:
            raise ConfigError("max_tokens must be positive.")
        if self.request_timeout_seconds <= 0:
            raise ConfigError("request_timeout_seconds must be positive.")
        if self.max_retries < 0:
            raise ConfigError("max_retries cannot be negative.")
        if self.retry_backoff_seconds < 0:
            raise ConfigError("retry_backoff_seconds cannot be negative.")


@dataclass(frozen=True)
class FeatureFlags:
    """System-wide feature flags controlling optional behaviour."""

    enable_authentication_referral_guard: bool = True
    enable_chain_of_thought_routing: bool = True
    enable_tool_invocation: bool = True
    enable_hook_events: bool = True
    enable_provenance_research: bool = True
    enable_material_analysis: bool = True
    enable_structured_logging: bool = True
    strict_disclaimer_mode: bool = True
    max_concurrent_sub_advisors: int = 4

    def __post_init__(self) -> None:
        if self.max_concurrent_sub_advisors <= 0:
            raise ConfigError("max_concurrent_sub_advisors must be >= 1.")


@dataclass(frozen=True)
class Paths:
    """Resolved filesystem paths used by the skill."""

    project_root: Path = PROJECT_ROOT
    references_dir: Path = PROJECT_ROOT / "references"
    assets_dir: Path = PROJECT_ROOT / "assets"
    schemas_dir: Path = PROJECT_ROOT / "assets" / "schemas"
    scripts_dir: Path = PROJECT_ROOT / "scripts"
    state_dir: Path = PROJECT_ROOT / ".skill_state"

    def ensure_runtime_dirs(self) -> None:
        """Create writable runtime directories (state, logs) if absent."""
        self.state_dir.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Settings:
    """Top-level immutable settings object."""

    app_name: str = "historical-cartography-research-advisor"
    environment: str = "production"
    log_level: str = "INFO"
    llm: LLMParams = field(default_factory=LLMParams)
    flags: FeatureFlags = field(default_factory=FeatureFlags)
    paths: Paths = field(default_factory=Paths)

    def __post_init__(self) -> None:
        if self.environment not in {"development", "staging", "production", "test"}:
            raise ConfigError(f"Unknown environment: {self.environment!r}.")
        level = self.log_level.upper()
        if level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ConfigError(f"Unknown log_level: {self.log_level!r}.")
        # normalise log level casing for downstream consumers
        if level != self.log_level:
            object.__setattr__(self, "log_level", level)

    def with_overrides(self, **changes: Any) -> "Settings":
        """Return a new :class:`Settings` with ``changes`` applied (immutable update)."""
        return replace(self, **changes)


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


_DEFAULT_YAML: Mapping[str, Any] = {
    "app_name": "historical-cartography-research-advisor",
    "environment": "production",
    "log_level": "INFO",
    "llm": {
        "provider": "fallback",
        "model": "claude-sonnet-4-5",
        "temperature": 0.2,
        "max_tokens": 4096,
        "request_timeout_seconds": 30.0,
        "max_retries": 3,
        "retry_backoff_seconds": 1.5,
        "fallback_on_error": True,
    },
    "flags": {
        "enable_authentication_referral_guard": True,
        "enable_chain_of_thought_routing": True,
        "enable_tool_invocation": True,
        "enable_hook_events": True,
        "enable_provenance_research": True,
        "enable_material_analysis": True,
        "enable_structured_logging": True,
        "strict_disclaimer_mode": True,
        "max_concurrent_sub_advisors": 4,
    },
}


def _load_yaml_defaults() -> Mapping[str, Any]:
    if yaml is None or not DEFAULTS_FILE.exists():
        return _DEFAULT_YAML
    try:
        with DEFAULTS_FILE.open("r", encoding="utf-8") as handle:
            loaded = yaml.safe_load(handle) or {}
    except Exception:
        # Never let a malformed defaults file take the whole skill down.
        return _DEFAULT_YAML
    if not isinstance(loaded, Mapping):
        return _DEFAULT_YAML
    # Merge loaded over builtin defaults (shallow per-section merge).
    merged: dict[str, Any] = {}
    for key, value in _DEFAULT_YAML.items():
        if isinstance(value, Mapping) and isinstance(loaded.get(key), Mapping):
            merged[key] = {**value, **loaded[key]}
        else:
            merged[key] = loaded.get(key, value)
    return merged


def _env_overrides(defaults: Mapping[str, Any]) -> dict[str, Any]:
    env = os.environ
    llm_defaults = dict(defaults.get("llm", {}))
    flag_defaults = dict(defaults.get("flags", {}))

    llm = LLMParams(
        provider=_coerce_str(env.get("HCRA_LLM_PROVIDER"), default=llm_defaults.get("provider", "fallback")),
        model=_coerce_str(env.get("HCRA_LLM_MODEL"), default=llm_defaults.get("model", "claude-sonnet-4-5")),
        temperature=float(_coerce_str(env.get("HCRA_LLM_TEMPERATURE"), default=str(llm_defaults.get("temperature", 0.2))) or 0.2),
        max_tokens=_coerce_int(env.get("HCRA_LLM_MAX_TOKENS"), default=llm_defaults.get("max_tokens", 4096), minimum=1),
        request_timeout_seconds=float(_coerce_int(env.get("HCRA_LLM_TIMEOUT"), default=int(llm_defaults.get("request_timeout_seconds", 30)), minimum=1)),
        max_retries=_coerce_int(env.get("HCRA_LLM_MAX_RETRIES"), default=llm_defaults.get("max_retries", 3), minimum=0),
        retry_backoff_seconds=float(_coerce_str(env.get("HCRA_LLM_BACKOFF"), default=str(llm_defaults.get("retry_backoff_seconds", 1.5)))),
        fallback_on_error=_coerce_bool(env.get("HCRA_LLM_FALLBACK_ON_ERROR"), default=llm_defaults.get("fallback_on_error", True)),
    )

    flags = FeatureFlags(
        enable_authentication_referral_guard=_coerce_bool(
            env.get("HCRA_FLAG_AUTH_GUARD"), default=flag_defaults.get("enable_authentication_referral_guard", True)
        ),
        enable_chain_of_thought_routing=_coerce_bool(
            env.get("HCRA_FLAG_COT_ROUTING"), default=flag_defaults.get("enable_chain_of_thought_routing", True)
        ),
        enable_tool_invocation=_coerce_bool(
            env.get("HCRA_FLAG_TOOLS"), default=flag_defaults.get("enable_tool_invocation", True)
        ),
        enable_hook_events=_coerce_bool(
            env.get("HCRA_FLAG_HOOKS"), default=flag_defaults.get("enable_hook_events", True)
        ),
        enable_provenance_research=_coerce_bool(
            env.get("HCRA_FLAG_PROVENANCE"), default=flag_defaults.get("enable_provenance_research", True)
        ),
        enable_material_analysis=_coerce_bool(
            env.get("HCRA_FLAG_MATERIALS"), default=flag_defaults.get("enable_material_analysis", True)
        ),
        enable_structured_logging=_coerce_bool(
            env.get("HCRA_FLAG_STRUCTURED_LOGS"), default=flag_defaults.get("enable_structured_logging", True)
        ),
        strict_disclaimer_mode=_coerce_bool(
            env.get("HCRA_FLAG_STRICT_DISCLAIMER"), default=flag_defaults.get("strict_disclaimer_mode", True)
        ),
        max_concurrent_sub_advisors=_coerce_int(
            env.get("HCRA_MAX_CONCURRENT_ADVISORS"),
            default=flag_defaults.get("max_concurrent_sub_advisors", 4),
            minimum=1,
        ),
    )

    return {
        "app_name": _coerce_str(env.get("HCRA_APP_NAME"), default=defaults.get("app_name", "historical-cartography-research-advisor")),
        "environment": _coerce_str(env.get("HCRA_ENV"), default=defaults.get("environment", "production")),
        "log_level": _coerce_str(env.get("HCRA_LOG_LEVEL"), default=defaults.get("log_level", "INFO")),
        "llm": llm,
        "flags": flags,
    }


def load_settings(**explicit_overrides: Any) -> Settings:
    """Build a validated :class:`Settings` from ``defaults.yaml`` + environment.

    Optional ``explicit_overrides`` are applied last and win over env vars,
    which is useful in tests and for programmatic callers.
    """
    defaults = _load_yaml_defaults()
    resolved = _env_overrides(defaults)
    resolved.update(explicit_overrides)
    settings = Settings(**resolved)  # type: ignore[arg-type]
    settings.paths.ensure_runtime_dirs()
    return settings
