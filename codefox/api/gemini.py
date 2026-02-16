import os
import time

from google import genai
from google.genai import types
from rich import print
from rich.progress import track

from codefox.api.base_api import BaseAPI



class Gemini(BaseAPI):
    SUPPORTED_EXTENSIONS = {'.py', '.js', '.java', '.cpp', '.c', '.cs', '.go', '.rb', '.php', '.ts', '.swift'}

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

        store = self.client.file_search_stores.create(
            config={'display_name': 'CodeFox File Store'}
        )

        all_files_to_upload = []
        for root, dirs, files in os.walk(root_directory):
            if any(ignored in root for ignored in ['.git', '__pycache__', 'node_modules'] + ignored_paths):
                continue

            for filename in files:
                ext = os.path.splitext(filename)[1].lower()
                if ext in self.SUPPORTED_EXTENSIONS:
                    all_files_to_upload.append(os.path.join(root, filename))


        operations = []
        for file_path in track(all_files_to_upload, description="[bold cyan]Uploading codebase...[/]"):
            try:
                upload_op = self.client.file_search_stores.upload_to_file_search_store(
                    file_search_store_name=store.name,
                    file=file_path,
                    config={'mime_type': 'text/plain'}
                )

                operations.append(upload_op)
            except Exception as e:
                return False, f"Error uploading {file_path}: {e}"
        
        print(f'[yellow]Waiting for Gemini API to process uploaded files...[/yellow]')
        while all(op.done for op in operations):
            time.sleep(2)

        return True, store
            
    def execute(self, store, diff_text=""):
        super().execute()

        promt = f"""
        You are CodeFox, an elite AI Engineer specializing in code quality and cybersecurity. Your mission is to conduct a deep audit of the provided files, going far beyond the capabilities of standard linters.

        Core Priorities:
        1. Security: Identify vulnerabilities such as SQL injections, XSS, secret leaks, and insecure dependencies.
        2. Architectural Integrity: Enforce SOLID, DRY, and KISS principles, and identify appropriate design patterns.
        3. Business Logic: Detect potential bugs in calculations, state management, and edge-case handling.
        4. Auto-Fix: For every identified issue, you MUST provide a corrected code snippet.

        Output Style & Formatting:
        YOU MUST RESPOND EXCLUSIVELY USING PYTHON 'RICH' LIBRARY MARKUP TAGS. DO NOT USE STANDARD MARKDOWN (like ## or **) OR ANY OTHER FORMATTING STYLES.

        Formatting Rules:
        1. Headers: [bold magenta]HEADER TEXT[/]
        2. Errors/Issues: [bold red]Error description[/]
        3. Fixes/Solutions: [green]Fix description[/]
        4. File Paths: [cyan underline]path/to/file.ext[/]
        5. Emojis: Use :fox_face:, :warning:, :white_check_mark:, :bug: frequently.

        ### Response Structure:
        For each finding, use the following template:
        [bold blue]─── CodeFox Audit Report ───[/]
        - Location: [cyan underline]/path/to/file.ext[/] : [bold yellow]Line number[/]
        - Issue: [bold red]Description of the issue[/]
        - Auto-Fix ([language]): 
        [green]
        Corrected code snippet with line numbers and syntax highlighting (if applicable)[/]
        [/]
        - Senior Tip: [italic white]brief professional advice[/]

        If no issues are found, respond with:
        [bold green]:white_check_mark: LGTM: All systems clear. Code satisfies CodeFox standards.[/]

        Context:
        Git diff of the current commit: 
        {diff_text}
        """
        
        return self.client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=promt,
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[store.name]
                        )
                    )
                ]
            )
        )
    
