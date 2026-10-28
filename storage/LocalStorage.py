import mimetypes
import os 
from pathlib import Path
from .IStorage import StorageInterface

class LocalStorage(StorageInterface):
    def __init__(self):
        default_upload_dir = Path(__file__).resolve().parent.parent / "LOCAL_UPLOADS"
        
        self.upload_dir = Path(
            os.getenv("LOCAL_STORAGE_DIR", str(default_upload_dir))
        ).resolve()
        
        self.audio_cache_dir = self.upload_dir / ".generated-audio"
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.audio_cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _safe_path(self, directory: Path, filename: str) -> Path:
        """
        Evita que um nome de ficheiro com '..' aceda fora da pasta esperada.
        O contrato atual da interface recebe nomes de ficheiro, não caminhos.
        """
        if not filename or Path(filename).name != filename:
            raise ValueError("O nome do ficheiro não é válido.")
        
        target_path = (directory / filename).resolve()
        
        try:
            target_path.relative_to(directory.resolve())
        except ValueError as exc:
            raise ValueError("O caminho do ficheiro não é permitido.") from exc
        
        return target_path
                
    def upload_files_to_storage(self, data: bytes, filename: str) -> str:
        file_path = self._safe_path(self.upload_dir, filename)
        file_path.parent.mkdir(parents=True, exists_ok=True)
        file_path.write_bytes(data)
    
        return f"/local_storage/{filename}"
    
    def download_files_from_storage(self, filename: str) -> bytes:
        file_path = self._safe_path(self.upload_dir, filename)
        return file_path.read_bytes()
        
    def delete_file_from_storage(self, filename: str):
        file_path = self._safe_path(self.upload_dir, filename)
        if file_path.exists():
            file_path.unlink()
    
    def get_cached_audio(self, blob_name: str) -> bytes | None:
        audio_path = self._safe_path(self.audio_cache_dir, blob_name)
        
        if not audio_path.exists():
            return None
        
        return audio_path.read_bytes()
    
    def save_cached_audio(self, blob_name: str, data: bytes) -> None:
        audio_path = self._safe_path(self.audio_cache_dir, blob_name)
        audio_path.parent.mkdir(parents=True, exists_ok=True)
        audio_path.write_bytes(data)
    
    def delete_cached_audio(self, blob_name: str) -> None:
        audio_path = self._safe_path(self.audio_cache_dir, blob_name)
        
        if audio_path.exists():
            audio_path.unlink()