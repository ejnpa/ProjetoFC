
import mimetypes
from azure.storage.blob import BlobServiceClient, ContentSettings
from .IStorage import StorageInterface
from config import settings
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError


class AzureStorage(StorageInterface):
    def __init__(self):
        
        self.blob_service_client = BlobServiceClient.from_connection_string(
            settings.storage_connection_string,
            api_version="2023-11-03"
        )
        
        
        self.docs_container="documentos"
        self.thumbnail_container="thumbnails"
        self.audio_cache_container = "generated-audio"
        
        self._init_container(self.docs_container, public_access ="blob")
        self._init_container(self.thumbnail_container, public_access = "blob")
        self._init_container(self.audio_cache_container)
        
        
    def _init_container(self, container_name: str, public_access: str | None = None,) -> None:
        """Função auxiliar para garantir que o contentor existe e é público"""

        container_client = self.blob_service_client.get_container_client(container_name)
        
        try:
            container_client.create_container(public_access = public_access)  
        except ResourceExistsError:
            pass
        
    def _get_target_container(self, filename: str) -> str:      
        """Lógica de roteamento: se começar por 'thumb_', vai para as miniaturas."""
        if filename.startswith("thumb_"):
            return self.thumbnail_container
        return self.docs_container    
              
    def upload_files_to_storage(self, data: bytes, filename: str) -> str:
        
        container = self._get_target_container(filename)
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
        container = self._get_target_container(filename)
        container_client = self.blob_service_client.get_container_client(container)
        blob_client = container_client.get_blob_client(blob=filename)
        return blob_client.download_blob().readall()

    def delete_file_from_storage(self, filename: str):
        try:
            container = self._get_target_container(filename)
            container_client = self.blob_service_client.get_container_client(container)
            blob_client = container_client.get_blob_client(blob=filename)
            blob_client.delete_blob(delete_snapshots="include")
        except Exception as e:
            print(f"Aviso do Storage: O ficheiro '{filename}' já não existe no Azurite. Ignorado.")
            
    def get_cached_audio(self, blob_name: str) -> bytes | None:
        client = self.blob_service_client.get_container_client(
            self.audio_cache_container
        ).get_blob_client(blob_name)
        
        try:
            return client.download_blob().readall()
        except ResourceNotFoundError:
            return None
        
    def save_cached_audio(self, blob_name: str, data: bytes) -> None:
        client = self.blob_service_client.get_container_client(
            self.audio_cache_container
        ).get_blob_client(blob_name)
        
        client.upload_blob(
            data,
            overwrite = True,
            content_settings = ContentSettings(content_type="audio/mpeg")
            
        )
            
    def delete_cached_audio(self, blob_name: str) -> None:
        client = self.blob_service_client.get_container_client(
            self.audio_cache_container
        ).get_blob_client(blob_name)
        
        try:
            client.delete_blob()
        except ResourceNotFoundError:
            pass       