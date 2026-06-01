# dev/models/claude.py
import os
import anthropic
from .base import BaseModelClient, ModelResponse


class ClaudeClient(BaseModelClient):
    provider = "anthropic"
    model_id  = "claude-sonnet-4-5"

    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError("ANTHROPIC_API_KEY not set.")
        self._client = anthropic.Anthropic(api_key=api_key)

    def generate(self, prompt: str) -> ModelResponse:
        try:
            msg = self._client.messages.create(
                model=self.model_id,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )
            return ModelResponse(self.model_id, self.provider, msg.content[0].text, None)
        except Exception as e:
            return ModelResponse(self.model_id, self.provider, "", str(e))
