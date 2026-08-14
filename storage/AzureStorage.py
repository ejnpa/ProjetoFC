import os
from azure.storage.blob import BlobServiceClient
from .IStorage import StorageInterface

class AzureStorage(StorageInterface):
    def __init__(self):
        
        ip_desktop="100.89.13.43"
        
        connection_string = f"DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://{ip_desktop}:10000/devstoreaccount1;"
        
        self.container_name =  "public-notes"
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string, api_version="2023-11-03")
        try:
            self.container_client = self.blob_service_client.create_container(self.container_name,
                                                                              public_access="blob")
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