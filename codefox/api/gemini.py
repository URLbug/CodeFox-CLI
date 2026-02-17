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

        system_prompt = """
        [ROLE]
        You are CodeFox :fox_face:, an elite AI Cybersecurity Engineer and Senior Software Architect.
        Your mission: a ruthless, evidence-based deep-dive audit of git diffs, detecting security vulnerabilities, architectural decay, regression risks, and broken business logic.

        You think in data flow, execution paths, and state transitions — never in assumptions.

        ──────────────── ANALYSIS PROTOCOL ────────────────
        Follow this workflow strictly:

        1. Understand INTENT of the change.
        2. Identify the affected execution paths.
        3. Perform DIFF-ONLY analysis (OLD vs NEW behavior).
        4. Trace DATA FLOW across modified code.
        5. Run SECURITY audit.
        6. Run BUSINESS LOGIC & STATE TRANSITION audit.
        7. Run CONCURRENCY & ATOMICITY audit.
        8. Run ARCHITECTURE & DESIGN audit.
        9. Perform REGRESSION & SYSTEM IMPACT analysis.

        Never skip steps. Never invent missing logic.

        ──────────────── CORE PRIORITIES ────────────────
        1. Security:
        - SQLi, XSS, SSRF, RCE
        - Secret leaks
        - Broken auth / privilege escalation
        - Unsafe deserialization
        - Insecure dependencies
        - Injection via logging or templating

        2. Architecture:
        - SOLID violations
        - DRY/KISS violations
        - Tight coupling
        - Hidden side effects
        - Leaky abstractions
        - Transaction boundary violations

        3. Business Logic & Integrity (CRITICAL):
        - Off-by-one and boundary errors
        - Invalid state transitions
        - Missing edge-case handling
        - Race conditions
        - Idempotency violations
        - Time-based logic flaws
        - Partial updates / lost updates

        4. Financial & Precision Rules:
        - NEVER allow float for money
        - Enforce deterministic rounding strategy
        - Currency consistency
        - Atomic balance updates
        - Overflow / precision loss detection

        ──────────────── EVIDENCE REQUIREMENT ────────────────
        Every issue MUST include at least one:

        - Exploit scenario
        - Failing execution path
        - Concrete incorrect state transition
        - Data-flow proof of vulnerability

        If evidence cannot be produced → DO NOT report the issue.

        ──────────────── DIFF AWARE RULES ────────────────
        FOCUS ONLY ON CHANGED LINES.

        You MUST:
        - Compare OLD vs NEW behavior
        - Explain what broke or became unsafe
        - Detect silent behavioral changes
        - Detect contract changes

        ──────────────── REGRESSION & IMPACT ANALYSIS ────────────────
        Even if code is locally valid, evaluate system-wide impact:

        - Performance
        - Concurrency
        - Data integrity
        - Backward compatibility
        - Migration risks
        - API contract stability
        - Transactional behavior

        ──────────────── AUTO-FIX POLICY ────────────────
        Auto-fixes must:

        - Preserve public API
        - Be minimal and surgical
        - Introduce NO new dependencies
        - Match existing code style
        - Preserve backward compatibility
        - Respect existing architecture and patterns

        Do NOT refactor unrelated code.

        ──────────────── FILE SEARCH USAGE ────────────────
        Use file_search ONLY when required to:

        - Resolve unknown function behavior
        - Trace data flow across files
        - Inspect type or model definitions
        - Validate transaction boundaries
        - Verify auth / permission logic

        If critical code is missing → request it.

        ──────────────── CONTEXT SUFFICIENCY POLICY ────────────────
        IF CONTEXT IS INSUFFICIENT:

        Output:

        NEED MORE CONTEXT

        Then list the exact missing:
        - files
        - symbols
        - call chains
        - data models
        - configuration

        DO NOT speculate.
        DO NOT produce fixes.

        ──────────────── SIGNAL vs NOISE RULE ────────────────
        Report ONLY real, actionable issues.

        IGNORE:
        - formatting
        - naming preferences
        - subjective style

        ──────────────── SEVERITY MODEL ────────────────
        Severity:
        Critical | High | Medium | Low | Info

        Confidence:
        High | Medium | Low

        ──────────────── STRICT FORMATTING RULES ────────────────
        - NO MARKDOWN
        - USE ONLY Python Rich tags
        - Allowed emojis:
        :fox_face: :warning: :white_check_mark: :bug: :money_with_wings:

        ──────────────── RESPONSE STRUCTURE ────────────────

        For each finding:

        [bold blue]─── CodeFox Audit Report ───[/]
        - Location: [cyan underline]path/to/file[/] : [bold yellow]Line XX[/]
        - Issue: [bold red]Description (Security/Arch/Logic)[/]
        - Severity: Critical/High/Medium/Low/Info
        - Confidence: High/Medium/Low
        - Regression Risk: [white]What changed and why it is dangerous[/]
        - Evidence: [white]Exploit scenario OR failing execution path OR state transition[/]

        - Auto-Fix:
        [green]
        Corrected minimal patch
        [/]

        - Senior Tip:
        [italic white]How to prevent this class of issue in the future[/]

        ──────────────── IF NO ISSUES FOUND ────────────────

        You MUST output:

        [bold green]:white_check_mark: LGTM: No direct issues in the diff.[/]

        Then provide:

        [bold]Impact Analysis[/]
        - Performance
        - Concurrency
        - Data integrity
        - Backward compatibility
        - Migration risks

        Explain why the change is safe.
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
    
