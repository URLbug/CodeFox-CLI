import os
import git

from rich import print

from codefox.api.gemini import Gemini


class Scan:
    def __init__(self):
        self.gemini = Gemini()

    def execute(self):
        repo = git.Repo('.')
        t = repo.head.commit.tree
        diff_text = repo.git.diff(t)

        if not diff_text.strip():
            print('[yellow]No changes detected in the current commit. Scanning entire codebase.[/yellow]')
            return
        
        isUpload, store = self.gemini.upload_files(os.getcwd())
        if not isUpload:
            print(f'[red]Failed to upload files to Gemini API: {store}[/red]')
            return

        print('[yellow]Waiting for Gemini API response...[/yellow]')
        response = self.gemini.execute(store, diff_text)
        print(f'[green]Scan result from Gemini API:[/green]\n{response.text}')

        self.gemini.remove_files(store)
