import os
import requests
from config import settings
from core.messages import AImessages

class AIAccessibilityService:
    def __init__(self):
        base_url = settings.ollama_url
        
        base_url = base_url.replace("/api/generate", "")
        
        self.ollama_url = f"{base_url.rstrip('/')}/api/chat"
        self.model = "llama3"  # modelo a usar
        
    def adapt_text(self,text:str) -> str:
        
        if not text or len(text.strip()) < 10:
            return "Erro: O sistema não conseguiu extrair texto nenhum deste ficheiro."
            
        short_text = text[:4000] if len(text) > 4000 else text # Limita o texto a 4000 caracteres para evitar sobrecarga
        
        messages = [
            { 
                "role": "system",
                "content":  AImessages.SYSTEM_PROMPT
                        },
                        {
                            "role": "user",
                            "content" : "Aplica as regras dadas para adaptar e resumir o seguinte texto original:\n\n{short_text}"
                        }
                    ]    

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.3}
        }
        
        try:
            print(f"A enviar pedido para o Ollama em {self.ollama_url}...")
            response = requests.post(self.ollama_url, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            if "message" in data and "content" in data["message"]:
                return data["message"]["content"]
            return AImessages.ERROR_BAD_FORMAT
        except requests.exceptions.RequestException as e:
            print(f"Erro ao comunicar com o Ollama: {e}")
            return AImessages.ERROR_OLLAMA_DOWN
        
        
        
                   
