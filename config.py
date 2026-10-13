from  pydantic_settings import BaseSettings


class Settings(BaseSettings):
    
    storage_connection_string: str
    ollama_url: str = "http://100.89.13.43:11434"
    database_url: str = "sqlite:///./database.db"
    secret_key: str = "supersecretkey"
    
    
    class Config:
        env_file = ".env"
        extra = "ignore"
        
settings = Settings()
        