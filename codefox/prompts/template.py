import abc


class Template(abc.ABC):
    @abc.abstractmethod
    def get(self) -> str:
        pass
