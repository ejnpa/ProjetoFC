
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Response
from sqlalchemy.orm import Session
from dependencies import get_notes_service
from security import get_current_user
from services.notes_service import NotesService
from services.ai_accessibility_service import AIAccessibilityService
from processors.pdf_generator import create_acessability_pdf
from core.config_loader import load_structure
from models import Users


router = APIRouter(prefix="/api/notes", tags=["Notes"])

@router.get("/structure")
def get_structure():
    """Devolve a árvore de Escolas, Cursos e Disciplinas (JSON) para desenhar as Dropdowns."""
    return load_structure()

@router.get("/")
def list_notes(
    school:str=None,
    course:str=None,
    year:str=None,
    subject:str=None,
    service: NotesService = Depends(get_notes_service)
):
    return service.get_filtered_notes(school, course, year, subject)

@router.post("/upload")
def upload_file(
    title: str = Form(...),
    school: str = Form(...),
    course: str = Form(...),
    year: str = Form(...),
    subject: str = Form(...),
    file: UploadFile = File(...),
    service: NotesService = Depends(get_notes_service),
    current_user: Users = Depends(get_current_user)
):
    service.process_upload(title, school, course, year, subject, file, current_user.email)
    return {"message": "Upload completo!"}


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
def download_note_file(note_id:str, service: NotesService = Depends(get_notes_service),
                       current_user: Users = Depends(get_current_user)):
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

@router.get("/{note_id}/adapt")
def adapt_note(note_id:str, service: NotesService = Depends(get_notes_service),current_user: Users = Depends(get_current_user)):
    """Extrai o texto do ficheiro e envia para a IA formatar."""
    note_data= service.read_note_content(note_id)
    
    if not note_data:
        raise HTTPException(status_code=404, detail="Apontamento não encontrado")
    
    ai_service = AIAccessibilityService()
    adapted_text = ai_service.adapt_text(note_data["content"])
    
    pdf_bytes = create_acessability_pdf(note_data["title"], adapted_text)
    
    return Response (content = pdf_bytes,
                     media_type = "application/pdf")



