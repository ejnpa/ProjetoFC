from fastapi import FastAPI
from database import engine, Base
from routers import auth, notes


Base.metadata.create_all(bind=engine)
        

app = FastAPI(
    title = "Notes API",
    description = "API Restful para formatação de textos com foco em PHDA",
    version = "1.0.0"
)

app.include_router(auth.router)
app.include_router(notes.router)


        
@app.get("/")
def root():
    return {"message": "Bem-vindo à API de Notas!"}
