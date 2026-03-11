import abc
from typing import Callable


class BaseTool(abc.ABC):
    @abc.abstractmethod
    def get_tool(self) -> Callable:
        pass
