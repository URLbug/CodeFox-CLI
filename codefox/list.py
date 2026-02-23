from rich import print
from rich.table import Table

from codefox.api.base_api import BaseAPI
from codefox.base_cli import BaseCLI


class List(BaseCLI):
    def __init__(self, model: type[BaseAPI]):
        self.model = model()

    def execute(self) -> None:
        is_connect, error = self.model.check_connection()
        if not is_connect:
            print(f"[red]Failed to connect to mode: {error}[/red]")
            return

        try:
            models = self.model.get_tag_models()

            if not models:
                print("[yellow]No models available[/yellow]")
                return

            table = Table()

            table.add_column("#", style="dim", width=4, justify="right")
            table.add_column("Model name", style="cyan")

            for i, model_name in enumerate(models, start=1):
                table.add_row(str(i), model_name)

            print(table)
        except Exception as e:
            print(f"[red]Failed get models from provider: {e}[/red]")
