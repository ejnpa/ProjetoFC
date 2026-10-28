from repositories.notes_repository import NotesRepository
from services.notes_service import NotesService
from services.ai_accessibility_service import AIAccessibilityService
from storage import get_storage_provider
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from services.audio_service import AudioService
from config import settings
from services.generated_artifact_service import GeneratedArtifactService


_ai_service_instance_ = AIAccessibilityService()

def get_ai_service():
    return _ai_service_instance_

def _get_notes_repo(db: Session = Depends(get_db)):
    return NotesRepository(db)

def _get_storage():
    return get_storage_provider()

def get_notes_service(
    repo: NotesRepository = Depends(_get_notes_repo),
    storage = Depends(_get_storage)
):
    return NotesService(repo= repo, storage=storage)

def get_audio_service() -> AudioService:
    return AudioService()

def get_generated_artifact_service(
    db: Session = Depends(get_db),
    storage = Depends(_get_storage),
    ai_service: AIAccessibilityService = Depends(get_ai_service),
    audio_service: AudioService = Depends(get_audio_service)
) -> GeneratedArtifactService:
    return GeneratedArtifactService(
        db=db,
        storage = storage,
        ai_service=ai_service,
        audio_service=audio_service,
        ttl_days=settings.generated_cache_ttl_days 
    )