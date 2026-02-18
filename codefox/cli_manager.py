from pathlib import Path

from dotenv import load_dotenv
from rich import print

from codefox.scan import Scan
from codefox.init import Init

from codefox.api.gemini import Gemini


class CLIManager:
    def __init__(self, command, args=None):
        self.command = command
        self.args = args

        path_env = Path('.codefoxenv')
        if not load_dotenv(path_env) and command not in ['init', 'version',]:
            raise FileExistsError(
                'Failed to load .env file.'
                'Please ensure it exists and is properly formatted.'
            )

    def run(self):
        if self.command == "version":
            print('[green]CodeFox CLI version Alpha 0.2v[/green]')
            return

        if self.command == "scan":
            scan = Scan()
            scan.execute()
            return

        if self.command == "init":
            init = Init(Gemini)
            init.execute()
            return

        print(f'[red]Unknown command: {self.command}[/red]')
        print(
            '[yellow]Please use flag "--help"',
            'to see available commands[/yellow]'
        )
