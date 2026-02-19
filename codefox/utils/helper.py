import git
import os
import yaml

from pathlib import Path


class Helper:
    SUPPORTED_EXTENSIONS = {
        ".py",
        ".js",
        ".java",
        ".cpp",
        ".c",
        ".cs",
        ".go",
        ".rb",
        ".php",
        ".ts",
        ".swift",
    }

    @staticmethod
    def read_yml(path: str) -> dict:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Not found file with {path}")

        with open(path, "r", encoding="utf-8") as file:
            config_data = yaml.safe_load(file)

        return config_data

    @staticmethod
    def read_codefoxignore() -> list[str]:
        ignore = Path(".codefoxignore")
        if not ignore.exists():
            return []

        ignored_paths = []
        with open(ignore, "r", encoding="utf-8") as ignore_file:
            ignored_paths = [
                line.strip()
                for line in ignore_file
                if line.strip() and not line.startswith("#")
            ]

        return ignored_paths

    @staticmethod
    def get_all_files(path_files: str) -> list:
        ignored_paths = Helper.read_codefoxignore()

        all_files_to_upload = []
        for root, _, files in os.walk(path_files):
            skip_dirs = [".git", "__pycache__", "node_modules"]
            if os.path.basename(root) in skip_dirs or any(
                ignored in root for ignored in ignored_paths
            ):
                continue

            for filename in files:
                ext = os.path.splitext(filename)[1].lower()
                if ext in Helper.SUPPORTED_EXTENSIONS:
                    all_files_to_upload.append(os.path.join(root, filename))

        return all_files_to_upload

    @staticmethod
    def get_diff() -> str | None:
        try:
            repo = git.Repo(".")
            diff_text = repo.git.diff(repo.head.commit)
            return diff_text
        except git.exc.InvalidGitRepositoryError:
            return None
