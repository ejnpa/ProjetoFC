import os
from abc import abstractmethod
from azure.storage.blob import BlobServiceClient
from .strategy import StorageStrategy

class AzureStorage(StorageStrategy):
    def __init__(self):
        connection_string = os.getenv("STORAGE_STORAGE_CONNECTION_STRING", "UseDevelopmentStorage=true")
        self.container_name =  "notes"
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        try:
            self.container_client = self.blob_service_client.create_container(self.container_name)
        except Exception:
            self.container_client = self.blob_service_client.get_container_client(self.container_name) 
            
              
    def upload_files_to_storage(self, data: bytes, filename: str) -> str:
        blob_client = self.container_client.get_blob_client(blob=filename) 
        blob_client.upload_blob(data, overwrite=True)
        return blob_client.url
    
    def download_files_from_storage(self, filename: str) -> bytes:
        blob_client = self.container_client.get_blob_client(blob=filename)
        return blob_client.download_blob().readall()
    
    def delete_file_from_storage(self, filename: str):
        blob_client = self.container_client.get_blob_client(blob=filename)
        blob_client.delete_blob(delete_snapshots="include")   