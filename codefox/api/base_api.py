import abc

from codefox.utils.helper import Helper


class BaseAPI(abc.ABC):
    def __init__(self, config: dict = None):
        super().__init__()
        try:
            self.config = config or Helper.read_yml('.codefox.yml')
        except FileNotFoundError:
            raise RuntimeError(
                "Configuration file '.codefox.yml' not found. "
                "Please run 'codefox --command init' first."
            )

        if 'model' not in self.config or not self.config.get('model'):
            raise ValueError(
                "Missing required key 'model'"
            )

        self.model_config = self.config['model']
        if (
            'name' not in self.model_config or
            not self.model_config.get('name')
        ):
            raise ValueError(
                "Key 'model' missing required value key 'name'"
            )

        if 'max_tokens' not in self.model_config:
            self.model_config['max_tokens'] = None

        if 'temperature' not in self.model_config:
            self.model_config['temperature'] = 0.2

    @abc.abstractmethod
    def check_model(self, name: str) -> bool:
        pass

    @abc.abstractmethod
    def execute(self) -> str:
        pass

    @abc.abstractmethod
    def check_connection(self) -> bool:
        pass

    @abc.abstractmethod
    def upload_files(self, path_files: str) -> tuple:
        pass
