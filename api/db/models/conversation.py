from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text
from db.session import Base


class ConversationContext(Base):
    __tablename__ = "conversation_context"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String, nullable=False, index=True)
    role = Column(String(20), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
