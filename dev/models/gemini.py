# dev/models/gemini.py
import os
from google import genai
from google.genai import types
from .base import BaseModelClient, ModelResponse


class GeminiClient(BaseModelClient):
    provider = "google"
    model_id  = "gemini-2.0-flash"

    def __init__(self):
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise EnvironmentError("GOOGLE_API_KEY not set.")
        self._client = genai.Client(api_key=api_key)

    def generate(self, prompt: str) -> ModelResponse:
        try:
            response = self._client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0,
                    max_output_tokens=2048,
                ),
            )
            return ModelResponse(self.model_id, self.provider, response.text, None)
        except Exception as e:
            return ModelResponse(self.model_id, self.provider, "", str(e))
