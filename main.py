from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import auth, notes
import models


models.Base.metadata.create_all(bind=engine)
        

app = FastAPI(
    title = "Notes API",
    description = "API Restful para formatação de textos com foco em PHDA",
    version = "1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ 
            "http://127.0.0.1:5500",
            "http://localhost:5500",
            "http://localhost:8000", 
            "http://127.0.0.1:8000",
            "http://100.89.13.43"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 


app.include_router(auth.router)
app.include_router(notes.router)


        
@app.get("/")
def root():
    return {"message": "Bem-vindo à API!",
            "docs": "Acede a http://127.0.0.1:8000/docs"}
