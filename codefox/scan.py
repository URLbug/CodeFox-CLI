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

        if not self.gemini.check_connection():
            return

        name = self.gemini.model_config["name"]
        if not self.gemini.check_model(name):
            available_models = "\n".join(self.gemini.get_tag_models())

            print(f"[red]Model '{name}' not found.")
            print(f"Available models:\n{available_models}")
            return

        if not diff_text.strip():
            print(
                '[yellow]No changes detected in the current commit.'
                'Scanning entire codebase.[/yellow]'
            )
            return

        isUpload, store = self.gemini.upload_files(os.getcwd())
        if not isUpload:
            print(f'[red]Failed to upload files to Gemini API: {store}[/red]')
            return

        print('[yellow]Waiting for Gemini API response...[/yellow]')
        try:
            response = self.gemini.execute(store, diff_text)
            print(f'[green]Scan result from Gemini API:[/green]\n{response.text}')
        except Exception as e:
            print(
                f"[red]Failed scan: {e}[/red]"
            )

        self.gemini.remove_files(store)
