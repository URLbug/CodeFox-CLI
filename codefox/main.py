#!/usr/bin/env python3
import typer

from codefox.cli_manager import CLIManager

def main(
        command: str = typer.Option(help="The command to execute."),
        args: str = typer.Option(None, help="Arguments for the command.")
):
    """
    Welcome to CodeFox CLI! This tool allows you to interact with various AI models and perform different tasks. 
    
    To get started, use the following commands:
    
    - [bold cyan]init[/bold cyan]: Initializes the CodeFox CLI environment.
    
    - [bold cyan]scan[/bold cyan]: Executes a scan using the Gemini API to generate content based on a prompt.

    - [bold cyan]version[/bold cyan]: Displays the current version of CodeFox CLI.
    """
    manager = CLIManager(command=command, args=args)
    manager.run()

def cli():
    """Entry point wrapper used by the console script."""
    typer.run(main)


if __name__ == "__main__":
    cli()