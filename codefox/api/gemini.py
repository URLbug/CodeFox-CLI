import os
import time

from rich import print
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeElapsedColumn
)

from google import genai
from google.genai import types

from codefox.promts.promt_template import PromtTemplate

from concurrent.futures import ThreadPoolExecutor, as_completed

from codefox.api.base_api import BaseAPI
from codefox.utils.helper import Helper


class Gemini(BaseAPI):
    MAX_WORKERS = 10
    SUPPORTED_EXTENSIONS = {
        '.py',
        '.js',
        '.java',
        '.cpp',
        '.c',
        '.cs',
        '.go',
        '.rb',
        '.php',
        '.ts',
        '.swift',
    }

    def __init__(self):
        super().__init__()
        self.client = genai.Client(api_key=os.getenv('CODEFOX_API_KEY'))

    def check_connection(self) -> bool:
        try:
            self.client.models.list()
            return True
        except Exception as e:
            print(f'[red]Failed to connect to Gemini API: {e}[/red]')
            return False

    def upload_files(self, path_files: str) -> tuple:
        super().upload_files(path_files)

        ignored_paths = Helper.read_codefoxignore()

        try:
            store = self.client.file_search_stores.create(
                config={'display_name': 'CodeFox File Store'}
            )
        except Exception as e:
            return False, f"Error creating file search store: {e}"

        all_files_to_upload = []
        for root, _, files in os.walk(path_files):
            if any(
                ignored in root
                for ignored in [
                    '.git',
                    '__pycache__',
                    'node_modules',
                ] + ignored_paths
            ):
                continue

            for filename in files:
                ext = os.path.splitext(filename)[1].lower()
                if ext in self.SUPPORTED_EXTENSIONS:
                    all_files_to_upload.append(os.path.join(root, filename))

        valid_files = [
            f for f in all_files_to_upload
            if not any(ignored in f for ignored in ignored_paths)
        ]

        operations = self._upload_thead_pool_files(store, valid_files)
        if not operations:
            return True, store

        print(
            '[yellow]Waiting for Gemini API '
            'to process uploaded files...[/yellow]'
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

            while True:
                operations = [
                    self.client.operations.get(op)
                    for op in operations
                ]

                done_count = sum(1 if op.done else 0 for op in operations)
                progress.update(task, completed=done_count)

                if done_count:
                    break

                time.sleep(2)

        return True, store

    def remove_files(self, store):
        try:
            self.client.file_search_stores.delete(
                name=store.name,
                config=types.DeleteFileSearchStoreConfig(
                    force=True
                )
            )
            print(
                '[green]Successfully removed'
                f'file search store: {store.name}[/green]'
            )
        except Exception as e:
            print(
                '[red]Error removing '
                f'file search store {store.name}: {e}[/red]'
            )

    def execute(self, store, diff_text=""):
        super().execute()

        system_prompt = PromtTemplate(self.config)
        content = (
            "Analyze the following git diff"
            f"and identify potential risks:\n\n{diff_text}"
        )

        return self.client.models.generate_content(
            model=self.model_config['name'],
            contents=content,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt.get(),
                temperature=self.model_config['temperature'],
                max_output_tokens=self.model_config['max_tokens'],
                tools=[
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[store.name]
                        )
                    )
                ]
            )
        )

    def _upload_thead_pool_files(
            self,
            store: types.FileSearchStore,
            valid_files: list = []
    ) -> list:
        """
        Upload many files to Gemini store
        """
        operations = []
        with Progress() as progress:
            task = progress.add_task(
                '[bold cyan]Uploading codebase...[/]',
                total=len(valid_files)
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
                            f'[red]Error uploading {failed_file}: {exc}[/red]'
                        )
                    else:
                        operations.append(upload_op)

                    progress.advance(task)

        return operations

    def _upload_single_file(
            self,
            file_path: str,
            store: types.FileSearchStore
    ) -> tuple:
        """
        Upload single file to gemini store
        """
        try:
            file_stores = self.client.file_search_stores

            upload_op = file_stores.upload_to_file_search_store(
                file_search_store_name=store.name,
                file=file_path,
                config={'mime_type': 'text/plain'}
            )
            return upload_op, None
        except Exception as e:
            return None, (file_path, e)
