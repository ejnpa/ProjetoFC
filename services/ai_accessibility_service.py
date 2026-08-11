import os
import requests
import json

class AIAccessibilityService:
    def __init__(self, api_key):
        self.api_key = os.getenv("AI_ACCESSIBILITY_API_KEY", api_key)
        self.model = "gemini-3-flash-16k"  # modelo a usar
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent" # URL da API
        