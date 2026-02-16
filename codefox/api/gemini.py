import os

from codefox.api.base_api import BaseAPI

from google import genai
from google.genai import types


class Gemini(BaseAPI):
    def __init__(self):
        super().__init__()
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def check_connection(self):
        try:
            self.client.models.list()
            return True
        except Exception as e:
            print(f'[red]Failed to connect to Gemini API: {e}[/red]')
            return False

    def execute(self):
        super().execute()
        
        return self.client.models.generate_content(
            model="gemini-3-flash-preview",
            contents="Скажи мне анекдот про программистов",
        )
    
