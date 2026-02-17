import os
import time

from google import genai
from google.genai import types
from rich import print
from rich.progress import Progress
from concurrent.futures import ThreadPoolExecutor, as_completed

from codefox.api.base_api import BaseAPI



class Gemini(BaseAPI):
    SUPPORTED_EXTENSIONS = {'.py', '.js', '.java', '.cpp', '.c', '.cs', '.go', '.rb', '.php', '.ts', '.swift'}
    MAX_WORKERS = 10 

    def __init__(self):
        super().__init__()
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def check_connection(self):
        try:
            self.client.models.list()
            return True
        except Exception as e:
            print(f'[red]Failed to connect to Gemini API: {e}[/red]')
            return False
    
    def upload_files(self, root_directory):
        ignored_paths = super().upload_files(None)

        try:
            store = self.client.file_search_stores.create(
                config={'display_name': 'CodeFox File Store'}
            )
        except Exception as e:
            return False, f"Error creating file search store: {e}"

        all_files_to_upload = []
        for root, dirs, files in os.walk(root_directory):
            if any(ignored in root for ignored in ['.git', '__pycache__', 'node_modules'] + ignored_paths):
                continue

            for filename in files:
                ext = os.path.splitext(filename)[1].lower()
                if ext in self.SUPPORTED_EXTENSIONS:
                    all_files_to_upload.append(os.path.join(root, filename))


        valid_files = [
            f for f in all_files_to_upload 
            if not any(ignored in f for ignored in ignored_paths)
        ]

        operations = []

        with Progress() as progress:
            task = progress.add_task("[bold cyan]Uploading codebase...[/]", total=len(valid_files))
            
            with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
                futures = {executor.submit(self.__upload_single_file, f, store): f for f in valid_files}
                
                for future in as_completed(futures):
                    upload_op, error = future.result()
                    
                    if error:
                        failed_file, exc = error
                        print(f'[red]Error uploading {failed_file}: {exc}[/red]')
                    else:
                        operations.append(upload_op)
                        
                    progress.advance(task)
        
        print(f'[yellow]Waiting for Gemini API to process uploaded files...[/yellow]')
        while all(op.done for op in operations):
            time.sleep(2)

        return True, store
            
    def __upload_single_file(self, file_path, store):
        try:
            upload_op = self.client.file_search_stores.upload_to_file_search_store(
                file_search_store_name=store.name,
                file=file_path,
                config={'mime_type': 'text/plain'}
            )
            return upload_op, None
        except Exception as e:
            return None, (file_path, e)

    def remove_files(self, store):
        try:
            self.client.file_search_stores.delete(name=store.name, config=types.DeleteFileSearchStoreConfig(force=True))
            print(f'[green]Successfully removed file search store: {store.name}[/green]')
        except Exception as e:
            print(f'[red]Error removing file search store {store.name}: {e}[/red]')
    
    def execute(self, store, diff_text=""):
        super().execute()

        path_instruction = os.path.join(os.path.dirname(__file__), '..', 'instruction.txt')
        with open(path_instruction, 'r') as f:
            system_prompt = f.read()

        content = f"Analyze the following git diff and identify potential risks:\n\n{diff_text}"        
        
        return self.client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=content,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.2,
                tools=[
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[store.name]
                        )
                    )
                ]
            )
        )
    
