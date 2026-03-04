#!/usr/bin/env python3
import typer

from codefox.cli_manager import CLIManager


def main(
    command: str = typer.Argument(
        ..., help="The command to execute (e.g., scan, init)."
    ),
    args: str = typer.Argument(
        None, help="Additional arguments for the command."
    ),
):
    """CodeFox CLI — automated code review with Gemini, Ollama, and OpenRouter.

    Commands:

    - [bold cyan]init[/bold cyan]:
    Set up the environment (provider, API key, .codefoxignore, .codefox.yml).

    - [bold cyan]scan[/bold cyan]:
    Run review on the current git diff using the configured model.

    - [bold cyan]list[/bold cyan]:
    List available models for the current provider.

    - [bold cyan]version[/bold cyan]: Show CodeFox CLI version.
    """

    manager = CLIManager(command=command, args=args)
    manager.run()


def cli():
    """Entry point wrapper used by the console script."""
    typer.run(main)


if __name__ == "__main__":
    cli()
