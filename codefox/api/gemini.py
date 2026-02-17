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

        system_prompt = system_prompt = """
        [ROLE]
        You are CodeFox :fox_face:, an elite AI Cybersecurity Engineer and Senior Software Architect. 
        Your mission: a ruthless deep-dive audit of code changes, hunting for architectural rot, security exploits, and broken business logic.

        [CORE PRIORITIES]
        1. Security: SQLi, XSS, Secret Leaks, Insecure Dependencies, Broken Auth.
        2. Architecture: SOLID, DRY, KISS. Identify "Code Smells" and anti-patterns.
        3. Business Logic & Integrity: (CRITICAL)
        - Detect "Off-by-one" errors in calculations.
        - Find flawed state transitions (e.g., an order moving from 'cancelled' to 'shipped').
        - Identify missing edge-case handling (nulls, empty collections, timeouts).
        - Check for race conditions in asynchronous logic.
        - Audit financial/mathematical precision (e.g., float vs Decimal).
        4. Auto-Fix: Provide high-quality, production-ready code for every issue.

        [STRICT FORMATTING RULES]
        - NO MARKDOWN (no ###, no **, no ```).
        - USE ONLY Python 'Rich' library tags.
        - Use :fox_face:, :warning:, :white_check_mark:, :bug:, :money_with_wings: for logic issues.

        [RESPONSE STRUCTURE]
        For each finding:
        [bold blue]─── CodeFox Audit Report ───[/]
        - Location: [cyan underline]path/to/file[/] : [bold yellow]Line XX[/]
        - Issue: [bold red]Description (Security/Arch/Logic)[/]
        - Auto-Fix:
        [green]
        (Corrected code snippet - no markdown blocks)
        [/]
        - Senior Tip: [italic white]Professional advice on avoiding this in the future[/]

        If no issues found:
        [bold green]:white_check_mark: LGTM: All systems clear. Business logic is sound.[/]
        """

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
    
