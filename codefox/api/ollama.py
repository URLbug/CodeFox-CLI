import os
from typing import Any

import requests
from ollama import ChatResponse, Client

from codefox.api.base_api import BaseAPI, ExecuteResponse, Response
from codefox.prompts.prompt_template import PromptTemplate
from codefox.utils.local_rag import LocalRAG


class Ollama(BaseAPI):
    default_model_name = "gemma3:12b"
    default_embedding = "BAAI/bge-small-en-v1.5"
    base_url = "https://ollama.com"

    def __init__(self, config=None):
        super().__init__(config)

        if self.model_config.get("base_url"):
            self.base_url = self.model_config.get("base_url")

        if "embedding" not in self.model_config or not self.model_config.get(
            "embedding"
        ):
            self.model_config["embedding"] = self.default_embedding

        api_key = os.getenv("CODEFOX_API_KEY")

        headers = None
        if api_key and api_key != "null":
            headers = {
                "Authorization": f"Bearer {api_key}",
            }

        self.rag = None

        self.client = Client(host=self.base_url, headers=headers)

    def check_model(self, name: str) -> bool:
        return name in self.get_tag_models()

    def check_connection(self):
        try:
            self.client.show(self.default_model_name)
            return True
        except Exception:
            return False

    def upload_files(self, path_files: str) -> tuple[bool, Any]:
        if self.review_config["diff_only"]:
            return True, None

        self.rag = LocalRAG(self.model_config["embedding"], path_files)
        self.rag.build()

        return True, None

    def remove_files(self):
        pass

    def execute(self, diff_text: str) -> ExecuteResponse:
        system_prompt = PromptTemplate(self.config)

        rag_context = ""
        if self.rag:
            hits = self.rag.search(diff_text, k=5)
            rag_context = "\n\n".join(hits)

        content = f"""
        You are performing a DIFF AUDIT.

        Your task:
        Detect BEHAVIOR CHANGE caused by the modified lines.

        DO NOT:
        - explain the codebase
        - describe architecture
        - summarize classes

        If you do not compare OLD vs NEW behavior → the answer is INVALID.

        ──────── DIFF ────────
        GIT DIFF WITH +/- MARKERS. ONLY THESE LINES CHANGED.
        {diff_text}

        ──────── RELEVANT CONTEXT ────────
        (USE ONLY IF NEEDED TO TRACE DATA FLOW)
        Do NOT analyze this section by itself.
        Use it only to understand symbols referenced in the diff.

        {rag_context}

        ──────── REQUIRED REASONING ────────

        1. List the changed lines
        2. For each change:
        OLD behavior →
        NEW behavior →
        3. What execution path now behaves differently?
        4. What can break?

        If there is no behavioral change → explicitly say:
        NO BEHAVIORAL CHANGE.
        """

        chat_response: ChatResponse = self.client.chat(
            model=self.model_config["name"],
            messages=[
                {"role": "system", "content": system_prompt.get()},
                {"role": "user", "content": content},
            ],
        )

        response = Response(chat_response.message.content)
        return response

    def get_tag_models(self) -> list[str]:
        response = requests.get(f"{self.base_url}/api/tags")

        if response.status_code == 200:
            data = response.json()
            return [
                model["name"] for model in data["models"] if model.get("name")
            ]
        else:
            return []
