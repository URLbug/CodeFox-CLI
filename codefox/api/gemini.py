import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from google import genai
from google.genai import types
from rich import print
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from codefox.api.base_api import BaseAPI, ExecuteResponse
from codefox.prompts.prompt_template import PromptTemplate
from codefox.utils.helper import Helper


class Gemini(BaseAPI):
    default_model_name = "gemini-2.0-flash"
    MAX_WORKERS = 10

    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.store = None
        self.client = genai.Client(api_key=os.getenv("CODEFOX_API_KEY"))

    def check_model(self, name: str) -> bool:
        return name in self.get_tag_models()

    def check_connection(self) -> bool:
        try:
            self.client.models.list()
            return True
        except Exception:
            return False

    def get_tag_models(self) -> list:
        response = self.client.models.list()
        return [
            model.name.replace("models/", "")
            for model in response.page
            if "generateContent" in model.supported_actions
        ]

    def upload_files(self, path_files: str) -> tuple:
        super().upload_files(path_files)

        ignored_paths = Helper.read_codefoxignore()

        try:
            store = self.client.file_search_stores.create(
                config={"display_name": "CodeFox File Store"}
            )
        except Exception as e:
            return False, f"Error creating file search store: {e}"

        if self.config.get("diff_only", False):
            self.store = store
            return True, None

        valid_files = [
            f
            for f in Helper.get_all_files(path_files)
            if not any(ignored in f for ignored in ignored_paths)
        ]

        operations = self._upload_thread_pool_files(store, valid_files)
        if not operations:
            return True, None

        print(
            "[yellow]Waiting for Gemini API "
            "to process uploaded files...[/yellow]"
        )
        total = len(operations)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("Processing files...", total=total)

            timeout = self.model_config["timeout"]
            start_time = time.time()
            pending_ops = {op.name: op for op in operations}
            while pending_ops:
                if time.time() - start_time > timeout:
                    return False, "Gemini file processing timed out."

                for name in list(pending_ops.keys()):
                    op = self.client.operations.get(pending_ops[name])
                    if op.done:
                        if op.error:
                            print(
                                f"File processing failed: {op.error.message}"
                            )
                        pending_ops.pop(name)

                done_count = len(operations) - len(pending_ops)
                progress.update(task, completed=done_count)

                if not pending_ops:
                    break
                time.sleep(2)

        self.store = store
        return True, None

    def remove_files(self):
        if self.store is not None:
            try:
                self.client.file_search_stores.delete(
                    name=self.store.name,
                    config=types.DeleteFileSearchStoreConfig(force=True),
                )
                print(
                    "Successfully removed "
                    f"file search store: {self.store.name}"
                )
            except Exception as e:
                print(
                    f"Error removing file search store {self.store.name}: {e}"
                )
        else:
            print("No file search store to remove")

    def execute(self, diff_text: str) -> ExecuteResponse:
        system_prompt = PromptTemplate(self.config)
        content = (
            "Analyze the following git diff"
            f"and identify potential risks:\n\n{diff_text}"
        )

        return self.client.models.generate_content(
            model=self.model_config["name"],
            contents=content,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt.get(),
                temperature=self.model_config["temperature"],
                max_output_tokens=self.model_config["max_tokens"],
                tools=[
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[self.store.name]
                        )
                    )
                ],
            ),
        )

    def _upload_thread_pool_files(
        self, store: types.FileSearchStore, valid_files: list | None = None
    ) -> list:
        """
        Upload many files to Gemini store
        """

        valid_files = valid_files or []
        if not valid_files:
            return []

        operations = []
        with Progress() as progress:
            task = progress.add_task(
                "[bold cyan]Uploading codebase...[/]", total=len(valid_files)
            )

            with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
                futures = {
                    executor.submit(
                        self._upload_single_file, file, store
                    ): file
                    for file in valid_files
                }

                for future in as_completed(futures):
                    upload_op, error = future.result()

                    if error:
                        failed_file, exc = error
                        print(
                            f"[red]Error uploading {failed_file}: {exc}[/red]"
                        )
                    else:
                        operations.append(upload_op)

                    progress.advance(task)

        return operations

    def _upload_single_file(
        self, file_path: str, store: types.FileSearchStore
    ) -> tuple:
        """
        Upload single file to gemini store
        """
        try:
            file_stores = self.client.file_search_stores

            upload_op = file_stores.upload_to_file_search_store(
                file_search_store_name=store.name,
                file=file_path,
                config={"mime_type": "text/plain"},
            )
            return upload_op, None
        except Exception as e:
            return None, (file_path, e)
