
import mimetypes
from azure.storage.blob import BlobServiceClient, ContentSettings
from .IStorage import StorageInterface
from config import settings

class AzureStorage(StorageInterface):
    def __init__(self):
        
        self.blob_service_client = BlobServiceClient.from_connection_string(
            settings.storage_connection_string,
            api_version="2023-11-03"
        )
        
        self.docs_container="documentos"
        self.thumbnail_container="thumbnails"
        
        self.init_container(self.docs_container)
        self.init_container(self.thumbnail_container)
        
    def init_container(self, container_name: str):
        """Função auxiliar para garantir que o contentor existe e é público"""
        try:
            self.blob_service_client.create_container(container_name, public_access="blob")   
        except Exception:
            pass
        
    def get_target_container(self, filename: str) -> str:      
        """Lógica de roteamento: se começar por 'thumb_', vai para as miniaturas."""
        if filename.startswith("thumb_"):
            return self.thumbnail_container
        return self.docs_container    
              
    def upload_files_to_storage(self, data: bytes, filename: str) -> str:
        
        container = self.get_target_container(filename)
        container_client = self.blob_service_client.get_container_client(container)
        
        blob_client = container_client.get_blob_client(blob=filename) 
        
        mime_guess = mimetypes.guess_type(filename)
        
        content_type = mime_guess[0] if mime_guess and mime_guess[0] else "application/octet-stream"
            
        settings = ContentSettings(
            content_type=content_type,
            content_disposition="inline"
        )
        
        blob_client.upload_blob(data, overwrite=True, content_settings=settings)
        return blob_client.url
    
    
    def download_files_from_storage(self, filename: str) -> bytes:
        container = self.get_target_container(filename)
        container_client = self.blob_service_client.get_container_client(container)
        blob_client = container_client.get_blob_client(blob=filename)
        return blob_client.download_blob().readall()
    
    
    
    
    def delete_file_from_storage(self, filename: str):
        try:
            container = self.get_target_container(filename)
            container_client = self.blob_service_client.get_container_client(container)
            blob_client = container_client.get_blob_client(blob=filename)
            blob_client.delete_blob(delete_snapshots="include")
        except Exception as e:
            print(f"Aviso do Storage: O ficheiro '{filename}' já não existe no Azurite. Ignorado.")