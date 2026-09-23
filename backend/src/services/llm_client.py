"""Unified LLM client — OpenAI SDK pointing to local Ollama (Qwen3-8B)."""
from __future__ import annotations

import logging
from typing import Optional

from openai import OpenAI

from .config import get_config

logger = logging.getLogger("astral.llm_client")


class LLMClient:
    """Single LLM client for all AI operations.

    Uses OpenAI SDK pointing to Ollama at http://localhost:11434/v1.
    """

    def __init__(self):
        cfg = get_config()
        self._base_url = cfg["llm"]["base_url"]
        self._model = cfg["llm"]["model"]
        self._max_tokens = cfg["llm"]["max_tokens"]
        self._temperature = cfg["llm"]["temperature"]
        self._api_key = cfg["llm"].get("api_key", "dummy")

        self._client = OpenAI(
            base_url=self._base_url,
            api_key=self._api_key,
            timeout=120,
        )

    @property
    def model(self) -> str:
        return self._model

    def chat(
        self,
        system: str,
        user: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False,
    ) -> str:
        """Call LLM chat completion.

        Args:
            system: System prompt
            user: User message
            max_tokens: Override default max_tokens
            temperature: Override default temperature
            stream: If True, stream and collect full response

        Returns:
            LLM response text
        """
        msgs = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        kwargs = dict(
            model=self._model,
            messages=msgs,
            max_tokens=max_tokens or self._max_tokens,
            temperature=temperature if temperature is not None else self._temperature,
        )

        if stream:
            kwargs["stream"] = True
            chunks = []
            for chunk in self._client.chat.completions.create(**kwargs):
                if chunk.choices and chunk.choices[0].delta.content:
                    chunks.append(chunk.choices[0].delta.content)
            return "".join(chunks)
        else:
            resp = self._client.chat.completions.create(**kwargs)
            return resp.choices[0].message.content or ""

    def chat_raw(self, messages: list[dict], max_tokens: Optional[int] = None, temperature: Optional[float] = None) -> str:
        """Call LLM with raw messages list.

        Args:
            messages: Full messages list (system/user/assistant)
            max_tokens: Override default
            temperature: Override default

        Returns:
            LLM response text
        """
        return self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            max_tokens=max_tokens or self._max_tokens,
            temperature=temperature if temperature is not None else self._temperature,
        ).choices[0].message.content or ""

    def health_check(self) -> dict:
        """Test LLM connectivity."""
        try:
            resp = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=5,
            )
            text = resp.choices[0].message.content or ""
            return {"ok": True, "model": self._model, "base_url": self._base_url, "sample": text}
        except Exception as e:
            logger.error(f"LLM health check failed: {e}")
            return {"ok": False, "model": self._model, "base_url": self._base_url, "error": str(e)}


# Singleton
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get singleton LLM client."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


def llm_chat(system: str, user: str, max_tokens: int = 4096, temperature: float = 0.7) -> str:
    """Convenience function for quick LLM calls."""
    client = get_llm_client()
    return client.chat(system=system, user=user, max_tokens=max_tokens, temperature=temperature)
