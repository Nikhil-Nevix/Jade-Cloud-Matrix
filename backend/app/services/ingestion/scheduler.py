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
            hour=settings.INGESTION_HOUR,
            minute=settings.INGESTION_MINUTE
        ),
        id="daily_pricing_ingestion",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    scheduler.start()
    logger.info(f"Pricing ingestion scheduler started. Runs daily at {settings.INGESTION_HOUR:02d}:{settings.INGESTION_MINUTE:02d} UTC.")


async def stop_scheduler():
    """Stop scheduler on app shutdown."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Pricing ingestion scheduler stopped.")
