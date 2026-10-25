from sqlalchemy.orm import Session
from models.notes import Notes

class NotesRepository:
    
    def __init__(self, db:Session):
        self.db = db
 
    def _format_notes(self, notes_bd, current_user_id):
        res = []
        for note in notes_bd:
            note_dict = {col.name: getattr(note, col.name) for col in note.__table__.columns}
            
            note_dict["likes"] = len(note.like_list)
            note_dict["liked_by_user"] = any(like.user_id == current_user_id for like in note.like_list)

            res.append(note_dict)
        return res   
            
    def create(self, note_data: dict) -> Notes:
        new_note = Notes(**note_data)
        self.db.add(new_note)
        self.db.commit()
        self.db.refresh(new_note)
        return new_note
    
    def get_all(self):
        return self.db.query(Notes).all()
    
    def get_by_id(self, note_id: int) -> Notes:
        return self.db.query(Notes).filter(Notes.id == note_id).first()
    
    def get_by_author(self, author_email: str, current_user_id: int = None):
        notes_bd = self.db.query(Notes).filter(Notes.author == author_email).all()
        return self._format_notes(notes_bd, current_user_id)
    
    def delete(self, note_id:str):
        note_to_delete = self.db.query(Notes).filter(Notes.id == note_id).first()
        if note_to_delete:
            self.db.delete(note_to_delete)
            self.db.commit()
            
    def get_all_with_filters(self, school:str=None, course:str=None, year:str=None, subject:str=None,
                             current_user_id:int = None):
         
        query = self.db.query(Notes)
        
        if school and school != "Todas":
            query = query.filter(Notes.school == school)
        if course and course != "Todos":
            query = query.filter(Notes.course == course)
        if year and year != "Todos":
            query = query.filter(Notes.year == year)
        if subject and subject != "Todas":
            query = query.filter(Notes.subject == subject)
        return self._format_notes(query.all(), current_user_id)
        
