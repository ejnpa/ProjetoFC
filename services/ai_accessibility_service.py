import os
import requests
import json

class AIAccessibilityService:
    def __init__(self, api_key):
        base_url = os.getenv("OLLAMA_BASE_URL", "http://100.89.13.43:11434")
        self.ollama_url = f"{base_url}/api/generate"
        self.model = "llama3"  # modelo a usar
        
        
        
                   