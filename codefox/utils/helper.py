import yaml

from pathlib import Path


class Helper:
    @staticmethod
    def read_yml(path: str) -> dict:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f'Not found file with {path}')

        with open(path, 'r') as file:
            config_data = yaml.safe_load(file)

        return config_data

    @staticmethod
    def read_codefoxignore() -> list[str]:
        ignore = Path('.codefoxignore')
        if not ignore.exists():
            return []

        ignored_paths = []
        with open(ignore, 'r') as ignore_file:
            ignored_paths = [
                line.strip()
                for line in ignore_file
                if line.strip() and not line.startswith('#')
            ]

        return ignored_paths
