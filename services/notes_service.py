import uuid
from urllib.parse import unquote
from fastapi import UploadFile, HTTPException

from processors.text_extractor import extract_text_from_file
from processors.image_extractor import generate_pdf_thumbnail_bytes
from repositories.notes_repository import NotesRepository


class NotesService:
    
    def __init__(self, repo: NotesRepository, storage):
        self.repo = repo
        self.storage = storage
    
    def process_upload(self, title: str,
                       school: str,
                       course: str,
                       year: str,
                       subject: str,
                       file: UploadFile,
                       author_email: str):
        file_bytes = file.file.read()
        new_id = str(uuid.uuid4())
        safe_filename = f"{new_id}_{file.filename.replace(' ', '_')}"
        
        # Correção: Invocação através da estratégia (self.storage)
        file_url = self.storage.upload_files_to_storage(file_bytes, safe_filename)
        thumbnail_url = None
        thumb_bytes = generate_pdf_thumbnail_bytes(file_bytes, safe_filename)
        
        if thumb_bytes:
            thumb_filename = f"thumb_{safe_filename}.png"
            thumbnail_url = self.storage.upload_files_to_storage(thumb_bytes, thumb_filename)
        
        note_metadata = {
            "id": new_id,
            "title": title,
            "school": school,
            "course": course,
            "year":year,
            "subject": subject,
            "author": author_email,
            "file_url": file_url,
            "thumbnail_url": thumbnail_url
        }
        return self.repo.create(note_metadata)
    
    def read_note_content(self, note_id: str):
            note = self.repo.get_by_id(note_id)
            if not note:
                return None
                
            filename = unquote(note.file_url.split("/")[-1])
            try:
                file_bytes = self.storage.download_files_from_storage(filename)
            except Exception as e:
                print(f"Erro ao transferir ficheiro do storage: {e}")
                raise HTTPException(status_code=404, detail="O ficheiro físico já não existe no servidor.")
            
            return {
                "id": note.id,
                "title": note.title,
                "subject": note.subject,
                "author": note.author,
                "file_url": note.file_url,
                "thumbnail_url": note.thumbnail_url,
                "content": extract_text_from_file(file_bytes, filename)
            }
    
    
    
    def get_filtered_notes(self, school: str = None, course: str = None, year: str = None, subject: str = None):
        return self.repo.get_all_with_filters(school, course, year, subject)
            
    def get_all_notes(self):
        return self.repo.get_all()
    
    def get_my_notes(self, author_email: str):
        return self.repo.get_by_author(author_email)
    
    def get_note_by_id(self, note_id: str):
        return self.repo.get_by_id(note_id)   
    
    def prepare_download(self, note_id: str):
        note = self.repo.get_by_id(note_id)
        if not note:
            return None
        
        filename = unquote(note.file_url.split("/")[-1])
        file_bytes = self.storage.download_files_from_storage(filename)
        
        original_name = filename.split("_", 1)[-1] if "_" in filename else filename
        
        return {"bytes": file_bytes, "filename": original_name}
    
    def delete_note(self, note_id: str, current_user_email: str):
        note = self.repo.get_by_id(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Apontamento não encontrado")
        
        if note.author != current_user_email:
            raise HTTPException(status_code=403, detail="Não tem permissão para efetuar esta ação")
        
        try:
            filename = unquote(note.file_url.split("/")[-1])
            self.storage.delete_file_from_storage(filename)
            
            if note.thumbnail_url:
                thumb_filename = note.thumbnail_url.split("/")[-1]
                self.storage.delete_file_from_storage(thumb_filename)
        except Exception as e:
            print(f"Aviso ao apagar ficheiros físicos (podem já ter sido apagados): {e}")
        
        self.repo.delete(note_id)
        return True