from sqlalchemy import Column, String, Integer, DateTime, Text, Enum
import enum
from datetime import datetime
from app.db.session import Base

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SCORED_REVISING = "scored_revising"
    COMPLETED = "completed"
    FAILED = "failed"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    topic = Column(String, index=True)
    target_word_count = Column(Integer, default=1500)
    language = Column(String, default="English")
    status = Column(String, default=JobStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Store intermediate state for durability
    serp_data = Column(Text, nullable=True) # JSON serialized
    outline = Column(Text, nullable=True) # JSON serialized
    draft_content = Column(Text, nullable=True)
    
    # Store final result
    result = Column(Text, nullable=True) # JSON serialized ArticleOutput
    error_message = Column(Text, nullable=True)
