import os

from rich import print
from rich.markup import escape

from codefox.api.base_api import BaseAPI
from codefox.utils.helper import Helper


class Scan:
    def __init__(self, model: type[BaseAPI]):
        self.model = model()

    def execute(self):
        diff_text = Helper.get_diff()
        if not diff_text:
            print(
                "[yellow]Repository is not found or not have change[/yellow]"
            )
            return

        if not self.model.check_connection():
            print("[red]Failed to connect to model[/red]")
            return

        name = self.model.model_config["name"]
        if not self.model.check_model(name):
            available_models = "\n".join(self.model.get_tag_models())

            print(f"[red]Model '{name}' not found.")
            print(f"Available models:\n{available_models}")
            return

        if not diff_text.strip():
            print(
                "[yellow]No changes to analyze."
                "Make changes and run scan again.[/yellow]"
            )
            return

        is_upload, error = self.model.upload_files(os.getcwd())
        if not is_upload:
            print(
                "[red]Failed to upload files to model: "
                + escape(str(error))
                + "[/red]"
            )
            return

        print("[yellow]Waiting for model response...[/yellow]")
        try:
            response = self.model.execute(diff_text)
            print(f"[green]Scan result from model:[/green]\n{response.text}")
        except Exception as e:
            err_str = str(e)
            print("[red]Failed scan: " + escape(err_str) + "[/red]")

        self.model.remove_files()
