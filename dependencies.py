from repositories.notes_repository import NotesRepository
from services.notes_service import NotesService
from services.ai_accessibility_service import AIAccessibilityService
from storage import get_storage_provider
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from services.audio_service import AudioService

_ai_service_instance_ = AIAccessibilityService()

def get_ai_service():
    return _ai_service_instance_

def get_notes_repo(db: Session = Depends(get_db)):
    return NotesRepository(db)

def get_storage():
    return get_storage_provider()

def get_notes_service(
    repo: NotesRepository = Depends(get_notes_repo),
    storage = Depends(get_storage)
):
    return NotesService(repo= repo, storage=storage)

def get_audio_service() -> AudioService:
    return AudioService()
