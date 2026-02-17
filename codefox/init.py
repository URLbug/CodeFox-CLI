import os

from dotenv import load_dotenv
from rich import print
from rich.prompt import Confirm

from codefox.api.gemini import Gemini


class Init:
    def __init__(self):
        pass

    def execute(self):
        api_key = input('Enter your Gemini API Key: ').strip()
        if len(api_key) < 30:
             print('[red]Invalid API key format. Please check your Gemini API Key.[/red]')
             return

        self.setup_config(api_key)
        
        print('[yellow]Check connection to Gemini API...[/yellow]')
        gemini = Gemini()
        if not gemini.check_connection():
            print('[red]Failed to connect to Gemini API. Please check your API key and network connection.[/red]')
            return

        print('[green]CodeFox CLI initialized successfully![/green]')
    
    def setup_config(self, api_key):
        path_env = os.path.join(os.path.dirname(__file__), '..', '.env')
        
        should_write_env = True
        if os.path.exists(path_env):
            should_write_env = Confirm.ask("[yellow].env file already exists. Overwrite API key?[/yellow]")

        if should_write_env:
            try:
                print('[yellow]Saving API key to .env file...[/yellow]')
                with open(path_env, 'w', encoding='utf-8') as env_file:
                    env_file.write(f'GEMINI_API_KEY={api_key}\n')
                print('[green]API key saved successfully![/green]')
            except Exception as e:
                print(f'[red]Error writing API key to .env file: {e}[/red]')
        else:
            print('[blue]Skipping .env update.[/blue]')

        path_ignore = '.codefoxignore'
        if not os.path.exists(path_ignore):
            try:
                print('[yellow]Creating .codefoxignore file...[/yellow]')
                default_ignore = "node_modules/\nvendor/\n.git/\n__pycache__/\n.env\n"
                with open(path_ignore, 'w', encoding='utf-8') as ignore_file:
                    ignore_file.write(default_ignore)
            except Exception as e:
                print(f'[red]Error creating .codefoxignore file: {e}[/red]')
        else:
            print('[blue].codefoxignore already exists, skipping...[/blue]')
        
        if not load_dotenv(path_env):
            print('[red]Failed to load .env file. Please ensure it exists and is properly formatted.[/red]')
            return
        