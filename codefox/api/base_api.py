import abc

@abc.abstractmethod
class BaseAPI(abc.ABC):
    @abc.abstractmethod
    def execute(self):
        pass

    @abc.abstractmethod
    def check_connection(self):
        pass
    
    @abc.abstractmethod
    def upload_files(self, files):
        with open('.codefoxignore', 'r') as ignore_file:
            ignored_paths = [line.strip() for line in ignore_file if line.strip() and not line.startswith('#')]
        
        return ignored_paths
    


