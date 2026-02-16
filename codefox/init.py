import os

from dotenv import load_dotenv
from rich import print

from codefox.api.gemini import Gemini


class Init:
    def __init__(self):
        pass

    def execute(self):
        api_key = input('Enter your Gemini API Key: ').strip()
        if len(api_key) < 30:
             print('[red]Invalid API key format. Please check your Gemini API Key.[/red]')
             return

        try:
            print('[yellow]Saving API key to .env file...[/yellow]')

            path_env = os.path.join(os.path.dirname(__file__), '..', '.env')
            with open(path_env, 'wb') as env_file:
                env_file.write(f'GEMINI_API_KEY={api_key}\n'.encode('utf-8'))
        except Exception as e:
            print(f'[red]Error writing API key to .env file: {e}[/red]')
            return
        
        try:
            print('[yellow]Creating .codefoxignore file...[/yellow]')
            with open('.codefoxignore', 'wb') as ignore_file:
                ignore_file.write(''.encode('utf-8'))
        except Exception as e:
            print(f'[red]Error creating .codefoxignore file: {e}[/red]')
            return
        
        if not load_dotenv(path_env):
            print('[red]Failed to load .env file. Please ensure it exists and is properly formatted.[/red]')
            return
        
        print('[yellow]Check connection to Gemini API...[/yellow]')
        gemini = Gemini()
        if not gemini.check_connection():
            print('[red]Failed to connect to Gemini API. Please check your API key and network connection.[/red]')
            return

        print('[green]CodeFox CLI initialized successfully![/green]')