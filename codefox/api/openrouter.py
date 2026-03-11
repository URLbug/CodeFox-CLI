import os
from typing import Any

from openai import OpenAI

from codefox.api.base_api import BaseAPI, ExecuteResponse, Response
from codefox.prompts.prompt_template import PromptTemplate


class OpenRouter(BaseAPI):
    default_model_name = "qwen/qwen3-vl-30b-a3b-thinking"
    base_url = "https://openrouter.ai/api/v1"
    default_max_rag_chars = 4096
    default_max_diff_chars = 16_000

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)

        if "base_url" in self.model_config or self.model_config.get(
            "base_url"
        ):
            self.base_url = self.model_config["base_url"]

        self.client = OpenAI(
            api_key=os.getenv("CODEFOX_API_KEY"), base_url=self.base_url
        )

    def check_connection(self) -> tuple[bool, Any]:
        try:
            self.client.models.list()
            return True, None
        except Exception as e:
            return False, e

    def check_model(self, name: str) -> bool:
        return name in self.get_tag_models()

    def execute(self, diff_text: str = "") -> ExecuteResponse:
        rag_context = self.get_context(diff_text)

        system_prompt = PromptTemplate(self.config)
        context_prompt = PromptTemplate(
            {"files_context": rag_context, "diff_text": diff_text}, "content"
        )
        content = context_prompt.get()

        completion = self.client.chat.completions.create(
            model=self.model_config["name"],
            temperature=self.model_config["temperature"],
            timeout=self.model_config.get("timeout", 600),
            max_tokens=self.model_config["max_tokens"],
            max_completion_tokens=self.model_config["max_completion_tokens"],
            messages=[
                {"role": "system", "content": system_prompt.get()},
                {"role": "user", "content": content},
            ],
        )

        raw = completion.choices[0].message.content
        return Response(text=raw if raw is not None else "")

    def remove_files(self) -> None:
        pass

    def upload_files(self, path_files: str) -> tuple[bool, Any]:
        return super().upload_files(path_files)

    def get_tag_models(self) -> list:
        models = self.client.models.list()
        return [model.id for model in models]
