"""BaseAgent + LLM provider abstraction. Mock works offline; real providers via env."""
from __future__ import annotations
import os

class LLMProvider:
    def generate(self, prompt: str) -> str:
        raise NotImplementedError

class MockProvider(LLMProvider):
    """Deterministic template provider — no API key, great for learning/tests."""
    def generate(self, prompt: str) -> str:
        # Echo a structured response the agents can parse. Real LLM would do this better.
        return prompt  # agents build content from prompt context in mock mode (see agents)

def get_provider() -> LLMProvider:
    name = os.getenv("LLM_PROVIDER", "mock").lower()
    if name == "openai":
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            class OpenAIProvider(LLMProvider):
                def generate(self, prompt: str) -> str:
                    r = client.chat.completions.create(model=model, messages=[{"role":"user","content":prompt}], temperature=0.7)
                    return r.choices[0].message.content or ""
            return OpenAIProvider()
        except Exception as e:
            print(f"[warn] OpenAI unavailable ({e}), falling back to MockProvider")
            return MockProvider()
    if name == "anthropic":
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")
            class AnthropicProvider(LLMProvider):
                def generate(self, prompt: str) -> str:
                    r = client.messages.create(model=model, max_tokens=2000, messages=[{"role":"user","content":prompt}])
                    return "".join(b.text for b in r.content if hasattr(b, "text"))
            return AnthropicProvider()
        except Exception as e:
            print(f"[warn] Anthropic unavailable ({e}), falling back to MockProvider")
            return MockProvider()
    return MockProvider()

class BaseAgent:
    name = "BaseAgent"
    def __init__(self, provider: LLMProvider | None = None):
        self.llm = provider or get_provider()
    def log(self, msg: str):
        print(f"[{self.name}] {msg}")
