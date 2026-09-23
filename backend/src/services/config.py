"""Config loader — reads local_config.yaml."""
from __future__ import annotations

import os
import logging
from pathlib import Path

logger = logging.getLogger("astral.config")

DEFAULT_CONFIG = {
    "llm": {
        "provider": "ollama",
        "base_url": "http://localhost:11434/v1",
        "model": "qwen3-8b-uc:latest",
        "max_tokens": 4096,
        "temperature": 0.7,
        "api_key": "dummy",
    },
    "api_keys": {
        "jyotish": "",
    },
}

_config: dict | None = None


def load_config() -> dict:
    """Load config from local_config.yaml, merge with defaults."""
    global _config
    if _config is not None:
        return _config

    # Search up from cwd for config
    config_path = None
    for parent in [Path.cwd(), *Path.cwd().parents]:
        candidate = parent / "src" / "config" / "local_config.yaml"
        if candidate.exists():
            config_path = candidate
            break
        candidate = parent / "local_config.yaml"
        if candidate.exists():
            config_path = candidate
            break

    if config_path is None:
        # Fallback: create config dir and file
        config_dir = Path(__file__).resolve().parent.parent / "config"
        config_dir.mkdir(exist_ok=True)
        config_path = config_dir / "local_config.yaml"
        if not config_path.exists():
            import yaml
            config_path.write_text(
                "llm:\n"
                "  provider: ollama\n"
                "  base_url: http://localhost:11434/v1\n"
                "  model: qwen3-8b-uc:latest\n"
                "  max_tokens: 4096\n"
                "  temperature: 0.7\n"
                "  api_key: dummy\n"
                "api_keys:\n"
                "  jyotish: ''\n",
                encoding="utf-8",
            )
            logger.info(f"Created default config at {config_path}")

    try:
        import yaml
        with open(config_path, encoding="utf-8") as f:
            file_config = yaml.safe_load(f) or {}

        # Deep merge
        _config = _deep_merge(DEFAULT_CONFIG, file_config)
        logger.info(f"Loaded config from {config_path}")
    except Exception as e:
        logger.warning(f"Failed to load config from {config_path}: {e}, using defaults")
        _config = DEFAULT_CONFIG.copy()

    # Override from environment
    for key, env_var in [
        ("llm.base_url", "ASTRAL_LLM_BASE_URL"),
        ("llm.model", "ASTRAL_LLM_MODEL"),
        ("llm.api_key", "ASTRAL_LLM_API_KEY"),
        ("llm.provider", "ASTRAL_LLM_PROVIDER"),
    ]:
        val = os.getenv(env_var)
        if val is not None:
            parts = key.split(".")
            d = _config
            for p in parts[:-1]:
                d = d.setdefault(p, {})
            d[parts[-1]] = val

    return _config


def get_config() -> dict:
    """Get current config (load if needed)."""
    if _config is None:
        return load_config()
    return _config


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge override into base."""
    result = base.copy()
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result
