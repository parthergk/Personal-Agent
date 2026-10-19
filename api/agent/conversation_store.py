import logging
from typing import List, Dict
from db.session import SessionLocal, Base, engine
from db.models.conversation import ConversationContext

logger = logging.getLogger(__name__)

# Ensure tables are created if not already present
Base.metadata.create_all(bind=engine)

MAX_CONTEXT_MESSAGES = 6  # Last 3 user + 3 assistant turns


def get_conversation_context(sender: str, max_messages: int = MAX_CONTEXT_MESSAGES) -> List[Dict[str, str]]:
    """
    Fetches the persistent, recent conversation context for a sender.
    Returns a list of dicts suitable for OpenAI messages: [{"role": ..., "content": ...}]
    Persists across restarts and does not expire on a short timer.
    """
    if not sender:
        return []

    db = SessionLocal()
    try:
        # Get the most recent `max_messages` rows for this sender in descending order
        rows = (
            db.query(ConversationContext)
            .filter(ConversationContext.sender == sender)
            .order_by(ConversationContext.id.desc())
            .limit(max_messages)
            .all()
        )

        # Reverse to get chronological order (oldest to newest)
        rows.reverse()

        return [{"role": r.role, "content": r.content} for r in rows]

    except Exception as e:
        logger.error("Failed to fetch conversation context for sender %s: %s", sender, e)
        return []
    finally:
        db.close()


def add_conversation_turn(
    sender: str,
    user_content: str,
    assistant_content: str,
    is_out_of_scope: bool = False,
    max_messages: int = MAX_CONTEXT_MESSAGES,
) -> None:
    """
    Persists a completed user-assistant conversation turn for the sender.
    Filters out off-topic / out-of-scope interactions (e.g. general trivia, coding).
    Maintains a bounded sliding window by removing older messages beyond `max_messages`.
    """
    if not sender or is_out_of_scope:
        return

    db = SessionLocal()
    try:
        # 1. Insert user message
        if user_content:
            db.add(ConversationContext(sender=sender, role="user", content=user_content))

        # 2. Insert assistant response
        if assistant_content:
            db.add(ConversationContext(sender=sender, role="assistant", content=assistant_content))

        db.commit()

        # 3. Trim older messages for this sender beyond `max_messages` to keep the database bounded
        older_ids = (
            db.query(ConversationContext.id)
            .filter(ConversationContext.sender == sender)
            .order_by(ConversationContext.id.desc())
            .offset(max_messages)
            .all()
        )

        if older_ids:
            ids_to_delete = [r[0] for r in older_ids]
            db.query(ConversationContext).filter(ConversationContext.id.in_(ids_to_delete)).delete(synchronize_session=False)
            db.commit()

    except Exception as e:
        db.rollback()
        logger.error("Failed to save conversation turn for sender %s: %s", sender, e)
    finally:
        db.close()


def clear_conversation_context(sender: str) -> None:
    """
    Explicitly deletes conversation context for a sender if ever needed.
    """
    if not sender:
        return

    db = SessionLocal()
    try:
        db.query(ConversationContext).filter(ConversationContext.sender == sender).delete(synchronize_session=False)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("Failed to clear conversation context for sender %s: %s", sender, e)
    finally:
        db.close()
