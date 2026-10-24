"""
send_reminder.py
----------------
Delivers a due reminder to the bot owner via the Meta WhatsApp Cloud API.

The APScheduler BackgroundScheduler fires process_due_reminders() in a
background thread — there is no running event loop in that thread.
We therefore use asyncio.run() to create a fresh event loop per delivery,
which correctly drives the async send_whatsapp_message() call without
interfering with the FastAPI event loop running in the main thread.
"""

import os
import asyncio
import logging
from dotenv import load_dotenv

from db.models.reminder import Reminder
from .whatsapp import send_whatsapp_message

load_dotenv()

logger = logging.getLogger(__name__)

# The personal number that receives all reminder notifications.
# Format: international digits only, e.g. 919876543210 (no +, no spaces).
RECIPIENT_PHONE = os.getenv("RECIPIENT_PHONE_NUMBER")


def send_reminder_via_whatsapp(reminder: Reminder) -> None:
    """
    Synchronous delivery handler — called from the APScheduler background thread.

    Formats the reminder as a WhatsApp text message and sends it to the
    recipient stored on the reminder row (set at creation time from the
    webhook sender number). Falls back to RECIPIENT_PHONE env var for
    reminders created before this field was added.

    Raises an exception on failure so that reminder_scheduler.py can
    mark the reminder as failed and retry on the next poll cycle.
    """
    to_phone = getattr(reminder, "recipient_phone", None) or RECIPIENT_PHONE

    if not to_phone:
        raise RuntimeError(
            "No recipient phone number available for reminder "
            f"#{reminder.id}. Set RECIPIENT_PHONE_NUMBER in .env as fallback."
        )

    # Build a user-friendly message body
    body = (
        f"⏰ Reminder\n\n"
        f"{reminder.message}"
    )

    logger.info(
        "Sending reminder #%s to %s via WhatsApp: %s",
        reminder.id,
        to_phone,
        reminder.message,
    )

    # Bridge sync → async: safe to use asyncio.run() here because
    # APScheduler BackgroundScheduler runs jobs in a plain thread with
    # no event loop attached — asyncio.run() creates and closes one cleanly.
    asyncio.run(
        send_whatsapp_message(
            to=to_phone,
            message=body,
            type="text",
        )
    )

    logger.info("Reminder #%s delivered successfully via WhatsApp.", reminder.id)

