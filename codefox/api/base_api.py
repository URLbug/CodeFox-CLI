import abc

@abc.abstractmethod
class BaseAPI(abc.ABC):
    @abc.abstractmethod
    def execute(self):
        pass