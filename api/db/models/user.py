from sqlalchemy import Column, String, Integer, Boolean, DateTime
from db.session import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    conversations = relationship("ConversationContext", back_populates="user")
    reminders = relationship("Reminder", back_populates="user")
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)
    timezone = Column(String, nullable=False, default='Asia/Kolkata')
    is_active = Column(Boolean,nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)