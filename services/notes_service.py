import uuid
from fastapi import UploadFile, HTTPException
from repositories.notes_repository import NotesRepository
from storage import upload_files_to_storage, download_files_from_storage, delete_file_from_storage
from utils import generate_file_thumbnail, extract_text_from_pdf

class NotesService:
    
    def __init__(self, repo: NotesRepository):
        self.repo = repo
    
    def process_upload(self, title:str, discipline:str, file:UploadFile, author_email:str):
        
        file_bytes = file.file.read()
        new_id  = str(uuid.uuid4())
        safe_filename = f"{new_id}_{file.filename.replace(' ', '_')}"
        
        file_url = upload_files_to_storage(file_bytes, safe_filename)
        thumbnail_url = generate_file_thumbnail(file_bytes, safe_filename)
        
        note_metadata = {
            "id": new_id,
            "title": title,
            "discipline": discipline,
            "author": author_email,
            "file_url": file_url,
            "thumbnail_url": thumbnail_url
        }
        return self.repo.create(note_metadata)
    
    def read_note_content(self,note_id:str):
            note = self.repo.get_by_id(note_id)
            if not note:
                return None
            
            filename= note.file_url.split("/")[-1]
            file_bytes = download_files_from_storage(filename)
            
            return {
                "id": note.id,
                "title": note.title,
                "discipline": note.discipline,
                "author": note.author,
                "file_url": note.file_url,
                "thumbnail_url": note.thumbnail_url
            }
            
    def get_all_notes(self):
        return self.repo.get_all()
    
    def get_my_notes(self, author_email:str):
        return self.repo.get_by_author(author_email)
    
    def get_note_by_id(self, note_id:str):
        return self.repo.get_by_id(note_id)   
    
    def prepare_download(self, note_id:str):
        """ Vai buscar os bytes à cloud e limpa o nome original para o browser."""
        note = self.repo.get_by_id(note_id)
        if not note:
            return None
        
        filename= note.file_url.split("/")[-1]
        file_bytes = download_files_from_storage(filename)
        
        # Limpar o nome para enviar para o utilizador (remover o UUID)
        original_name  = filename.split("_", 1)[-1] if "_"in filename else filename # Remove o UUID do nome do ficheiro
        
        return {"bytes": file_bytes, "filename": original_name}
    
    def delete_note(self, note_id:str, current_user_email:str):
        """
        Apaga da BD e liberta espaço na Cloud. 
        Garante que apenas o dono do apontamento o consegue apagar.
        """
        note = self.repo.get_by_id(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Apontamento não encontrado")
        
        if note.author != current_user_email:
            raise HTTPException(status_code=403, detail="Não tem permissão para efetuar esta ação")
        
        # 1. Apagar os ficheiros da Cloud (Ficheiro e Miniatura)
        try:
            filename = note.file_url.split("/")[-1]
            delete_file_from_storage(filename)
            
            if note.thumbnail_url:
                thumb_filename = note.thumbnail_url.split("/")[-1]
                delete_file_from_storage(thumb_filename)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro: {e}")
        
        # 2. Apagar da Base de Dados através do repositório
        self.repo.delete(note_id)
        return True
    
    
    def get_all_with_filters(self, school:str=None, course:str=None, year:str=None, discipline:str=None):
        return self.repo.get_all_with_filters(school, course, year, discipline)