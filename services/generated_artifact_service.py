import hashlib 
from datetime import datetime, timedelta, timezone
from repositories.generated_cache_repository import generatedCacheRepository 

class GeneratedArtifactService:
    PROMPT_VERSION = "prompt-v1" 
    AUDIO_VERSION = "mp3-v1"
    
    def __init__(self, storage, ai_service, audio_service, ttl_days):
        self.db = db
        self.storage = storage
        self.ai_service = ai_service
        self.audio_service = audio_service
        self.ttl_days = ttl_days
        
    @staticmethod
    def _hash(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()
    
    def get_or_create_summary(self, note_id: str, text: str):
        source_hash = self._hash(text)
        model = self.ai_service.model
        
        key_input = (f"summary|{note_id}|{source_hash}|{model}|{self.PROMPT_VERSION}")
        
        cache_key = self._hash(key_input)
        
        cached = self.cache.get(cache_key)
        if cached and cached.result_text:
            return cached.result_text, cache_key
        
        summary = self.ai_service.adapt_text(text)
        if not summary or summary.startswith("Erro:"):
            raise RuntimeError("A IA não conseguiu gerar o resumo.")
        
        now = datetime.now(timezone.utc)
        self.cache.save(
            cache_key,
            kind="summary",
            variant="adapted",
            source_hash = source_hash,
            result_text = summary,
            blob_name = blob_name,
            created_at = now,
            last_used_at = now, 
            expires_at = now + timedelta(days=self.ttl_days),
        )
        return summary, cache_key
    
    
    async def get_or_create_audio(self, note_id: str, variant: str, text: str):
        source_hash = self._hash(text)
        voice = self.audio_service.voice
        
        key_input = f"audio|{note_id}|{variant}|{source_hash}|{voice}|mp3-v1"
        cache_key = self._hash(key_input)
        blob_name = f"{cache_key}.mp3"
        
        cached = self.cache.get(cache_key)
        if cached:
            audio_bytes = self.storage.get_cached_audio(blob_name)
            if audio_bytes is not None:
                return audio_bytes, cache_key
            
        audio_bytes = await self.audio_service.synthesize(text)
        self.storage.save_cached_audio(blob_name, audio_bytes)
        
        now = datetime.now(timezone.utc)
        self.cache.save(
            cache_key, 
            note_id = note_id,
            kind = "audio",
            variant = variant,
            source_hash = source_hash,
            result_text = None,
            blob_name = None,
            created_at = now,
            last_used_at = now, 
            expires_at = now + timedelta(days=self.ttl_days),
        )
        return audio_bytes, cache_key
    

    
    
        