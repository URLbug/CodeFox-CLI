from dotenv import load_dotenv
from rich import print

from codefox.scan import Scan
from codefox.init import Init


class CLIManager:
    def __init__(self, command, args=None):
        self.command = command
        self.args = args

        if not load_dotenv('.env'):
            raise FileExistsError('Failed to load .env file. Please ensure it exists and is properly formatted.')

    def run(self):
        if self.command == "scan":
            scan = Scan()
            scan.execute()
            return
        
        if self.command == "init":
            init = Init()
            init.execute()
            return
        
        print(f'[red]Unknown command: {self.command}[/red]')
        print(f'[yellow]Please use flag "--help" to see available commands[/yellow]')
