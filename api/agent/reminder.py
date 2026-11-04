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
    - Scenario A: Explicit ID in message (e.g. '#3', 'reminder 3', or '3' from clarification query)
    - Scenario B: Auto-selection if only 1 active reminder exists
    - Scenario C: Multiple reminders exist - keyword & token overlap scoring
    - Scenario D: Ambiguity detection if multiple reminders match equally well
    """
    if not user_id:
        return "Error updating reminder: 'user_id' is required."

    reminder_text = (message or "").strip()
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

        # 1. Fetch pending reminders for this user (SQL as single source of truth)
        pending_reminders = (
            db.query(Reminder)
            .filter(Reminder.user_id == user_id, Reminder.status == "pending")
            .order_by(Reminder.due_at.asc())
            .all()
        )

        candidates = pending_reminders
        if not candidates:
            # Fallback to all reminders for user if no pending reminders exist
            candidates = (
                db.query(Reminder)
                .filter(Reminder.user_id == user_id)
                .order_by(Reminder.created_at.desc())
                .all()
            )

        if not candidates:
            return "No reminders found for you to update."

        best_match = None

        # Scenario A: Explicit ID provided in message (e.g. '#3', 'reminder 3', or '3')
        id_match = re.search(r"#?(\b\d+\b)", reminder_text)
        if id_match:
            target_id = int(id_match.group(1))
            best_match = next((r for r in candidates if r.id == target_id), None)
            if not best_match:
                best_match = db.query(Reminder).filter(Reminder.id == target_id, Reminder.user_id == user_id).first()

        # Scenario B: User only has ONE reminder active (No ambiguity possible)
        if not best_match and len(candidates) == 1:
            best_match = candidates[0]

        # Scenario C: Multiple reminders exist - match by keywords & detect ambiguity
        if not best_match:
            stopwords = {"the", "a", "an", "to", "for", "of", "in", "on", "at", "my", "reminder", "time", "please", "tomorrow", "today"}
            clean_query = reminder_text.lower()
            query_tokens = [w for w in re.findall(r"\w+", clean_query) if w not in stopwords]
            if not query_tokens:
                query_tokens = re.findall(r"\w+", clean_query)

            scored_candidates = []
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

                if score > 0:
                    scored_candidates.append((rem, score))

            if not scored_candidates:
                active_list = "\n".join([f"- #{r.id}: '{r.message}'" for r in candidates[:5]])
                return (
                    f"No reminder matching '{reminder_text}' was found. "
                    f"Here are your current active reminders:\n{active_list}\n"
                    f"Please tell me which one you'd like to update."
                )

            # Sort by highest match score
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            top_score = scored_candidates[0][1]
            top_matches = [rem for rem, score in scored_candidates if score == top_score]

            # Scenario D: Ambiguity! Multiple reminders tied with the same top score
            if len(top_matches) > 1:
                options = "\n".join([f"- #{r.id}: '{r.message}'" for r in top_matches])
                return (
                    f"Multiple reminders match your request '{reminder_text}':\n{options}\n"
                    f"Please clarify which reminder you want to reschedule (you can mention the title or #ID)."
                )

            best_match = scored_candidates[0][0]

        # Update the target reminder
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
