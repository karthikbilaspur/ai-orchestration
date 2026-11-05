"""Optional LLM wrapper (used only as a Parser fallback)."""
from typing import Optional
import config


class LLMClient:
    def __init__(self):
        self._client = None
        if config.ANTHROPIC_API_KEY:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
            except ImportError:
                self._client = None

    @property
    def available(self) -> bool:
        return self._client is not None

    def complete(self, system: str, user: str, max_tokens: int = 100) -> Optional[str]:
        if not self.available:
            return None
        resp = self._client.messages.create(
            model=config.LLM_MODEL, max_tokens=max_tokens, system=system,
            messages=[{"role": "user", "content": user}])
        return "".join(b.text for b in resp.content if b.type == "text").strip()
