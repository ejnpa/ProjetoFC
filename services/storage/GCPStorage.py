from .strategy import StorageStrategy

class GCPStorage(StorageStrategy):
    def __init__(self):
        # Initialize GCP storage client here
        pass

    def upload_files_to_storage(self, data: bytes, filename: str) -> str:
        # Implement GCP storage upload logic here
        pass

    def download_files_from_storage(self, filename: str) -> bytes:
        # Implement GCP storage download logic here
        pass

    def delete_file_from_storage(self, filename: str):
        # Implement GCP storage delete logic here
        pass