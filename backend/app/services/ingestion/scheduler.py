import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.config import settings
from app.database import AsyncSessionLocal
from app.services.ingestion.runner import run_full_ingestion
from app.core.audit import log_audit

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def scheduled_ingestion_job():
    """Job function called by scheduler daily."""
    logger.info("Running scheduled pricing ingestion...")
    async with AsyncSessionLocal() as db:
        try:
            await run_full_ingestion(db)
            await log_audit(db, action="scheduled_ingestion", status="success")
        except Exception as e:
            logger.error(f"Scheduled ingestion failed: {e}")
            await log_audit(
                db,
                action="scheduled_ingestion",
                status="error",
                error_message=str(e)
            )


async def start_scheduler():
    """Start the APScheduler background scheduler."""
    scheduler.add_job(
        scheduled_ingestion_job,
        CronTrigger(
            day_of_week='sun',  # Sunday
            hour=0,  # 12:00 AM (midnight)
            minute=0
        ),
        id="weekly_pricing_ingestion",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    scheduler.start()
    logger.info(f"Pricing ingestion scheduler started. Runs weekly on Sunday at 00:00 UTC (12:00 AM).")


async def stop_scheduler():
    """Stop scheduler on app shutdown."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Pricing ingestion scheduler stopped.")
