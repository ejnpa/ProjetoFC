import os
from ABC import abstractmethod

class StorageInterface(ABC):
    @abstractmethod
    def upload_files_to_storage(self, data: bytes, filename: str) -> str:
        pass
    
    @abstractmethod
    def download_files_from_storage(self, filename: str) -> bytes:
        pass
    
    @abstractmethod
    def delete_file_from_storage(self, filename: str):
        pass