from http.client import HTTPException

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from fastapi import Response
import uuid
import pypdfium2 as pdfium
import io

from database import get_db
from models import Notes, Users
from security import get_current_user
from storage import upload_files_to_storage
from repositories.notes_repository import NotesRepository
from services.notes_service import NotesService
from utils import load_structure


router = APIRouter(
    prefix="/api/notes",
    tags=["Notes"]
)
def get_notes_service(db:Session = Depends(get_db))->NotesService:
    repo = NotesRepository(db)
    return NotesService(repo)

@router.post("/upload")
def upload_file(
    title: str = Form(...),
    discipline: str = Form(...),
    file: UploadFile = File(...),
    service: NotesService = Depends(get_notes_service),
    current_user: Users = Depends(get_current_user)
):
    note = service.process_upload(title, discipline, file, current_user.email)
    return {"message": "Upload completo e miniatura gerada!", "note": note}


@router.get("/")
def list_notes(service: NotesService = Depends(get_notes_service)):
    return service.get_all_notes()

@router.get("/structure")
def get_structure():
    """Devolve a árvore de Escolas, Cursos e Disciplinas (JSON) para desenhar as Dropdowns."""
    return load_structure()


@router.get("/{note_id}/read")
def read_note(note_id:str, service: NotesService = Depends(get_notes_service)):
    note_data = service.read_note_content(note_id)
    if not note_data:
        raise HTTPException(status_code=404, detail="Não encontrado")
    return note_data

@router.get("/me")
def list_my_notes(service: NotesService = Depends(get_notes_service), current_user: Users = Depends(get_current_user)):
    """Devolve apenas os apontamentos de quem fez o login"""
    return service.get_my_notes(current_user.email)

@router.get("/{note_id}")
def get_note_details(note_id:str, service: NotesService = Depends(get_notes_service)):
    """Ver os detalhes e metadados de um apontamento."""
    note  = service.get_note_by_id(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Não encontrado")
    return note

@router.get("/{note_id}/download")
def download_note_file(note_id:str, service: NotesService = Depends(get_current_user)):
    """Vai buscar o ficheiro à Cloud e injeta-o na resposta como um anexo transferível."""
    data = service.prepare_download(note_id)
    if not data:
        raise HTTPException(status_code=404, detail="Ficheiro não encontrado")
    
    # O FastAPI Response devolve os bytes diretamente para o browser fazer download
    
    return Response(
        content=data["bytes"],
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={data['filename']}"}
    )        

@router.delete("/{note_id}")
def delete_note(note_id:str, service: NotesService = Depends(get_notes_service), current_user: Users = Depends(get_current_user)):
    """Apaga da BD e apaga os blobs da Cloud."""
    service.delete_note(note_id, current_user.email)
    return {"message": "Apontamento apagado com sucesso"}