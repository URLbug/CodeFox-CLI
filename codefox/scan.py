import os

from rich import print

from codefox.utils.helper import Helper
from codefox.api.gemini import Gemini


class Scan:
    def __init__(self):
        self.gemini = Gemini()

    def execute(self):
        diff_text = Helper.get_diff()
        if not diff_text:
            print("[yellow]Repository is not found[/yellow]")
            return

        if not self.gemini.check_connection():
            print("[red]Failed to connect to Gemini API[/red]")
            return

        name = self.gemini.model_config["name"]
        if not self.gemini.check_model(name):
            available_models = "\n".join(self.gemini.get_tag_models())

            print(f"[red]Model '{name}' not found.")
            print(f"Available models:\n{available_models}")
            return

        if not diff_text.strip():
            print(
                "[yellow]No changes to analyze."
                "Make changes and run scan again.[/yellow]"
            )
            return

        isUpload, store = self.gemini.upload_files(os.getcwd())
        if not isUpload:
            print(f"[red]Failed to upload files to Gemini API: {store}[/red]")
            return

        print("[yellow]Waiting for Gemini API response...[/yellow]")
        try:
            response = self.gemini.execute(store, diff_text)
            print(f"[green]Scan result from Gemini API:[/green]\n{response.text}")
        except Exception as e:
            print(f"[red]Failed scan: {e}[/red]")

        self.gemini.remove_files(store)
