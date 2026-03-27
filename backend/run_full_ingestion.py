#!/usr/bin/env python3
"""
Script to manually run full pricing ingestion for all providers (AWS, Azure, GCP).
"""
import asyncio
import sys
import logging
from app.database import get_async_session
from app.services.ingestion.runner import run_full_ingestion

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Run full pricing ingestion."""
    logger.info("🚀 Starting full pricing ingestion for all providers...")
    
    # Get database session
    async for db in get_async_session():
        try:
            await run_full_ingestion(db)
            logger.info("✅ Full pricing ingestion completed successfully!")
            break
        except Exception as e:
            logger.error(f"❌ Ingestion failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
