from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from database import Base

class SavedArtifact(Base):
    __tablename__="saved_atifact"
    
    id = Column(Integer, primary_key =True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False )
    cache_key = Column(String(64), ForeignKey("generated_cache.cache_key",ondelete="CASCADE"), nullable=False)
    saved_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    __table_args__=(UniqueConstraint("user_id", "cache_key"),)