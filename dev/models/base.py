# dev/models/base.py
"""
Base class for all model clients.

To add a new provider:
1. Create models/your_provider.py subclassing BaseModelClient
2. Implement generate(prompt: str) -> ModelResponse
3. Set provider and model_id class attributes
4. Add to models/__init__.py and ALL_CLIENTS
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ModelResponse:
    model_id:      str
    provider:      str
    response_text: str
    error:         str | None


class BaseModelClient(ABC):
    provider: str = ""
    model_id: str = ""

    @abstractmethod
    def generate(self, prompt: str) -> ModelResponse: ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(provider={self.provider!r}, model={self.model_id!r})"
