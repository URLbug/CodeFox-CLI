from pathlib import Path

from dotenv import load_dotenv
from rich import print

from codefox.scan import Scan
from codefox.init import Init
from codefox.utils.helper import Helper
from codefox.api.model_enum import ModelEnum


class CLIManager:
    def __init__(self, command, args=None):
        self.command = command
        self.args = args

        path_env = Path(".codefoxenv")
        if not load_dotenv(path_env) and command not in [
            "init",
            "version",
        ]:
            raise FileNotFoundError(
                "Failed to load .codefoxenv file."
                "Please ensure it exists and is properly formatted."
            )

    def _get_api_class(self):
        config = Helper.read_yml(".codefox.yml")
        provider = config.get("provider", "gemini")
        return ModelEnum.by_name(provider).api_class

    def run(self):
        if self.command == "version":
            print("[green]CodeFox CLI version Alpha 0.2v[/green]")
            return

        if self.command == "scan":
            api_class = self._get_api_class()
            scan = Scan(api_class)
            scan.execute()
            return

        if self.command == "init":
            init = Init()
            init.execute()
            return

        print(f"[red]Unknown command: {self.command}[/red]")
        print('[yellow]Please use flag "--help"', "to see available commands[/yellow]")
