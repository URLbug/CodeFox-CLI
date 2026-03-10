import shutil
from pathlib import Path
from typing import Any

from codefox.utils.local_rag import LocalRAG
from codefox.api.base_api import BaseAPI
from codefox.base_cli import BaseCLI


class Clean(BaseCLI):
    def __init__(self, model: type[BaseAPI], args: dict[str, Any] | None = None):
        self.model = model()
        self.args = args

    def execute(self) -> None:
        cache_dir = self._get_dir_cache()
        if not cache_dir or not cache_dir.exists():
            print("Sorry but not found cache dir")
            return
        
        if not cache_dir.is_dir():
            print("Sorry but current path is not dir")
            return
        
        if cache_dir in [Path("/"), Path.home()]:
            raise ValueError("Refusing to delete dangerous directory")
        
        try:
            shutil.rmtree(cache_dir)
            print(f"Cache directory removed: {cache_dir}")
        except Exception as e:
            print(f"Failed to remove cache dir: {e}")

        return
    
    def _get_dir_cache(self) -> Path | None:
        type_cache = self.args.get("typeCache")
        if type_cache == "embedding":
            return Path(
                self._get_embedding_cache()
            )
        elif type_cache == "rag":
            return Path(
                self._get_rag_index_dir()
            )
        return None

    def _get_embedding_cache(self) -> str:
        return LocalRAG.default_cache_dir

    def _get_rag_index_dir(self) -> str:
        configured_path = self.model.model_config.get(                                                                                                    
            "rag_index_dir", LocalRAG.default_index_dir                                                                                                   
        )                                                              
                                                                                   
        allowed_root = Path(LocalRAG.default_index_dir).resolve()                                                                                         
        target_path = Path(configured_path).resolve()                                                                                                     
        if not str(target_path).startswith(str(allowed_root)):                                                                                            
            raise ValueError("Configured rag_index_dir is outside the allowed cache directory")
                                                      
        return str(target_path)
