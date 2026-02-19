import enum
from typing import Type

from codefox.api.base_api import BaseAPI
from codefox.api.gemini import Gemini
from codefox.api.qwen import Qwen


class ModelEnum(enum.Enum):
    GEMINI = Gemini
    QWEN = Qwen

    @property
    def api_class(self) -> Type[BaseAPI]:
        return self.value

    @classmethod
    def by_name(cls, name: str) -> "ModelEnum":
        try:
            return cls[name.upper()]
        except KeyError:
            available = [e.name.lower() for e in cls]
            raise ValueError(
                f"Unknown provider '{name}'. Available: {available}"
            ) from None

    @classmethod
    def names(cls) -> list[str]:
        return [e.name.lower() for e in cls]
