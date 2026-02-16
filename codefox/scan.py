from codefox.api.gemini import Gemini

class Scan:
    def __init__(self):
        self.gemini = Gemini()

    def execute(self):
        response = self.gemini.execute()
        print(response.text)


        # (Опционально) Удаляем хранилище после работы
        # client.file_search_stores.delete(name=store.name)z