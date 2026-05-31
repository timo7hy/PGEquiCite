# dev/models/openai.py
import os
import openai
from .base import BaseModelClient, ModelResponse


class OpenAIClient(BaseModelClient):
    provider = "openai"
    model_id  = "gpt-4o"

    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY not set.")
        self._client = openai.OpenAI(api_key=api_key)

    def generate(self, prompt: str) -> ModelResponse:
        try:
            resp = self._client.chat.completions.create(
                model=self.model_id,
                max_tokens=2048,
                temperature=0,
                messages=[{"role": "user", "content": prompt}],
            )
            return ModelResponse(self.model_id, self.provider,
                                 resp.choices[0].message.content, None)
        except Exception as e:
            return ModelResponse(self.model_id, self.provider, "", str(e))
