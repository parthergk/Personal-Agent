import datetime
import re
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
    user_id: int = None,
) -> str:
    """
    Creates a reminder and saves it using SQLAlchemy according to the Reminder model.
    Accepts message (or task), due_at (or remind_at ISO-8601 string), and timezone.
    due_at is converted and stored in UTC.
    user_id is the ID of the user to schedule the reminder for.
    """
    if not user_id:
        return "Error creating reminder: 'user_id' is required."

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
            user_id=user_id,
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


def update_reminder(
    message: str = None,
    due_at: str = None,
    timezone: str = "Asia/Kolkata",
    user_id: int = None,
) -> str:
    """
    Updates the due_at time for an existing reminder belonging to the user.
    Takes message (used to identify/match the existing reminder), due_at (the updated reminder ISO-8601 time string),
    timezone, and user_id.
    """
    if not user_id:
        return "Error updating reminder: 'user_id' is required."

    reminder_text = message
    if not reminder_text:
        return "Error updating reminder: 'message' is required."

    time_str = due_at
    if not time_str:
        return "Error updating reminder: 'due_at' is required."

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

        # Fetch candidate reminders for this user (prioritizing pending)
        pending_reminders = (
            db.query(Reminder)
            .filter(Reminder.user_id == user_id, Reminder.status == "pending")
            .order_by(Reminder.due_at.asc())
            .all()
        )

        candidates = pending_reminders
        print("Pending Reminders: ",candidates)
        if not candidates:
            # Fallback to all reminders for user if no pending reminders exist
            candidates = (
                db.query(Reminder)
                .filter(Reminder.user_id == user_id)
                .order_by(Reminder.created_at.desc())
                .all()
            )

        if not candidates:
            return "No reminders found for user to update."

        best_match = None
        print("Reminder Text: ",reminder_text)
        # Check if reminder_text is an explicit ID like '#3' or '3'
        id_match = re.match(r"^#?(\d+)$", reminder_text.strip())
        print("Id Match: ",id_match)
        if id_match:
            target_id = int(id_match.group(1))
            best_match = next((r for r in candidates if r.id == target_id), None)
            print("Best Match: ",best_match)
            if not best_match:
                best_match = db.query(Reminder).filter(Reminder.id == target_id, Reminder.user_id == user_id).first()

        if not best_match:
            # Score candidates based on text match
            stopwords = {"the", "a", "an", "to", "for", "of", "in", "on", "at", "my", "reminder", "time", "please", "tomorrow", "today"}
            print("\nStopwords: ",stopwords)
            clean_query = reminder_text.strip().lower()
            print("\nClean_query: ",clean_query)
            query_tokens = [w for w in re.findall(r"\w+", clean_query) if w not in stopwords]
            print("\nQuery Tokens: ",query_tokens)
            if not query_tokens:
                query_tokens = re.findall(r"\w+", clean_query)

            best_score = 0
            for rem in candidates:
                rem_text = rem.message.strip().lower()
                rem_tokens = [w for w in re.findall(r"\w+", rem_text) if w not in stopwords]
                if not rem_tokens:
                    rem_tokens = re.findall(r"\w+", rem_text)

                score = 0
                if rem_text == clean_query:
                    score = 100
                elif clean_query in rem_text or rem_text in clean_query:
                    score = 80
                else:
                    common = set(query_tokens) & set(rem_tokens)
                    if common:
                        score = 40 + len(common) * 10

                if score > best_score:
                    best_score = score
                    best_match = rem

            # If single candidate exists and no match score, default to the single candidate
            if best_match is None and len(candidates) == 1:
                best_match = candidates[0]

        if not best_match:
            return f"No matching reminder found for '{reminder_text}'."

        best_match.due_at = due_at_utc
        best_match.timezone = tz_name
        best_match.status = "pending"
        best_match.locked_until = None
        best_match.attempts = 0
        db.commit()
        db.refresh(best_match)

        return (
            f"Successfully updated reminder #{best_match.id}: '{best_match.message}' "
            f"rescheduled for {due_at_utc.isoformat()} UTC ({tz_name})."
        )
    except Exception as e:
        db.rollback()
        return f"Error updating reminder: {str(e)}"
    finally:
        db.close()
