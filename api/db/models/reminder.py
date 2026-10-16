from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from db.session import Base


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, nullable=False)
    due_at = Column(DateTime, nullable=False, index=True)
    timezone = Column(String, nullable=False, default="Asia/Kolkata")
    status = Column(String, default="pending", nullable=False, index=True)
    attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    sent_at = Column(DateTime, nullable=True)