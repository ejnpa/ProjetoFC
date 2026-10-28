from datetime import datetime, timedelta, timezone

from models.generated_cache import GeneratedCache
from models.saved_artifact import SavedArtifact

def utc_now():
    return datetime.now(timezone.utc)

class GeneratedCacheRepository:
    def __init__(self, db, ttl_days: int):
        self.db = db
        self.ttl_days = ttl_days
        
    def get(self, cache_key: str):
        item = self.db.query(GeneratedCache).filter_by(cache_key=cache_key).first()
        if item is None:
            return None
        
        is_saved = (
            self.db.query(SavedArtifact.id)
            .filter_by(cache_key=cache_key)
            .first() 
            is not None
        )
        
        now = utc_now()
        if item.expires_at and item.expires_at <= now and not is_saved:
            return None

        item.last_use_at=now
        self.db.commit()
        return item
    
    def save(self, cache_key: str, **values):
        item = self.db.query(GeneratedCache).filter_by(cache_key=cache_key).first()
        
        if item is None:
            item = GeneratedCache(cache_key=cache_key, **values)
            self.db.add(item)
        else:
            for name, value in values.items():
                setattr(item, name, value)
            item.last_used_at = utc_now()
            item.expires_at = utc_now() + timedelta(days=self.ttl_days)
        
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def pin(self, user_id: int, cache_key: str):
        existing = self.db.query(SavedArtifact).filter_by(user_id=user_id, cache_key=cache_key).first()
        
        if not existing:
            self.db.add(SavedArtifact(user_id=user_id, cache_key=cache_key))
        
        item = self.db.query(GeneratedCache).filter_by(cache_key=cache_key).first()
        
        if item:
            item.expires_at=None
        
        self.db.commit()
    
    def unpin(self, user_id: int, cache_key: str):
        item = self.db.query(SavedArtifact).filter_by(user_id=user_id, cache_key=cache_key).first()
        
        if item:
            self.db.delete(item)
        
        still_saved = self.db.query(SavedArtifact.id).filter_by(cache_key=cache_key).first()
        
        cache_item = self.db.query(GeneratedCache).filter_by(cache_key=cache_key).first()
        
        if cache_item and not still_saved:
            cache_item.expires_at = utc_now() + timedelta(days=self.ttl_days)
            
        self.db.commit()
        
    def delete_expired(self, storage) -> int:
        """Apaga da base de dados e do storage os itens expirados não guardados."""
        now=utc_now()
        
        expired_items = (
            self.db.query(GeneratedCache)
            .filter(
                    GeneratedCache.expires_at.is_not(None), 
                    GeneratedCache.expires_at <= now,
            ).all()
        )
        
        deleted_count = 0
        
        for item in expired_items:
            is_saved = (
                self.db.query(SavedArtifact.id)
                .filter_by(cache_key = item.cache_key)
                .first()
                is not None
            )
            if is_saved:
                continue
            
            if item.kind == "audio" and item.blob_name:
                storage.delete_cached_audio(item.blob_name)
            self.db.delete(item)
            deleted_count += 1
            
        self.db.commit()
        return deleted_count    