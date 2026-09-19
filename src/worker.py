import time
import traceback
from datetime import datetime, timezone
from .database import SessionLocal
from . import models

def process_outbox_events():
    db = SessionLocal()
    try:
        # Fetch up to 50 pending events, locking them for update to prevent concurrent worker clashes
        pending_events = db.query(models.OutboxEvent).with_for_update(skip_locked=True).filter(
            models.OutboxEvent.status == "pending"
        ).order_by(models.OutboxEvent.created_at).limit(50).all()

        if not pending_events:
            return

        for event in pending_events:
            event.status = "processing"
        db.commit()

        for event in pending_events:
            try:
                if event.event_type == "label_published":
                    # Placeholder for the actual search re-indexing logic
                    label_id = event.payload.get("label_version_id")
                    print(f"Re-indexing search for published label: {label_id}")
                    # e.g., trigger pg_trgm materialized view refresh or external search sync

                event.status = "completed"
                event.processed_at = datetime.now(timezone.utc)

            except Exception as e:
                event.status = "failed"
                event.error_message = str(e) + "\n" + traceback.format_exc()
                event.processed_at = datetime.now(timezone.utc)

        db.commit()

    except Exception as e:
        print(f"Worker iteration failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting Gud Fud background worker...")
    while True:
        process_outbox_events()
        time.sleep(5)  # Poll interval
