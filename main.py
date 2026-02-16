import typer

from rich import print

from codefox.cli_manager import CLIManager

def main(
        command: str = typer.Option(help="The command to execute."),
        args: str = typer.Option(help="Arguments for the command.")
):
    """Entry point for the CodeFox CLI application."""
    manager = CLIManager(command=command, args=args)
    manager.run()

if __name__ == "__main__":
   typer.run(main)