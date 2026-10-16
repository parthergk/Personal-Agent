import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None

from db.session import SessionLocal, Base, engine
from db.models.reminder import Reminder

# Create tables if they do not exist
Base.metadata.create_all(bind=engine)

def create_reminder(
    message: str = None,
    due_at: str = None,
    timezone: str = "Asia/Kolkata",
) -> str:
    """
    Creates a reminder and saves it using SQLAlchemy according to the Reminder model.
    Accepts message (or task), due_at (or remind_at ISO-8601 string), and timezone.
    due_at is converted and stored in UTC.
    """
    reminder_text = message
    if not reminder_text:
        return "Error creating reminder: 'message' is required."

    time_str = due_at
    if not time_str:
        return "Error creating reminder: 'due_at' is required."

    tz_name = timezone or "Asia/Kolkata"

    db = SessionLocal()
    try:
        # Parse ISO-8601 string to a datetime object
        dt = datetime.datetime.fromisoformat(time_str)

        # If naive datetime, attach user's timezone before converting to UTC
        if dt.tzinfo is None and ZoneInfo is not None:
            try:
                dt = dt.replace(tzinfo=ZoneInfo(tz_name))
            except Exception:
                pass

        # Convert to UTC and store as naive datetime in UTC
        if dt.tzinfo is not None:
            dt = dt.astimezone(datetime.timezone.utc)
        due_at_utc = dt.replace(tzinfo=None)

        db_reminder = Reminder(
            message=reminder_text,
            due_at=due_at_utc,
            timezone=tz_name,
            status="pending",
            attempts=0,
        )
        db.add(db_reminder)
        db.commit()
        db.refresh(db_reminder)

        return f"Successfully created reminder #{db_reminder.id}: '{reminder_text}' scheduled for {due_at_utc.isoformat()} UTC ({tz_name})."
    except Exception as e:
        db.rollback()
        return f"Error creating reminder: {str(e)}"
    finally:
        db.close()
