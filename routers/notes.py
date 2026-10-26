
import os
from database import get_db
from core.config_loader import load_structure
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException,
    Response,
    Query,
    status)
from fastapi.responses import StreamingResponse
from models.note_like import NoteLike
from models.users import Users
from models.notes import Notes
from processors.pdf_generator import create_acessability_pdf
from security import get_current_user
from services.ai_accessibility_service import AIAccessibilityService
from services.audio_service import AudioService
from services.notes_service import NotesService
from dependencies import get_notes_service, get_ai_service, get_audio_service
from sqlalchemy.orm import Session

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

@router.get("/me")
def list_my_notes(service: NotesService = Depends(get_notes_service),
                  current_user: Users = Depends(get_current_user)):
    """Devolve apenas os apontamentos de quem fez o login"""
    return service.get_my_notes(current_user.email)

@router.get("/{note_id}")
def get_note_details(
    note_id:str, service: NotesService = Depends(get_notes_service)
    ):
    """Ver os detalhes e metadados de um apontamento."""
    note  = service.get_note_by_id(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Não encontrado")
    return note

@router.get("/{note_id}/read")
def read_note(
    note_id:str, 
    service: NotesService = Depends(get_notes_service), 
    current_user: Users = Depends(get_current_user)
):
    note_data = service.read_note_content(note_id)
    if not note_data:
        raise HTTPException(status_code=404, detail="Não encontrado")
    return note_data


@router.get("/{note_id}/download")
def download_note_file(
    note_id:str, 
    service: NotesService = Depends(get_notes_service),
    current_user: Users = Depends(get_current_user)
    ):
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
def delete_note(
    note_id:str, 
    service: NotesService = Depends(get_notes_service),
    current_user: Users = Depends(get_current_user)
    ):
    """Apaga da BD e apaga os blobs da Cloud."""
    service.delete_note(note_id, current_user.email)
    return {"message": "Apontamento apagado com sucesso"}

@router.get("/{note_id}/adapt")
def adapt_note(
    note_id:str, 
    service: NotesService = Depends(get_notes_service),
    current_user: Users = Depends(get_current_user),
    ai_service: AIAccessibilityService = Depends(get_ai_service)
    ):
    """Extrai o texto do ficheiro e envia para a IA formatar."""
    note_data= service.read_note_content(note_id)
    
    if not note_data:
        raise HTTPException(status_code=404, detail="Apontamento não encontrado")
    
    adapted_text = note_data.get("inclusive-summary")
    if not adapted_text:
        adapted_text = ai_service.adapt_text(note_data["content"])
        if hasattr(service, "save-inclusive-summary"):
            service.save_inclusive_summary(note_id, adapted_text)
    
    pdf_bytes = create_acessability_pdf(note_data["title"], adapted_text)
    
    return Response (content = pdf_bytes, media_type = "application/pdf")


@router.get("/{note_id}/audio")
async def get_note_audio(note_id:str, 
                         type:str = Query("original", regex= "^(original|adapted)$"),
                         service: NotesService = Depends(get_notes_service), 
                         ai_service: AIAccessibilityService = Depends(get_ai_service),
                         audio_service: AudioService = Depends(get_audio_service),
                         current_user: Users =  Depends(get_current_user)
):
    note_data = service.read_note_content(note_id)
    if not note_data or not note_data.get("content"):
        raise HTTPException(status_code = 404, detail = "Apontamento não encontrado")
    
    if type == 'adapted':
        text_to_read = note_data.get("inclusive_summary")
        if not text_to_read:
            text_to_read = ai_service.adapt_text(note_data["content"])
    else:
        text_to_read = note_data["content"]
            
    if not text_to_read.strip():
        raise HTTPException(
            satus_code=400, 
            detail= "Conteúdo indisponível para síntese de voz neste modo." 
        )
    return StreamingResponse(
        audio_service.stream_audio(note_data["content"]),
        media_type = "audio/mpeg"
    )


@router.post("/{note_id}/like")
def like_note(note_id: str, current_user: Users = Depends(get_current_user), db: Session = Depends(get_db)):
    
    note = db.query(Notes).filter(Notes.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail='Apontamento não encontrado')
    
    existing_like = db.query(NoteLike).filter(
        NoteLike.user_id == current_user.id,
        NoteLike.note_id == note_id                                        
    ).first()
    
   
    if not existing_like:
        new_like = NoteLike(user_id=current_user.id, note_id=note_id)
        db.add(new_like)
        db.commit() 
        
    return {"message": "Gosto adicionado!"}

@router.delete("/{note_id}/like")
def delete_like(note_id: str, current_user: Users = Depends(get_current_user), db: Session = Depends(get_db)):
    
    existing_like = db.query(NoteLike).filter(
        NoteLike.user_id == current_user.id,
        NoteLike.note_id == note_id                                        
    ).first()
    
    if existing_like:
        db.delete(existing_like)
        db.commit()
        
    return {"message": "Gosto removido!"}

