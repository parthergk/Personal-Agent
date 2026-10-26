import os
import sys
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Callable
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import or_, and_
from sqlalchemy.orm import joinedload

# Ensure parent directory is in sys.path for direct script execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db.session import SessionLocal
from db.models.reminder import Reminder
from .send_reminder import send_reminder_via_whatsapp

logger = logging.getLogger("reminder_scheduler")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [ReminderScheduler]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Configuration constants
LOCK_TIMEOUT_SECONDS = 60
MAX_DELIVERY_ATTEMPTS = 3
DEFAULT_POLL_INTERVAL_SECONDS = 5

_scheduler: Optional[BackgroundScheduler] = None

# Register the WhatsApp delivery handler as the default.
# Can be overridden at runtime via set_delivery_handler().
_delivery_handler: Optional[Callable[[Reminder], None]] = send_reminder_via_whatsapp


def set_delivery_handler(handler: Callable[[Reminder], None]):
    """
    Register a custom callback handler for sending reminders
    (e.g., sending via WhatsApp or a push notification service).
    """
    global _delivery_handler
    _delivery_handler = handler


def deliver_reminder(reminder: Reminder):
    """
    Default delivery action for a reminder. Calls custom handler if registered,
    otherwise logs the triggered reminder.
    """
    if _delivery_handler:
        _delivery_handler(reminder)
    else:
        logger.info(
            f"🔔 REMINDER TRIGGERED | ID: #{reminder.id} | "
            f"Message: '{reminder.message}' | Timezone: {reminder.timezone} | "
            f"Scheduled (UTC): {reminder.due_at}"
        )


def process_due_reminders():
    """
    Fetches due reminders from the database, locks them, executes delivery,
    and updates their status to 'sent' or 'failed'.
    """
    db = SessionLocal()
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)

    try:
        # Fetch reminders that are due and eligible for processing
        # Eligible: status='pending' OR status='processing' with an expired lock (crash recovery)
        due_reminders = (
            db.query(Reminder)
            .options(joinedload(Reminder.user))
            .filter(
                Reminder.due_at <= now_utc,
                Reminder.attempts < MAX_DELIVERY_ATTEMPTS,
                or_(
                    Reminder.status == "pending",
                    and_(
                        Reminder.status == "processing",
                        Reminder.locked_until.isnot(None),
                        Reminder.locked_until < now_utc,
                    ),
                ),
            )
            .order_by(Reminder.due_at.asc())
            .limit(50)
            .all()
        )

        if not due_reminders:
            return

        logger.info(f"Found {len(due_reminders)} due reminder(s) to process.")

        for reminder in due_reminders:
            # 1. Claim & lock the reminder
            reminder.status = "processing"
            reminder.attempts = (reminder.attempts or 0) + 1
            reminder.locked_until = now_utc + timedelta(seconds=LOCK_TIMEOUT_SECONDS)
            db.commit()

            # 2. Attempt delivery
            try:
                deliver_reminder(reminder)

                # 3. Mark as sent upon successful delivery
                reminder.status = "sent"
                reminder.sent_at = datetime.now(timezone.utc).replace(tzinfo=None)
                reminder.locked_until = None
                db.commit()
                logger.info(f"Reminder #{reminder.id} successfully marked as sent.")
            except Exception as delivery_err:
                db.rollback()
                logger.error(
                    f"Delivery failed for reminder #{reminder.id} (Attempt {reminder.attempts}/{MAX_DELIVERY_ATTEMPTS}): {delivery_err}"
                )
                if reminder.attempts >= MAX_DELIVERY_ATTEMPTS:
                    reminder.status = "failed"
                else:
                    reminder.status = "pending"
                reminder.locked_until = None
                db.commit()

    except Exception as e:
        db.rollback()
        logger.error(f"Error checking due reminders: {e}")
    finally:
        db.close()


def start_scheduler(interval_seconds: int = DEFAULT_POLL_INTERVAL_SECONDS) -> BackgroundScheduler:
    """
    Starts the APScheduler BackgroundScheduler to poll and process reminders every `interval_seconds`.
    """
    global _scheduler
    if _scheduler and _scheduler.running:
        logger.info("Reminder scheduler is already running.")
        return _scheduler

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        func=process_due_reminders,
        trigger="interval",
        seconds=interval_seconds,
        id="fetch_due_reminders",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    _scheduler.start()
    logger.info(f"Reminder scheduler started. Polling every {interval_seconds} seconds.")
    return _scheduler


def stop_scheduler():
    """
    Stops the background scheduler cleanly.
    """
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Reminder scheduler stopped.")
        _scheduler = None


def run_standalone(interval_seconds: int = DEFAULT_POLL_INTERVAL_SECONDS):
    """
    Runs the scheduler as a blocking, standalone process.
    """
    scheduler = BlockingScheduler()
    scheduler.add_job(
        func=process_due_reminders,
        trigger="interval",
        seconds=interval_seconds,
        id="fetch_due_reminders",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    logger.info(f"Starting standalone reminder scheduler service (interval: {interval_seconds}s)...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down standalone scheduler...")


if __name__ == "__main__":
    run_standalone()
