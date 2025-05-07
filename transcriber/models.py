from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class Transcription(Base):
    __tablename__ = "transcriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, index=True)
    user_id = Column(Integer, index=True)
    text = Column(String)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))