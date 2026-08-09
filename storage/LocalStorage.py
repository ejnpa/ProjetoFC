import os 
from .IStorage import StorageInterface

class LocalStorage(StorageInterface):
    def __init__(self):
        self.upload_dir = "LOCAL_UPLOADS"
        os.makedirs(self.upload_dir, exist_ok=True)
        
    def upload_files_to_storage(self, data: bytes, filename: str) -> str:
        file_path = os.path.join(self.upload_dir, filename)
        with open(file_path, "wb") as f:
            f.write(data)
        return f"/local_storage/{filename}"
    
    def download_files_from_storage(self, filename: str) -> bytes:
        file_path = os.path.join(self.upload_dir, filename)
        with open(file_path, "rb") as f:    
            return f.read()
        
    def delete_file_from_storage(self, filename: str):
        file_path = os.path.join(self.upload_dir, filename)
        if os.path.exists(file_path):
            os.remove(file_path)