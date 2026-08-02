from sqlalchemy.orm import Session
from models import Notes

class NotesRepository:
    
    def __init__(self, db:Session):
        self.db = db
        
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
    
    def get_by_author(self, author_email: str):
        return self.db.query(Notes).filter(Notes.author == author_email).all()
    
    def delete(self, notes:Notes):
        self.db.delete(notes)
        self.db.commit()
    
    def get_all_with_filters(self, school:str=None, course:str=None, year:str=None, discipline:str=None):
        """
        Pesquisa na Base de Dados aplicando apenas os filtros que o utilizador escolheu.
        A filtragem acontece ao nível do SQL para máxima performance.
        """   
        query = self.db.query(Notes)
        
        if school and school != "Todas":
            query = query.filter(Notes.school == school)
        if course and course != "Todos":
            query = query.filter(Notes.course == course)
        if year and year != "Todos":
            query = query.filter(Notes.year == year)
        if discipline and discipline != "Todas":
            query = query.filter(Notes.discipline == discipline)
        return query.all()
        