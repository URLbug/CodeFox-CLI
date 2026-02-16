import abc

@abc.abstractmethod
class BaseAPI(abc.ABC):
    @abc.abstractmethod
    def execute(self):
        pass

    @abc.abstractmethod
    def check_connection(self):
        pass