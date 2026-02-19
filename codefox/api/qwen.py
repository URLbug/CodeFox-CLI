import os

from openai import OpenAI
from rich.progress import track

from codefox.api.base_api import BaseAPI, ExecuteResponse, Response
from codefox.prompts.prompt_template import PromptTemplate
from codefox.utils.helper import Helper


class Qwen(BaseAPI):
    default_model_name = "qwen/qwen3-vl-30b-a3b-thinking"
    base_url = "https://openrouter.ai/api/v1"

    def __init__(self, config=None):
        super().__init__(config)

        if "base_url" in self.model_config or self.model_config.get(
            "base_url"
        ):
            self.base_url = self.model_config["base_url"]

        if "qwen" not in self.model_config["name"]:
            raise ValueError("This API key is not compatible with Qwen models")

        self.files = None
        self.client = OpenAI(
            api_key=os.getenv("CODEFOX_API_KEY"),
            base_url=self.base_url,
            timeout=self.model_config["timeout"],
        )

    def check_connection(self) -> bool:
        try:
            self.client.models.list()
            return True
        except Exception:
            return False

    def check_model(self, name: str) -> bool:
        return name in self.get_tag_models()

    def execute(self, diff_text="") -> ExecuteResponse:
        super().execute(diff_text)

        system_prompt = PromptTemplate(self.config)
        content = (
            "Analyze the following git diff"
            f"and identify potential risks:\n\n{diff_text}"
        )

        completion = self.client.chat.completions.create(
            model=self.model_config["name"],
            temperature=self.model_config["temperature"],
            messages=[
                {"role": "system", "content": system_prompt.get()},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": content},
                        {"type": "text", "text": self._build_files_context()},
                    ],
                },
            ],
        )

        return Response(text=completion.choices[0].message.content)

    def remove_files(self) -> None:
        pass

    def upload_files(self, path_files: str) -> tuple:
        super().upload_files(path_files)

        ignored_paths = Helper.read_codefoxignore()

        if self.config.get("diff_only", False):
            return True, None

        valid_files = [
            f
            for f in Helper.get_all_files(path_files)
            if not any(ignored in f for ignored in ignored_paths)
        ]

        files = []

        for file in track(valid_files):
            try:
                with open(file, encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                files.append({"path": file, "content": content})
            except Exception:
                continue

        self.files = files
        return True, None

    def get_tag_models(self) -> list:
        models = self.client.models.list()
        return [model.id for model in models]

    def _build_files_context(self, max_chars: int = 12000) -> str:
        chunks = []

        for file in self.files:
            text = file["content"][:max_chars]

            chunks.append(f"<file path='{file['path']}'>\n{text}\n</file>")

        return "\n\n".join(chunks)
