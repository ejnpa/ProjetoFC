from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.users import Users
from security import get_current_user
from services.notes_service import NotesService
from services.generated_artifact_service import GeneratedArtifactService
from dependencies import get_notes_service, get_generated_artifact_service

router = APIRouter(prefix="/api/library", tags=['Library'])

class SavedArtifactRequest(BaseModel):
    note_id:str
    kind: Literal['summary', 'audio']
    variant: Literal["original", "adapted"] = "adapted"
    
    
@router.post("/save")
async def save_artifact(
    request: SavedArtifactRequest,
    current_user: Users = Depends(get_current_user),
    notes: NotesService = Depends(get_notes_service),
    artifacts: GeneratedArtifactService = Depends(get_generated_artifact_service)
):
    note_data = notes.read_note_content(request.note_id)
    if not note_data:
        raise HTTPException(status_code = 404, details = "Apontamento não encontrado")
    
    if request.kind == 'summary':
        result_text, cache_key = artifacts.get_or_crate_summary(request.note_id, note_data["content"])
    else:
        text_to_read = note_data["content"]
        if request.variant == "adapted":
            text_to_read, _ = artifact.get_or_create_summary(
                request.note_id,
                note_data["content"]
            )
            
        _, cache_key =  await artifact.get_or_create_audio(
            request.note_id, 
            request.variant, 
            text_to_read
        )
    artifacts.cache.pin(current_user.id, cache_key)
    return {"message": "Guardado na Biblioteca"}
