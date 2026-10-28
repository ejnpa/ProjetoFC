import mimetypes
import os
from google.api_core.exceptions import NotFound
from google.cloud import storage
from .IStorage import StorageInterface

class GCPStorage(StorageInterface):
    def __init__(self):
        self.bucket_name = os.getenv("GCP_STORAGE_BUCKET")
        if not self.bucket_name:
            raise RuntimeError("Define a variável de ambiente GCP_STORAGE_BUCKET.")
        
        self.client = storage.Client()
        self.bucket =self.client.bucket(self.bucket_name)
        
        self.docs_prefix = "documentos"
        self.thumbnail_prefix = "thumbnails"
        self.audio_cache_prefix = "generated-audio"
        
    def _get_file_blob_name(self, filename: str) -> str:
        if not filename or "/" in filename or "\\" in filename:
            raise ValueError("O nome do ficheiro não é válido.")
        
        prefix = (
            self.thumbnail_prefix if filename.startswith("thumb_") else self.docs_prefix
        )
        
        return f"{prefix}/{filename}"
        
    def _get_audio_blob_name(self, blob_name: str) -> str:
        if not blob_name or "/" in blob_name or "\\" in blob_name:
            raise ValueError("O nome do audio não é válido.")
        
        if ".." in blob_name.split("/"):
            raise ValueError("O caminho do áudio não é permitido.")
        
        return f"{self.audio_cache_prefix}/{blob_name}"
    
    def upload_files_to_storage(self, data: bytes, filename: str) -> str:
        blob_name = self._get_file_blob_name(filename)
        blob = self.bucket.blob(blob_name)
        
        mime_type, _ = mimetypes.guess_type(filename)
        blob.upload_from_string(data, content_type = mime_type or "application/octet-stream")
        return blob.public_url

    def download_files_from_storage(self, filename: str) -> bytes:
        blob_name = self._get_file_blob_name(filename)
        blob = self.bucket.blob(blob_name)
        return blob.download_as_bytes()

    def delete_file_from_storage(self, filename: str):
        blob_name = self._get_file_blob_name(filename)
        blob = self.bucket.blob(blob_name)
        
        try:
            blob.delete()
        except NotFound:
            pass
        
    def get_cached_audio(self, blob_name: str) -> bytes | None:
        full_blob_name = self._get_audio_blob_name(blob_name)
        blob = self.bucket.blob(full_blob_name)
        
        try:
            return blob.download_as_bytes()
        except NotFound:
            return None
        
    def save_cached_audio(self, blob_name: str, data: bytes) -> bytes:
        full_blob_name = self._get_audio_blob_name(blob_name)
        blob = self.bucket.blob(full_blob_name)
        
        blob.upload_from_string(data, content_type = "audio/mpeg")
        
    def delete_cached_audio(self, blob_name: str) -> None:
        full_blob_name = self._get_audio_blob_name(blob_name)
        blob = self.bucket.blob(full_blob_name)
        
        try:
            blob.delete()
        except NotFound:
            pass