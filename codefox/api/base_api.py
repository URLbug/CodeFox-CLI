import abc
import dataclasses
from typing import Any, Protocol

from codefox.utils.helper import Helper


class ExecuteResponse(Protocol):
    text: str


@dataclasses.dataclass
class Response:
    text: str


class BaseAPI(abc.ABC):
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__()
        try:
            self.config: dict[str, Any] = config or Helper.read_yml(
                ".codefox.yml"
            )
        except FileNotFoundError:
            raise RuntimeError(
                "Configuration file '.codefox.yml' not found. "
                "Please run 'codefox --command init' first."
            )

        if "model" not in self.config or not self.config.get("model"):
            raise ValueError("Missing required key 'model'")

        self.model_config: dict[str, Any] = self.config["model"]
        if "name" not in self.model_config or not self.model_config.get(
            "name"
        ):
            raise ValueError("Key 'model' missing required value key 'name'")

        if not self.model_config["name"].strip():
            raise ValueError("Model name cannot be empty")

        if "max_tokens" not in self.model_config or not self.model_config.get(
            "max_tokens"
        ):
            self.model_config["max_tokens"] = None

        if (
            "max_completion_tokens" not in self.model_config
            or not self.model_config.get("max_completion_tokens")
        ):
            self.model_config["max_completion_tokens"] = None

        if "temperature" not in self.model_config or not self.model_config.get(
            "temperature"
        ):
            self.model_config["temperature"] = 0.2

        if "timeout" not in self.model_config or not self.model_config.get(
            "timeout"
        ):
            self.model_config["timeout"] = 600

    @abc.abstractmethod
    def check_model(self, name: str) -> bool:
        pass

    @abc.abstractmethod
    def execute(self, diff_text: str) -> ExecuteResponse:
        pass

    @abc.abstractmethod
    def check_connection(self) -> bool:
        pass

    @abc.abstractmethod
    def upload_files(self, path_files: str) -> tuple[bool, Any]:
        pass

    @abc.abstractmethod
    def remove_files(self) -> None:
        pass

    def get_tag_models(self) -> list[str]:
        return []
