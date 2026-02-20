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

        self.model_config = self._processing_model_config(self.config["model"])
        self.review_config = self._processing_review_config(
            self.config["review"]
        )

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

    def _processing_review_config(
        self, review_config: dict[str, Any]
    ) -> dict[str, Any]:
        if "max_issues" not in review_config:
            review_config["max_issues"] = None

        if "suggest_fixes" not in review_config:
            review_config["suggest_fixes"] = True

        if "diff_only" not in review_config:
            review_config["diff_only"] = False

        return review_config

    def _processing_model_config(
        self, model_config: dict[str, Any]
    ) -> dict[str, Any]:
        if "name" not in model_config or not model_config.get("name"):
            raise ValueError("Key 'model' missing required value key 'name'")

        if not model_config["name"].strip():
            raise ValueError("Model name cannot be empty")

        if "max_tokens" not in model_config or not model_config.get(
            "max_tokens"
        ):
            model_config["max_tokens"] = None

        if "max_completion_tokens" not in model_config or not model_config.get(
            "max_completion_tokens"
        ):
            model_config["max_completion_tokens"] = None

        if "temperature" not in model_config or not model_config.get(
            "temperature"
        ):
            model_config["temperature"] = 0.2

        if "timeout" not in model_config or not model_config.get("timeout"):
            model_config["timeout"] = 600

        return model_config
