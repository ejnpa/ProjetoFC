import os
from dotenv import load_dotenv

load_dotenv()  # Carrega as variáveis de ambiente do ficheiro .env

from database import sessionLocal, engine, Base
from models import Users
from security import get_password_hash


def criar_utilizadores_teste():
    db_url=os.getenv("DATABASE_URL")
    print(f"A usar a base de dados: {db_url}")
    
    
    Base.metadata.create_all(bind=engine)
    
    db=sessionLocal()
     
    try:
        print("A limpar utilizadores antigos e a criar 10 novos...")
        db.query(Users).delete()
        
        for i in range(1, 11):
            novo_utilizador = Users(
                username=f"Estudante{i}",
                email=f"aluno{i}@ipcb.pt",
                password=get_password_hash("senha123")
            )
            db.add(novo_utilizador)
        db.commit()    
        print("✅ 10 utilizadores criados com sucesso na Nuvem (PostgreSQL)!")   
            
    except Exception as e:
        print(f"❌ Erro ao popular base de dados: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    criar_utilizadores_teste()        